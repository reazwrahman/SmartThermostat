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

from application.apis.RelayControllerTarget import RelayControllerTarget
from application.apis.RelayControllerSim import RelayControllerSim
from application.apis.DeviceHistory import DeviceHistory, DeviceConfigKeys

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

    def __init__(self, running_mode="Simulation"):
        if running_mode == "Simulation":
            self.relay_controller = RelayControllerSim()
        else:
            self.relay_controller = RelayControllerTarget()

    def turn_on(self, effective_temperature=0.0):
        """
        Goes through a decision making process to determine
        whether it's safe to trigger the relay controller
        """

        if DeviceHistory.get_device_status():
            message = "PowerControlGateKeeper::turn_on, device is already on, nothing to do here"
            logger.debug(message)
            return States.ALREADY_ON

        last_turned_off: datetime = DeviceHistory.get_last_turn_off_time()
        if not last_turned_off:
            self.relay_controller.turn_on(effective_temperature)
            return States.TURNED_ON

        current_time: datetime = datetime.datetime.now()

        # Calculate the difference in minutes
        time_difference = (current_time - last_turned_off).total_seconds() / 60

        if time_difference >= DeviceHistory.get_safety_configs(
            DeviceConfigKeys.COOL_DOWN_PERIOD
        ):
            self.relay_controller.turn_on(effective_temperature)
            logger.warn("PowerControlGateKeeper::turn_on turning device on")
            return States.TURNED_ON

        else:
            logger.warn(
                "PowerControlGateKeeper::turn_on Unable to turn device on, device is currently in a cool down stage"
            )
            return States.REQUEST_DENIED

    def turn_off(self, effective_temperature=0.0):
        """
        Goes through a decision making process to determine
        whether it's safe to trigger the relay controller
        """
        successful_log_msg = (
                "PowerControlGateKeeper::turn_off turning device off"
            )
    
        if DeviceHistory.get_device_status() == False:
            logger.debug(
                "PowerControlGateKeeper::turn_off, device is already off, nothing to do here"
            )
            return States.ALREADY_OFF

        last_turned_on: datetime = DeviceHistory.get_last_turn_on_time()
        if not last_turned_on:
            self.relay_controller.turn_off(effective_temperature)
            logger.warn(successful_log_msg)
            return States.TURNED_OFF

        current_time: datetime = datetime.datetime.now()

        # Calculate the difference in minutes
        time_difference = (current_time - last_turned_on).total_seconds() / 60

        if time_difference >= DeviceHistory.get_safety_configs(
            DeviceConfigKeys.MINIMUM_ON_TIME
        ):
            self.relay_controller.turn_off(effective_temperature)
            logger.warn(successful_log_msg)
            return States.TURNED_OFF

        else:
            logger.warn(
                "PowerControlGateKeeper::turn_off Unable to turn device off, device needs to be on for a minimum period of time"
            )
            return States.REQUEST_DENIED
