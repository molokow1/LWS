# LWS: A discrete event LoRaWAN WUSN Simulator

_Currently in the process of refactoring (again) the old prototype code presented in the paper to a more maintainable and extensible core component of a web simulation app which will be based on Django and React._

## TODOs:

1. Modify the core transmit logic to a more maintainable and readable form in classes with simpy.env and simpy.Store (check simpy tutorial)
2. Model the behaviours of LWSDevices with FSM
3. Use Chart.js to produce graphs for simulation results
4. React frontend requests backend restful apis via axios

## API design 

*Should be able to develop frontend concurrently with mock apis*

Sim result API JSON response should be something like this:

```json
{
  "overall_result" : {
    "der" : "0.5",
    "energy_comsumption" : "100",
    "total_packets_sent" : "1000",
    "total_packets_received" : "2000",
    "total_packets_lost" : "0",
    "total_packets_collided" : "0",
  },
  "basestation" : {
    "basestation1_id" : {
      "x" : "30",
      "y" : "40",
    }
  },
  "end_devices" : 
    "end_device1_id" : {
      "x" : "10",
      "y" : "20",
    },
    "end_device2_id" : {
      "x" : "5",
      "y" : "10",
    },
    "end_deviceN_id" : {
    	"x" : "2",
      "y" : "40",
  	}
}
```

The overall stats should be displayed in a list. The `x` and `y` of each device should be used as their coordinated when rendering a 2d plot using chart.js. The rendered points are clickable with an onClick action that requests a event list of that particular end device.

When the server is requested for the event list of each individual end device and basestation the api json response should look like something like this

```json
{
	"unix_timestamp1" : "event_str1",
  "unix_timestamp2" : "event_str2",
  
  "unix_timestampN" : "event_strN",
}
```

The unix_timestamp which is in seconds, will be converted to the time of the day and the list of the events will be displayed. 





