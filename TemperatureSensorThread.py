from threading import Thread
import time
import logging

from apis.TemperatureSensorSim import TemperatureSensorSim
from apis.DeviceHistory import DeviceHistory

DELAY_BETWEEN_READS = 1  # in seconds

logger = logging.getLogger(__name__)


class TemperatureSensorThread(Thread):
    """
    CPU thread responsible for reading temeprature sensor
    value in a regular cadence
    """

    def __init__(self, thread_name="TemperatureSensorThread"):
        Thread.__init__(self)
        self.thermo_stat = TemperatureSensorSim()
        self.thread_name = thread_name
        self.keep_me_alive = True

    def run(self):
        """
        main thread that runs continuously
        """
        while self.keep_me_alive:
            current_temp: float = self.thermo_stat.get_temperature()
            DeviceHistory.update_temperature(current_temp)
            logging.info(
                f"Current Temperature: {DeviceHistory.get_temperature()}"
            )
            time.sleep(DELAY_BETWEEN_READS)

    def terminate(self):
        """
        terminates the thread, inherited from base class
        """
        logging.info(f"{self.thread_name} is terminated")
