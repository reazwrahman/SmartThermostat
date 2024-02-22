# How to run the app and the unit tests?

1) to run application: (from the application directory) run 
```python3 app.py```

2) to run unit tests in TemperatureSensorSim, again run from the application  
directory: ```python3 apis/Sensors/TemperatureSensorSim.py```  
Run the other unit tests from the root directory in the same way.  

3) Do not try to run any unit tests directly from that file's directory, 
this will cause module importing error. The project was written in a way 
so that everything is run from the root. 


# Helpful tips for grading 

1) to look for the usage of a specific data structure, do a global search 
with set, dict, list or tuple. 
I have initialized the data structure with those types, a global search should 
pick those up from the repository. 
example: ```my_list:list = [1,2,3] ```