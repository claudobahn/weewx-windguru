WeeWX WindGuru - WeeWX extension that publishes data to WindGuru
=
Based in large part on the WindFinder extension written by Matthew Wall.

## Installation
1. Run the extension installer:

   > setup.py install --extension weewx-windfinder.tgz

2. Update weewx.conf:

    ```
    [StdRESTful]
        [[WindGuru]]
            station_id = WINDFINDER_STATION_ID
            password = WINDFINDER_PASSWORD
    ```

3. Restart WeeWX

    > sudo /etc/init.d/weewx stop

    > sudo /etc/init.d/weewx start

For configuration options and details, see the comments in windguru.py
