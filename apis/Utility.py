import datetime
import json
import logging
from enum import Enum
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grand_parent_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)
sys.path.append(grand_parent_dir)

from apis.DatabaseAccess.CreateTable import SharedDataColumns
from apis.DatabaseAccess.DbInterface import DbInterface
from apis.Config import DeviceStatus
from apis.Registrar import RunningModes

logger = logging.getLogger(__name__)

STATE_CHANGE_LOGGER = "state_transition_record.txt"
MAX_RECORDS_TO_STORE = 20


class Utility:
    """
    Provides general utility services required by other components
    in this program.
    """

    state_transition_counter = 0  # static attribute to track total events recorded

    def __init__(self):
        self.db_interface = DbInterface()

    def record_state_transition(self, state_data: tuple):
        """
        Record state transition events by providing specific information
        """
        status: bool = state_data[0]
        effective_temperature: float = state_data[1]
        reason: str = state_data[2]

        ## read required values from database
        query_result: tuple = self.db_interface.read_multiple_columns(
            (
                SharedDataColumns.TARGET_TEMPERATURE.value,
                SharedDataColumns.LAST_TURNED_ON.value,
                SharedDataColumns.LAST_TURNED_OFF.value,
            )
        )
        payload = dict()

        ## populate payload from input state information
        if status:
            payload["state_change"] = "Device Turned On"
        else:
            payload["state_change"] = "Device Turned Off"
        payload["effective_temperature"] = effective_temperature
        payload["state_change_cause"] = reason

        ## populate payload from database
        payload["target_temperature"] = query_result[0]
        payload["last_turned_on"] = query_result[1]
        payload["last_turned_off"] = query_result[2]

        ## populate payload with extra processing
        payload["current_timestamp"] = datetime.datetime.now()
        if payload["last_turned_on"]:
            last_turned_on: datetime = datetime.datetime.strptime(
                payload["last_turned_on"], "%Y-%m-%d %H:%M:%S.%f"
            )
            payload["on_for_minutes"] = round(
                (payload["current_timestamp"] - last_turned_on).total_seconds() / 60, 2
            )
        if payload["last_turned_off"]:
            last_turned_off: datetime = datetime.datetime.strptime(
                payload["last_turned_off"], "%Y-%m-%d %H:%M:%S.%f"
            )
            payload["off_for_minutes"] = round(
                (payload["current_timestamp"] - last_turned_off).total_seconds() / 60, 2
            )

        self.__write_to_file(payload)

        # log the state transition
        logging.info("====================================")
        logger.info("Dictionary: %s", payload)
        logging.info("====================================")

    def record_state_transition_with_payload(self, payload):
        """
        Record state transition events by providing the full payload
        """
        self.__write_to_file(payload)
        # log the state transition
        logging.info("====================================")
        logger.info("Dictionary: %s", payload)
        logging.info("====================================")

    def __write_to_file(self, payload: dict):
        """
        private method to write payload to a text file
        """
        write_mode = None
        if os.path.exists(os.path.join(os.getcwd(), STATE_CHANGE_LOGGER)):
            write_mode = "a"
        else:
            write_mode = "w"

        with open(STATE_CHANGE_LOGGER, write_mode) as file:
            for key, value in payload.items():
                file.write(f"{key}: {value} \n")
            file.write("\n")

        Utility.state_transition_counter += 1
        self.__delete_older_records()

    def __delete_older_records(self):
        """
        delete old record logging file and start fresh,
        if max storage limit reached
        """
        if Utility.state_transition_counter >= MAX_RECORDS_TO_STORE:
            path = os.path.join(os.getcwd(), STATE_CHANGE_LOGGER)
            os.remove(path)
            Utility.state_transition_counter = 0  # restart counter


if __name__ == "__main__":
    utility = Utility()

    ## test write to file and delete older record capability
    test_payload = {"test_id": 1, "event": "on"}
    capacity_left = 2
    for i in range(MAX_RECORDS_TO_STORE - capacity_left):
        utility.record_state_transition_with_payload(test_payload)

    assert (
        os.path.exists(os.path.join(os.getcwd(), STATE_CHANGE_LOGGER)) == True
    ), "State transition record didn't get created or got deleted prematuredly"

    utility2 = Utility()
    ## force deletion of the state record file
    for i in range(capacity_left):
        utility2.record_state_transition_with_payload(test_payload)

    assert (
        os.path.exists(os.path.join(os.getcwd(), STATE_CHANGE_LOGGER)) == False
    ), "State transition record didn't get deleted as expected"
    print("all passed")
