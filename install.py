# Installer for WindGuru WeeWX extension

from setup import ExtensionInstaller


def loader():
    return WindGuruInstaller()


class WindGuruInstaller(ExtensionInstaller):
    def __init__(self):
        super(WindGuruInstaller, self).__init__(
                version="0.1",
                name='windguru',
                description='Upload weather data to WindGuru.',
                restful_services='user.windguru.WindGuru',
                config={
                    'StdRESTful': {
                        'WindGuru': {
                            'station_id': 'INSERT_WINDGURU_STATION_ID',
                            'password': 'INSERT_WINDGURU_PASSWORD'}}},
                files=[('bin/user', ['bin/user/windguru.py'])]
        )
