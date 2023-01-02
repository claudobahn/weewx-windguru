# Based on WindFinder plugin, portions copyright 2014 Matthew Wall

"""
This is a WeeWX extension that uploads data to WindGuru.

http://www.windguru.cz/

Station must be registered first by visiting:

https://stations.windguru.cz/register.php

The preferred upload frequency (post_interval) is one record every 5 minutes.

Minimal Configuration:

[StdRESTful]
    [[WindGuru]]
        station_id = WINDGURU_STATION_ID
        password = WINDGURU_PASSWORD

WindGuru does not have a published public API, please contact them if you want
to add support, they were very responsive.

Data is uploaded using a GET request:
http://www.windguru.cz/upload/api.php?stationtype=weewx&uid=station_id&interval=60&precip_interval=60&wind_avg=windSpeed&wind_max=windGust&wind_direction=windDir&temperature=outTemp&rh=outHumidity&mslp=barometer&precip=rain

Parameters explained:
interval: seconds, archive interval over which wind information is averaged
precip_interval: seconds, archive interval over which precipitation is accumulated in a sum
wind_avg: knots, average wind speed during interval
wind_max: knots, max wind speed during interval
wind_min: knots, min wind speed during interval
wind_direction: degrees, average wind direction during interval
temperature: celsius
rh: percent
mslp: hPa, mean sea level pressure
precip: mm
"""

try:
    # Python 3
    import queue
except ImportError:
    # Python 2
    import Queue as queue
try:
    # Python 3
    from urllib.parse import urlencode
except ImportError:
    # Python 2
    from urllib import urlencode
import re
import sys
import hashlib

import weewx
import weewx.restx
import weewx.units

VERSION = "0.3"

if weewx.__version__ < "3":
    raise weewx.UnsupportedFeature("weewx 3 is required, found %s" %
                                   weewx.__version__)


try:
    # Test for new-style weewx logging by trying to import weeutil.logger
    import weeutil.logger
    import logging
    log = logging.getLogger(__name__)

    def logdbg(msg):
        log.debug(msg)

    def loginf(msg):
        log.info(msg)

    def logerr(msg):
        log.error(msg)

except ImportError:
    # Old-style weewx logging
    import syslog

    def logmsg(level, msg):
        syslog.syslog(level, 'WindGuru: %s' % msg)

    def logdbg(msg):
        logmsg(syslog.LOG_DEBUG, msg)

    def loginf(msg):
        logmsg(syslog.LOG_INFO, msg)

    def logerr(msg):
        logmsg(syslog.LOG_ERR, msg)

def _mps_to_knot(v):
    from_t = (v, 'meter_per_second', 'group_speed')
    return weewx.units.convert(from_t, 'knot')[0]


class WindGuru(weewx.restx.StdRESTbase):
    def __init__(self, engine, config_dict):
        """This service recognizes standard restful options plus the following:

        station_id: WindGuru station identifier

        password: WindGuru password
        """
        super(WindGuru, self).__init__(engine, config_dict)
        loginf("service version is %s" % VERSION)
        site_dict = weewx.restx.get_site_dict(config_dict, 'WindGuru', 'station_id', 'password')
        if site_dict is None:
            return

        try:
            site_dict['manager_dict'] = weewx.manager.get_manager_dict_from_config(config_dict, 'wx_binding')
        except weewx.UnknownBinding:
            pass

        self.archive_queue = queue.Queue()
        self.archive_thread = WindGuruThread(self.archive_queue, **site_dict)
        self.archive_thread.start()
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)
        loginf("Data will be uploaded for %s" % site_dict['station_id'])

    def new_archive_record(self, event):
        self.archive_queue.put(event.record)




class WindGuruThread(weewx.restx.RESTThread):
    _SERVER_URL = 'http://www.windguru.cz/upload/api.php'
    _DATA_MAP = {'temperature': ('outTemp', '%.1f'),  # C
                 'wind_direction': ('windDir', '%.0f'),  # degree
                 'wind_avg': ('windSpeed', '%.1f'),  # knots
                 'wind_max': ('windGust', '%.1f'),  # knots
                 'rh': ('outHumidity', '%.1f'),  # %
                 'mslp': ('barometer', '%.3f'),  # hPa
                 'precip': ('hourRain', '%.2f'),  # mm
                 }

    def __init__(self, queue, station_id, password, manager_dict,
                 server_url=_SERVER_URL, skip_upload=False,
                 post_interval=60, max_backlog=sys.maxsize, stale=None,
                 log_success=True, log_failure=True,
                 timeout=60, max_tries=3, retry_wait=5):
        super(WindGuruThread, self).__init__(queue,
                                             protocol_name='WindGuru',
                                             manager_dict=manager_dict,
                                             post_interval=post_interval,
                                             max_backlog=max_backlog,
                                             stale=stale,
                                             log_success=log_success,
                                             log_failure=log_failure,
                                             timeout=timeout,
                                             max_tries=max_tries,
                                             retry_wait=retry_wait,
                                             skip_upload=skip_upload)
        self.station_id = station_id
        self.password = password
        self.server_url = server_url

    def check_response(self, response):
        lines = []
        for line in response:
            lines.append(line)
        msg = b''.join(lines)
        if not msg.decode('utf-8').startswith('OK'):
            raise weewx.restx.FailedPost("Server response: %s" % msg)

    def format_url(self, in_record):
        # put everything into the right units and scaling
        record = weewx.units.to_METRICWX(in_record)

        # authentication
        salt = "%d~salted" % record['dateTime']
        hash = hashlib.md5((salt + self.station_id + self.password).encode('utf-8')).hexdigest()

        if 'windSpeed' in record and record['windSpeed'] is not None:
            record['windSpeed'] = _mps_to_knot(record['windSpeed'])
        if 'windGust' in record and record['windGust'] is not None:
            record['windGust'] = _mps_to_knot(record['windGust'])

        values = {
            'stationtype': 'weewx',
            'uid': self.station_id,
            'salt': salt,
            'hash': hash,
            'interval': self.post_interval,
            'percip_interval': 3600 # hourly, because we pass hourRain as percipation value
        }

        for key in self._DATA_MAP:
            rkey = self._DATA_MAP[key][0]
            if rkey in record and record[rkey] is not None:
                values[key] = self._DATA_MAP[key][1] % record[rkey]

        url = self.server_url + '?' + urlencode(values)

        if weewx.debug >= 2:
            logdbg('url: %s' % url)

        return url
