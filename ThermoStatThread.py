from threading import Thread
import time
import logging
import datetime
import os

from apis.PowerControlGateKeeper import PowerControlGateKeeper, States
from apis.DeviceHistory import DeviceHistory, DeviceConfigKeys

DELAY_BETWEEN_READS = 1  # take a read every n seconds
SAMPLE_SIZE = 1  # take average of n reads before taking any action

logger = logging.getLogger(__name__)


class ThermoStatThread(Thread):
    """
    CPU thread responsible triggering power relay depending on
    current temperature and target temperature
    """

    def __init__(
        self, target_temperature: float, thread_name="ThermoStatThread"
    ):
        Thread.__init__(self)
        self.target_temp = target_temperature
        self.thread_name = thread_name
        self.keep_me_alive = True

        self.__gate_keeper = PowerControlGateKeeper()

    def run(self):
        """
        main thread that runs continuously. Read current temperature
        at regular intervals, take running average and trigger relay.
        """
        while self.keep_me_alive: 
            status = self.__check_device_on_time()
            if status != States.TURNED_OFF:
                current_temp: float = None
                running_avg: float = None
                temperature_history: list = []
            current_temp = DeviceHistory.get_temperature()
            if current_temp:
                temperature_history.append(current_temp)
                if len(temperature_history) == SAMPLE_SIZE:
                    running_avg = round(
                        sum(temperature_history) / SAMPLE_SIZE, 2
                    )
                    if running_avg <= self.target_temp:
                        status = self.__gate_keeper.turn_on(running_avg) 
                        logging.warn(f"temp went below triggering")
                    else:
                        status = self.__gate_keeper.turn_off(running_avg) 

            time.sleep(DELAY_BETWEEN_READS)

    def terminate(self):
        """
        terminates the thread, inherited from base class
        """
        logging.warn(f"{self.thread_name} is terminated")

    def __check_device_on_time(self):
        last_turned_on: datetime = DeviceHistory.get_last_turn_on_time()
        if last_turned_on:
            current_time: datetime = datetime.datetime.now()
            time_difference = (current_time - last_turned_on).total_seconds() / 60

            if time_difference >= DeviceHistory.get_safety_configs(
                DeviceConfigKeys.MAXIMUM_ON_TIME
            ):
                logger.warn(
                    "ThermoStatThread::__check_heater_on_time Device's maximum on time has exceeded"
                )
                status = self.relay_controller.turn_off()
                return status

        return States.NO_ACTION
