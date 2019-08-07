# LWS: A discrete event LoRaWAN WUSN Simulator

*Currently in the process of refactoring (again) the old prototype code presented in the paper to a more maintainable and extensible core component of a web simulation app which will be based on Django and React.*

*LWSCore TODOs:*
1. Modify the core transmit logic to a more maintainable and readable form in classes with simpy.env and simpy.Store (check simpy tutorial)
2. Model the behaviours of LWSDevices with FSM 
3. Use Chart.js to produce graphs for simulation results