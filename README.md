WeeWX WindGuru - WeeWX extension that publishes data to WindGuru
=
Based in large part on the [WindFinder extension](https://github.com/weewx/weewx/wiki/windfinder) written by Matthew Wall.

## Installation
1. Register your [WindGuru station](https://stations.windguru.cz/register.php)

2. Download the extension

    ```bash
    wget -O weewx-windguru.zip https://github.com/claudobahn/weewx-windguru/archive/master.zip
    ```

3. Run the extension installer:

    ```bash
    wee_extension --install weewx-windguru.zip
    ```

4. Update weewx.conf:

    The station_id is also called UID and Weewx ID in windguru, it's a bit confusing.

    ```
    [StdRESTful]
        [[WindGuru]]
            station_id = WindGuru_Station_UID
            password = WindGuru_Password
            post_interval = 60
    ```



5. Restart WeeWX

    > sudo /etc/init.d/weewx stop

    > sudo /etc/init.d/weewx start
