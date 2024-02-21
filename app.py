import logging 
import os

from TemperatureSensorThread import TemperatureSensorThread
from ThermoStatThread import ThermoStatThread  
from apis.DatabaseAccess.CreateTable import CreateTable 
from apis.DatabaseAccess.DbInterface import DbInterface

STATE_CHANGE_LOGGER = "state_transition_record.txt" 
DATABASE = "DeviceHistory.db" 


if os.path.exists(os.path.join(os.getcwd(), STATE_CHANGE_LOGGER)): 
    os.remove(STATE_CHANGE_LOGGER) 

if os.path.exists(os.path.join(os.getcwd(), DATABASE)): 
    os.remove(DATABASE)

logging.basicConfig(level=logging.WARN) 
logger = logging.getLogger(__name__)   

table_creator = CreateTable() 
table_creator.create_shared_datatable()
db_api = DbInterface() 


sensor_thread: TemperatureSensorThread = TemperatureSensorThread(db_interface = db_api)
sensor_thread.start() 

thermostat_thread: ThermoStatThread = ThermoStatThread(target_temperature=22.0, db_interface=db_api)
thermostat_thread.start()  

sensor_thread.join()
thermostat_thread.join()

## TODO: write a function here to get user input on temperature, use args if
### guideline supports it

## keep it at that, go thru guidelines and make additions to check the boxes.
