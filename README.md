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


# Helpful tips for grading 

1) to look for the usage of a specific data structure, do a global search 
with set, dict, list or tuple. 
I have initialized the data structure with those types, a global search should 
pick those up from the repository. 
example: ```my_list:list = [1,2,3] ```  

2) 1 iteration type (for, while), 1 conditional (if) & 
1 try block with an else condition. 

These are kinda spread across the codebase, a global search should do the trick. 

3) To meet the requirement for 1 user-defined function: 
look at the two functions in the app.py file: ```get_target_temperature``` 
and ```delete_file``` 

4) for requirements below: use the apis/Utility.py file. I have written it 
in a way so that it meets all the requirements.  

    a) 1 user-defined class. The class must be imported by your main program from 
        a separate file and have the following required structures. [DONE]

    b) at least 1 private and 2 public self class attributes [DONE]

    c) at least 1 private and 2 public class methods that take arguments, return 
        values and are used by your program [DONE] 

    d) an init() class method that takes at least 1 argument [DONE]

    e) a repr() or str() class method [DONE]

    f) a magic class method (not one of the methods listed above) [DONE]

    g) Provide 2 unit tests that prove two of your public class methods work as expected.
        The tests should evaluate results using assert statements. [DONE]