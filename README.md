# Price calc

Home assistant custom component for calculating price of running a electric appliance with non-linear energy usage.

For getting the electricity prices the awesome [Energi Data Service](https://github.com/MTrab/energidataservice) custom component from [@MTrab](https://github.com/MTrab) is required.

Simulates the price using a rolling window:
![price_calc_principle]  ![price_calc_principle](https://github.com/fars-fede-fire/price_calc/assets/87006332/5f7d30f9-60b9-46bc-a17e-79a85d1ab346)

Blue: electricity price  
Black: energy usage  
Red: calculated price for running appliance  

THIS IS ONLY TESTED USING A SHELLY PLUG S

Creates a single sensor with current price and following attributes:

### Entities with home charger
Attribute | Description
-- | -- 
`current_time` | Datetime matching the price_now sensor.
`next_lowest` |  Datetime of the lowest calculated price with available energy prices that has not yet parsed.
`next_lowest price` | Lowest calculated price with available energy prices that has not yet parsed.
`diff_now_and_next_lowest` | Difference in calculated price now compared to the next cheapest calculated price.
`delay_hours` | Delay in whole hours to cheapest start hourly from now. Be aware that this is not necessarily the absolute cheapest time.
`delay_hours_price` | Calculated price when delaying for `delay_hours`.
`diff_now_and_delay` | Calculated price difference when starting appliance now versus delaying for `delay_hours`.
`todays_highest` | The highest calculated price with available energy prices.
`today_highest_time` | Datetime of the highest calculated price with available energy prices.
`todays_lowest` | The lowest calculated price with available energy prices.
`today_lowest_time` | Datetime of the lowest calculated price with available energy prices.
`price_data` | All calculated prices and datetimes with available data. This is optional to add during setup. Be aware that this attribute can contain a lot of data!


### Data
#### History
For best results a consistent energy usage of electric appliance is needed. I have tested it using af Shelly Plug S. When using default Shelly integration data was updated with inconsistency, ranging from update interval from 45-75 seconds.  
When adding a REST sensor like this:
```yaml
rest:
  resource: http://192.168.1.83/meter/0
  scan_interval: 1
  sensor:
    - name: "shelly_rest_energy"
      unique_id: "shelly_rest_energy"
      unit_of_measurement: "kWh"
      value_template: "{{ value_json.total / 60000 }}"
```
Update interval variance was less than 1 second.
Make sure to delete this sensor after creating the price calc sensor to reduce network traffic.

#### File
If you already have downloaded a config file or added to the `custom_components/price_calc/data` you can select this file during setup.
Be aware that you need to restart Home Assistant if file is added while Home Assistant is running.

#### URL
You can share and download config files from [https://github.com/fars-fede-fire/price_calc_data](https://github.com/fars-fede-fire/price_calc_data)
1. Find the file you want to use in the repo and open it.
2. Click 'Raw' in the upper right corner.
3. Copy the URL and insert during setup when prompted.



