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
from apis.DatabaseAccess.DbInterface import DbInterface, DeviceStatus

logger = logging.getLogger(__name__)

SAFETY_CONFIGS_FILE = "apis/safety_configs.json"
STATE_CHANGE_LOGGER = "state_transition_record.txt"
MAX_RECORDS_TO_STORE = 20


class DeviceConfigKeys(Enum):
    MINIMUM_ON_TIME = "MINIMUM_ON_TIME"
    COOL_DOWN_PERIOD = "COOL_DOWN_PERIOD"
    MAXIMUM_ON_TIME = "MAXIMUM_ON_TIME"


class Utility:
    """
    Provides general utility services required by other components
    in this program.
    """

    state_transition_counter = 0  # static attribute to track total events recorded

    def __init__(self):
        self.__safety_configs: dict = dict()
        self.__read_safety_configs()
        self.db_interface = DbInterface()

    def __read_safety_configs(self):
        """
        Reads a user defined json file to set the safety config parameters
        """
        try:
            with open(SAFETY_CONFIGS_FILE, "r") as file:
                config_data: dict = json.load(file)
        except Exception as e:
            logger.error(
                f"Utility::__read_safety_configs failed to read file: {SAFETY_CONFIGS_FILE}, exception: {str(e)}"
            )
            sys.exit()

        try:
            self.__safety_configs = config_data
        except Exception as e:
            logger.error(
                f"An error occured while trying to {SAFETY_CONFIGS_FILE}, recheck the data types. Exception details: {str(e)}"
            )
            sys.exit()

    def get_safety_configs(self, data_key: str):
        """
        get safety config value by providing a config key
        """
        if data_key in self.__safety_configs:
            return self.__safety_configs[data_key]
        else:
            logger.error(
                f"Utility::get_safety_configs requested key does not exist {data_key}"
            )
            return None

    def record_state_transition(
        self, status: bool, effective_temperature: float, reason: str
    ):
        """
        Record state transition events by providing specific information
        """
        payload = dict()
        if status:
            payload["state_change"] = "Device Turned On"
        else:
            payload["state_change"] = "Device Turned Off"
        payload["effective_temperature"] = effective_temperature
        payload["target_temperature"] = self.db_interface.read_column(
            SharedDataColumns.TARGET_TEMPERATURE.value
        )
        payload["state_change_cause"] = reason
        payload["current_timestamp"] = datetime.datetime.now()
        payload["last_turned_on"] = self.db_interface.read_column(
            SharedDataColumns.LAST_TURNED_ON.value
        )
        payload["last_turned_off"] = self.db_interface.read_column(
            SharedDataColumns.LAST_TURNED_OFF.value
        )
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

    ## test read config data capability
    assert (
        type(utility.get_safety_configs(DeviceConfigKeys.MAXIMUM_ON_TIME.value)) == int
    ), "Safety configs values are not loaded properly"
    assert (
        type(utility.get_safety_configs(DeviceConfigKeys.COOL_DOWN_PERIOD.value)) == int
    ), "Safety configs values are not loaded properly"
    assert (
        type(utility.get_safety_configs(DeviceConfigKeys.MINIMUM_ON_TIME.value)) == int
    ), "Safety configs values are not loaded properly"

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
