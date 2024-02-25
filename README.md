# How to run the app and the unit tests?

1) to run application: (from the application directory) run 
```python3 app.py```

2) to run unit tests in TemperatureSensorSim, again run from the application  
directory: ```python3 apis/Sensors/TemperatureSensorSim.py```  
Run the other unit tests from the root directory in the same way.  

3) Alternatively, you could run the following command to run all the unit tests 
in one shot: 
```python3 run_unit_tests.py```

4) Do not try to run any unit test directly from that file's directory, 
this will cause module importing error. The project was written in a way 
so that everything is run from the root.  

5) Github repository for this project: https://github.com/reazwrahman/SmartThermostat



# Docker instructions 
1) to build: ```docker build --no-cache -t thermostat-docker .``` 
2) to run application in docker: 
```docker run -it thermostat-docker``` 
3) to run docker terminal: 
```docker run -it thermostat-docker /bin/bash```


# A summary of the project and the motivation behind it 

I live in an old single family house in New York City. The boiler heating system in the house is far from ideal in the winter. Either it gets unbearably hot in my room during the day to do any work or extremely cold at night making me wake up in the middle of the night. 

I have an electric heater in my room which I can turn on and off manually to get the temperature I want in the room but the problem is I don’t want to wake up in the middle of the night to turn on/off this device. My solution is to automatically control the heater based on the current temperature in the room. 

In order to implement this solution, I would need a temperature sensor, a power relay to control the power supply to the electric heater and a microprocessor to run all the logic. For the microprocessor piece I have chosen a Raspberry Pi (https://www.raspberrypi.com/). Raspberry Pi runs on Python and is extremely popular among hobby Python developers. 

My plan is to divide the project to have two different modes: 1) I am calling the first one “target” state where everything will be running on actual hardware (microcontroller, sensor and relay) and 2) the simulation mode where I can run the program on any computer and test out the fundamental logic.   

My first goal is to get the simulation mode running and this is what is particular codebase does. I have stubbed out the Target version of the TemperatureSensor and RelayController objects. 

The program produces logs which can be used to validate the behavior of each component, and it also produces a state_transition_record.txt file that records the last 20 state transtion (heater going from on to off or vice versa). These two outputs are sufficient to validate the program behavior. The program also uses a DeviceHistory.db database to store the shared data that's used and updated by multiple concurrent threads.