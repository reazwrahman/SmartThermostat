import os
import sys
import logging

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grand_parent_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)
sys.path.append(grand_parent_dir)

from application.apis.RelayController import RelayController
from application.apis.DeviceHistory import DeviceHistory

logger = logging.getLogger(__name__)


class RelayControllerSim(RelayController):
    """
    Simulation class intended to mimic the behavior of the actual
    relay controller class.
    """

    def __init__(self):
        self.current_state: bool = False

    def setup(self):
        pass

    def turn_on(self):
        """
        Simulates turning on the device connected to the power relay.
        """
        self.current_state = True
        try:
            DeviceHistory.set_device_status(True)
            return True
        except Exception as e:
            logger.error(
                f"RelayControllerSim::turn_on failed to set device status to True, exception:{str(e)}"
            )
            return False

    def turn_off(self):
        """
        Simulates turning off the device connected to the power relay.
        """
        self.current_state = False
        try:
            DeviceHistory.set_device_status(False)
            return True
        except Exception as e:
            logger.error(
                f"RelayControllerSim::turn_off failed to set device status to False, exception:{str(e)}"
            )
            return False


if __name__ == "__main__":
    controller = RelayControllerSim()
    assert (
        controller.current_state == False
    ), "Failed, Expected initial state to be False"

    ## test turn_on method
    controller.turn_on()
    assert (
        controller.current_state == True
    ), "RelayControllerSim failed to turn on device"
    assert (
        DeviceHistory.get_device_status() == True
    ), "RelayControllerSim failed to turn on device"

    ## test turn_off method
    controller.turn_off()
    assert (
        controller.current_state == False
    ), "RelayControllerSim failed to turn off device"
    assert (
        DeviceHistory.get_device_status() == False
    ), "RelayControllerSim failed to turn off device"

    logger.error("all test succeeded")
