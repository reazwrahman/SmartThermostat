import os
import sys
import logging
import datetime
from enum import Enum

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grand_parent_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)
sys.path.append(grand_parent_dir)

from apis.Utility import Utility
from apis.DatabaseAccess.CreateTable import SharedDataColumns
from apis.DatabaseAccess.DbInterface import DbInterface
from apis.Config import DeviceStatus
from apis.Registrar import Registrar
from apis.Config import RUNNING_MODE, MINIMUM_ON_TIME, COOL_DOWN_PERIOD

logger = logging.getLogger(__name__)


class States(Enum):
    ALREADY_ON = "ALREADY_ON"
    ALREADY_OFF = "ALREADY_OFF"
    TURNED_ON = "TURNED_ON"
    TURNED_OFF = "TURNED_OFF"
    REQUEST_DENIED = "REQUEST_DENIED"
    NO_ACTION = "NO_ACTION"


class PowerControlGateKeeper:
    """
    This class is responsible for ensuring that it's safe to turn on or
    turn off the device, based on the safety parameters
    outlined in the configs.
    """

    def __init__(self, db_interface: DbInterface, running_mode="Simulation"):
        self.relay_controller = Registrar.get_relay_controllers(RUNNING_MODE)
        self.db_interface: DbInterface = db_interface
        self.utility = Utility()

    def turn_on(self, effective_temperature=0.0, reason=""):
        """
        Goes through a decision making process to determine
        whether it's safe to trigger the relay controller
        """
        if (
            self.db_interface.read_column(SharedDataColumns.DEVICE_STATUS.value)
            == DeviceStatus.ON.value
        ):
            message = "PowerControlGateKeeper::turn_on, device is already on, nothing to do here"
            logger.info(message)
            return States.ALREADY_ON

        last_turned_off: str = self.db_interface.read_column(
            SharedDataColumns.LAST_TURNED_OFF.value
        )
        if not last_turned_off:
            self.relay_controller.turn_on(effective_temperature, reason=reason)
            return States.TURNED_ON

        current_time: datetime = datetime.datetime.now()

        # Calculate the difference in minutes
        last_turned_off: datetime = datetime.datetime.strptime(
            last_turned_off, "%Y-%m-%d %H:%M:%S.%f"
        )
        time_difference = (current_time - last_turned_off).total_seconds() / 60
        if time_difference >= COOL_DOWN_PERIOD:
            self.relay_controller.turn_on(effective_temperature, reason=reason)
            logger.warn("PowerControlGateKeeper::turn_on turning device on")
            return States.TURNED_ON

        else:
            logger.warn(
                "PowerControlGateKeeper::turn_on Unable to turn device on, device is currently in a cool down stage"
            )
            return States.REQUEST_DENIED

    def turn_off(self, effective_temperature=0.0, reason=""):
        """
        Goes through a decision making process to determine
        whether it's safe to trigger the relay controller
        """
        successful_log_msg = "PowerControlGateKeeper::turn_off turning device off"

        if (
            self.db_interface.read_column(SharedDataColumns.DEVICE_STATUS.value)
            == DeviceStatus.OFF.value
        ):
            logger.info(
                "PowerControlGateKeeper::turn_off, device is already off, nothing to do here"
            )
            return States.ALREADY_OFF

        last_turned_on: str = self.db_interface.read_column(
            SharedDataColumns.LAST_TURNED_ON.value
        )
        if not last_turned_on:
            self.relay_controller.turn_off(effective_temperature, reason=reason)
            logger.warn(successful_log_msg)
            return States.TURNED_OFF

        current_time: datetime = datetime.datetime.now()

        # Calculate the difference in minutes
        last_turned_on: datetime = datetime.datetime.strptime(
            last_turned_on, "%Y-%m-%d %H:%M:%S.%f"
        )
        time_difference = (current_time - last_turned_on).total_seconds() / 60

        if time_difference >= MINIMUM_ON_TIME:
            self.relay_controller.turn_off(effective_temperature, reason=reason)
            logger.warn(successful_log_msg)
            return States.TURNED_OFF

        else:
            logger.warn(
                "PowerControlGateKeeper::turn_off Unable to turn device off, device needs to be on for a minimum period of time"
            )
            return States.REQUEST_DENIED
