from threading import Thread
import time
import logging

from apis.DatabaseAccess.DbTables import SharedDataColumns
from apis.Config import DeviceStatus
from apis.Registrar import Registrar
from apis.Config import RUNNING_MODE
from apis.Sensors.TemperatureSensor import TemperatureSensor

DELAY_BETWEEN_READS = 1  # take a read every n seconds
SAMPLE_SIZE = 5  # take average of n reads before taking any action

logger = logging.getLogger(__name__)


class TemperatureSensorThread(Thread):
    """
    CPU thread responsible for reading temeprature sensor
    value in a regular cadence
    """

    def __init__(self, db_interface, thread_name="TemperatureSensorThread"):
        Thread.__init__(self)
        self.thermo_stat: TemperatureSensor = Registrar.get_temperature_sensor(
            RUNNING_MODE
        )
        self.thread_name = thread_name
        self.keep_me_alive = True
        self.db_interface = db_interface
        self.temperature_history: list = []

    def run(self):
        """
        main thread that runs continuously. Update every n seconds,
        with the running average of n sample data
        """
        while self.keep_me_alive:
            device_status = self.db_interface.read_column(
                SharedDataColumns.DEVICE_STATUS.value
            )
            current_temp: float = self.thermo_stat.get_temperature(
                device_status == DeviceStatus.ON.value
            )
            self.temperature_history.append(current_temp)
            if len(self.temperature_history) >= SAMPLE_SIZE:
                running_avg = round(sum(self.temperature_history) / SAMPLE_SIZE, 2)

                self.db_interface.update_column(
                    SharedDataColumns.LAST_TEMPERATURE.value, running_avg
                )
                self.temperature_history = []  # reset batch
            logging.info(f"Current Temperature: {current_temp}")
            time.sleep(DELAY_BETWEEN_READS)

    def terminate(self):
        """
        terminates the thread, inherited from base class
        """
        self.keep_me_alive = False
        logging.info(f"{self.thread_name} is terminated")
