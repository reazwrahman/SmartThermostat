import logging
import os

from TemperatureSensorThread import TemperatureSensorThread
from ThermoStatThread import ThermoStatThread
from apis.DatabaseAccess.CreateTable import CreateTable
from apis.DatabaseAccess.DbInterface import DbInterface

STATE_CHANGE_LOGGER = "state_transition_record.txt"
DATABASE = "DeviceHistory.db"

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

## TODO: write a function here to get user input on temperature, use args if
### guideline supports it
def get_target_temperature(): 
    pass

def register_threads(target_temperature, db_api:DbInterface):

    # set guarantees that each thread can only be registered once
    registered_threads:set = set() 

    sensor_thread: TemperatureSensorThread = TemperatureSensorThread(db_interface=db_api)

    thermostat_thread: ThermoStatThread = ThermoStatThread(
        target_temperature=target_temperature, db_interface=db_api
    )
    registered_threads.add(sensor_thread) 
    registered_threads.add(thermostat_thread)  

    return registered_threads

if __name__ == "__main__":  
    if os.path.exists(os.path.join(os.getcwd(), STATE_CHANGE_LOGGER)):
        os.remove(STATE_CHANGE_LOGGER)

    if os.path.exists(os.path.join(os.getcwd(), DATABASE)):
        os.remove(DATABASE)  
    
    table_creator = CreateTable()
    table_creator.create_shared_datatable()
    db_api = DbInterface()

    target_temperature:float = get_target_temperature()
    registered_threads:set = register_threads(22, db_api)

    for each_thread in registered_threads: 
        each_thread.start() 

    for each_thread in registered_threads:
        each_thread.join()
