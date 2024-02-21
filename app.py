import logging 
import os

from TemperatureSensorThread import TemperatureSensorThread
from ThermoStatThread import ThermoStatThread  
from apis.DatabaseAccess.CreateTable import CreateTable 
from apis.DatabaseAccess.DbInterface import DbInterface

STATE_CHANGE_LOGGER = "state_transition_record.txt"

if os.path.exists(os.path.join(os.getcwd(), STATE_CHANGE_LOGGER)): 
    os.remove(STATE_CHANGE_LOGGER)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


table_creator = CreateTable() 
table_creator.create_shared_datatable() 

dbInterface = DbInterface() 
dbInterface.update_temperature(21.9) 
dbInterface.read_temperature()

"""sensor_thread: TemperatureSensorThread = TemperatureSensorThread()
sensor_thread.start()

thermostat_thread: ThermoStatThread = ThermoStatThread(target_temperature=22.0)
thermostat_thread.start()"""

## TODO: write a function here to get user input on temperature, use args if
### guideline supports it

## keep it at that, go thru guidelines and make additions to check the boxes.
