# Installer for WindGuru WeeWX extension

from weecfg.extension import ExtensionInstaller


def loader():
    return WindGuruInstaller()


class WindGuruInstaller(ExtensionInstaller):
    def __init__(self):
        super(WindGuruInstaller, self).__init__(
            version="0.2",
            name='windguru',
            description='Upload weather data to WindGuru.',
            restful_services='user.windguru.WindGuru',
            config={
                'StdRESTful': {
                    'WindGuru': {
                        'station_id': 'replace_me',
                        'password': 'replace_me'}}},
            files=[('bin/user', ['bin/user/windguru.py'])]
        )
