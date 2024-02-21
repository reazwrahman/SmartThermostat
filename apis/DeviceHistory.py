import datetime
import threading
import logging
from enum import Enum
import os

logger = logging.getLogger(__name__)

STATE_CHANGE_LOGGER = "state_transition_record.txt"


class DeviceConfigKeys(Enum):
    MINIMUM_ON_TIME = "MINIMUM_ON_TIME"
    COOL_DOWN_PERIOD = "COOL_DOWN_PERIOD"
    MAXIMUM_ON_TIME = "MAXIMUM_ON_TIME"


class DeviceHistory:
    """
    Contains device related states and information during program run time.
    This is the shared data between all concurrent threads.
    All members are static by design.
    """

    __device_is_on: bool = False
    __last_turned_on: datetime.datetime = None
    __last_turned_off: datetime.datetime = None

    last_temperature: float = None

    __safety_configs = {
        DeviceConfigKeys.MINIMUM_ON_TIME: 0.2,  # in minutes
        DeviceConfigKeys.COOL_DOWN_PERIOD: 0.2,  # in minutes
        DeviceConfigKeys.MAXIMUM_ON_TIME: 10,  # in minutes
    }

    __temperature_lock = threading.Lock()  # Lock for thread synchronization
    __device_status_lock = threading.Lock() 
    __temperature_read_lock = threading.Lock()

    @staticmethod
    def get_device_status():
        with DeviceHistory.__device_status_lock:  # Acquire lock
            return DeviceHistory.__device_is_on

    @staticmethod
    def set_device_status(new_status: bool, effective_temperature:float = 0.0): 
        with DeviceHistory.__device_status_lock:  # Acquire lock
            DeviceHistory.__device_is_on = new_status
            if new_status:
                DeviceHistory.set_last_turn_on_time(datetime.datetime.now())
            else:
                DeviceHistory.set_last_turn_off_time(datetime.datetime.now()) 
        DeviceHistory.record_state_transition(new_status, effective_temperature)

    @staticmethod
    def get_last_turn_on_time():
        return DeviceHistory.__last_turned_on

    @staticmethod
    def set_last_turn_on_time(timestamp: datetime.datetime):
        DeviceHistory.__last_turned_on = timestamp

    @staticmethod
    def get_last_turn_off_time():
        return DeviceHistory.__last_turned_off

    @staticmethod
    def set_last_turn_off_time(timestamp: datetime.datetime):
        DeviceHistory.__last_turned_off = timestamp

    @staticmethod
    def get_temperature():   
        with DeviceHistory.__temperature_read_lock:
            return DeviceHistory.last_temperature

    @staticmethod
    def update_temperature(new_temperature: float): 
        with DeviceHistory.__temperature_lock:
            DeviceHistory.last_temperature = new_temperature  
      

    @staticmethod
    def get_safety_configs(data_key: str):
        if data_key in DeviceHistory.__safety_configs:
            return DeviceHistory.__safety_configs[data_key]
        else:
            logger.error(
                f"DeviceHistory::get_safety_configs requested key does not exist {data_key}"
            )
            return None

    @staticmethod
    def record_state_transition(status: bool, effective_temperature:float):
        payload = dict()
        if status:
            payload["state_change"] = "Device Turned On"
        else:
            payload["state_change"] = "Device Turned Off"
        payload["current_temperature"] = effective_temperature
        payload["current_timestamp"] = datetime.datetime.now()
        payload["last_turned_on"] = DeviceHistory.get_last_turn_on_time()
        payload["last_turned_off"] = DeviceHistory.get_last_turn_off_time() 
        if payload["last_turned_on"]: 
            payload["on_for_minutes"] = round((payload["current_timestamp"] - payload["last_turned_on"]).total_seconds() / 60,2) 
        if payload["last_turned_off"]: 
            payload["off_for_minutes"] = round((payload["current_timestamp"] - payload["last_turned_off"]).total_seconds() / 60,2) 
        DeviceHistory.__write_to_file(payload)

        # log the state transition
        logging.info("====================================")
        logger.info("Dictionary: %s", payload)
        logging.info("====================================")

    @staticmethod
    def __write_to_file(payload: dict):
        write_mode = None
        if os.path.exists(os.path.join(os.getcwd(), STATE_CHANGE_LOGGER)):
            write_mode = "a"
        else:
            write_mode = "w"

        with open(STATE_CHANGE_LOGGER, write_mode) as file:
            for key, value in payload.items():
                file.write(f"{key}: {value} \n")
            file.write("\n")
