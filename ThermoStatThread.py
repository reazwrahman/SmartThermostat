from threading import Thread
import time
import logging
import datetime
import os

from apis.Relays.PowerControlGateKeeper import PowerControlGateKeeper, States
from apis.DatabaseAccess.CreateTable import SharedDataColumns
from apis.DatabaseAccess.DbInterface import DbInterface
from apis.Utility import Utility
from apis.Config import MAXIMUM_ON_TIME

DELAY_BETWEEN_READS = 10  # take a read every n seconds

logger = logging.getLogger(__name__)


class ThermoStatThread(Thread):
    """
    CPU thread responsible triggering power relay depending on
    current temperature and target temperature
    """

    def __init__(
        self,
        target_temperature: float,
        db_interface: DbInterface,
        thread_name="ThermoStatThread",
    ):
        Thread.__init__(self)
        self.target_temp = target_temperature
        self.thread_name = thread_name
        self.keep_me_alive = True
        self.db_interface: DbInterface = db_interface
        self.utility = Utility()

        self.__gate_keeper: PowerControlGateKeeper = PowerControlGateKeeper(
            db_interface=db_interface
        )
        self.db_interface.update_column(
            SharedDataColumns.TARGET_TEMPERATURE.value, self.target_temp
        )

    def run(self):
        """
        main thread that runs continuously. Read current temperature
        at regular intervals, take running average and trigger relay.
        """
        while self.keep_me_alive:
            status = self.__check_device_on_time()
            if status != States.TURNED_OFF:
                current_temp: float = self.db_interface.read_column(
                    SharedDataColumns.LAST_TEMPERATURE.value
                )
                if current_temp:
                    if current_temp <= self.target_temp:
                        status = self.__gate_keeper.turn_on(
                            effective_temperature=current_temp,
                            reason="Current Temperature is below target temperature",
                        )
                    else:
                        status = self.__gate_keeper.turn_off(
                            effective_temperature=current_temp,
                            reason="Current Temperature is above target temperature",
                        )

            time.sleep(DELAY_BETWEEN_READS)

    def terminate(self):
        """
        terminates the thread, inherited from base class
        """
        logging.warn(f"{self.thread_name} is terminated")

    def __check_device_on_time(self):
        last_turned_on: str = self.db_interface.read_column(
            SharedDataColumns.LAST_TURNED_ON.value
        )
        if last_turned_on:
            last_turned_on: datetime = datetime.datetime.strptime(
                last_turned_on, "%Y-%m-%d %H:%M:%S.%f"
            )
            current_time: datetime = datetime.datetime.now()
            time_difference = (current_time - last_turned_on).total_seconds() / 60
            if time_difference >= self.utility.get_safety_configs(MAXIMUM_ON_TIME):
                logger.warn(
                    "ThermoStatThread::__check_heater_on_time Device's maximum on time has exceeded"
                )
                status = self.__gate_keeper.turn_off(
                    effective_temperature=0.0,
                    reason="Device's maximum on time has exceeded",
                )
                return status

        return States.NO_ACTION
