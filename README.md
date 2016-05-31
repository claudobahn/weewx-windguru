WeeWX WindGuru - WeeWX extension that publishes data to WindGuru
=
Based in large part on the [WindFinder extension](https://github.com/weewx/weewx/wiki/windfinder) written by Matthew Wall.

## Installation
1. Download the extension
    > wget wget -O weewx-windguru.zip https://github.com/claudobahn/weewx-windguru/archive/master.zip

2. Run the extension installer:

   > wee_extension --install weewx-windguru.zip

2. Update weewx.conf:

    ```
    [StdRESTful]
        [[WindGuru]]
            station_id = WindGuru_Station_id
            password = WindGuru_Password
    ```

3. Restart WeeWX

    > sudo /etc/init.d/weewx stop

    > sudo /etc/init.d/weewx start
