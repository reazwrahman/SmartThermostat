import logging
import os

from TemperatureSensorThread import TemperatureSensorThread
from ThermoStatThread import ThermoStatThread
from apis.DatabaseAccess.CreateTable import CreateTable
from apis.DatabaseAccess.DbInterface import DbInterface
from apis.Registrar import Registrar, RunningModes
from apis.TemperatureSensorSim import TemperatureSensorSim
from apis.TemperatureSensorTarget import TemperatureSensorTarget
from apis.RelayControllerSim import RelayControllerSim
from apis.RelayControllerTarget import RelayControllerTarget

STATE_CHANGE_LOGGER = "state_transition_record.txt"
DATABASE = "DeviceHistory.db"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


## TODO: write a function here to get user input on temperature, use args if
### guideline supports it
def get_target_temperature():
    pass


if __name__ == "__main__":
    ## clean up directory
    if os.path.exists(os.path.join(os.getcwd(), STATE_CHANGE_LOGGER)):
        os.remove(STATE_CHANGE_LOGGER)

    if os.path.exists(os.path.join(os.getcwd(), DATABASE)):
        os.remove(DATABASE)

    ## prepare database
    table_creator = CreateTable()
    table_creator.create_shared_datatable()
    db_api = DbInterface()

    ## register all sensors
    simulation_sensor = TemperatureSensorSim()
    target_sensor = TemperatureSensorTarget()
    Registrar.register_temperature_sensor(simulation_sensor, RunningModes.SIM)
    Registrar.register_temperature_sensor(target_sensor, RunningModes.TARGET)

    ## register all relay controllers
    simulation_relay = RelayControllerSim(db_interface=db_api)
    target_relay = RelayControllerTarget()
    Registrar.register_relay_controllers(simulation_relay, RunningModes.SIM)
    Registrar.register_relay_controllers(target_relay, RunningModes.TARGET)

    ## register all threads
    sensor_thread: TemperatureSensorThread = TemperatureSensorThread(
        db_interface=db_api
    )
    Registrar.register_thread(sensor_thread)

    thermostat_thread: ThermoStatThread = ThermoStatThread(
        target_temperature=22.0, db_interface=db_api
    )
    Registrar.register_thread(thermostat_thread)

    ## start all threads
    registered_threads: set = Registrar.get_registered_threads()
    for each_thread in registered_threads:
        each_thread.start()

    for each_thread in registered_threads:
        each_thread.join()
