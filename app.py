import logging
import os

from TemperatureSensorThread import TemperatureSensorThread
from ThermoStatThread import ThermoStatThread
from apis.DatabaseAccess.CreateTable import CreateTable
from apis.DatabaseAccess.DbInterface import DbInterface
from apis.Registrar import Registrar, RunningModes
from apis.Sensors.TemperatureSensorSim import TemperatureSensorSim
from apis.Sensors.TemperatureSensorTarget import TemperatureSensorTarget
from apis.Relays.RelayControllerSim import RelayControllerSim
from apis.Relays.RelayControllerTarget import RelayControllerTarget

STATE_CHANGE_LOGGER = "state_transition_record.txt"
DATABASE = "DeviceHistory.db"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_target_temperature():
    input_is_invalid: bool = True
    while input_is_invalid:
        try:
            target_temp = input(
                "Please enter the desired temperature in Celsius (between 0 and 50): "
            )
            target_temp = float(target_temp)
            if target_temp < 0 or target_temp > 50:
                raise ValueError
            input_is_invalid = False
        except ValueError:
            print(
                "Entered value is either not convertible to a number or outside of the 0 to 50 range"
            )

        except Exception as e:
            print(f"Unknown exception occured, exception: {str(e)}")

    return target_temp


if __name__ == "__main__":
    ## get target temperature
    target_temp: float = get_target_temperature()

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
        target_temperature=target_temp, db_interface=db_api
    )
    Registrar.register_thread(thermostat_thread)

    ## start all threads
    registered_threads: set = Registrar.get_registered_threads()
    for each_thread in registered_threads:
        each_thread.start()

    for each_thread in registered_threads:
        each_thread.join()
