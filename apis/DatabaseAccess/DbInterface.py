import sqlite3
import logging
from enum import Enum

from apis.DatabaseAccess.CreateTable import SharedDataColumns

DB_NAME = "DeviceHistory.db"
SHARED_DATA_TABLE = "SharedData"

logger = logging.getLogger(__name__)


class DeviceStatus(Enum):
    ON = "ON"
    OFF = "OFF"


class DbInterface:
    """
    An API to interact with the database
    """

    def __init__(self):
        self.db_name = DB_NAME

    def update_column(self, column_name, new_value):
        """
        Updates a column in the database table with the provided value
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Check if the table is empty
            cursor.execute(f"SELECT COUNT(*) FROM {SHARED_DATA_TABLE}")
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.execute(
                    f"""
                    INSERT INTO {SHARED_DATA_TABLE} (id, {column_name})
                    VALUES (1, ?)
                """,
                    (new_value,),
                )
            else:
                cursor.execute(
                    f"""
                    UPDATE {SHARED_DATA_TABLE}
                    SET {column_name} = ?
                    WHERE id = 1
                """,
                    (new_value,),
                )

            conn.commit()
            logger.info(f"{column_name} value updated successfully: {new_value}.")

        except sqlite3.Error as e:
            logger.error(f"Error updating {column_name} value:", e)

        finally:
            if conn:
                conn.close()

    def read_column(self, column_name):
        """
        reads the specified column from the table and returns the value
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute(
                f"""
                SELECT {column_name}
                FROM {SHARED_DATA_TABLE}
                WHERE id = 1
            """
            )
            value = cursor.fetchone()

            if value:
                logger.debug(f"{column_name} read from db: {value[0]}")
                return value[0]
            else:
                logger.warn(f"No {column_name} data found.")
                return None

        except sqlite3.Error as e:
            logger.error("Error reading temperature value:", e)
            return None

        finally:
            if conn:
                conn.close()


if __name__ == "__main__":
    # Example usage
    temperature_interface = DbInterface()
    written_temeprature = 0.9
    temperature_interface.update_column(
        SharedDataColumns.LAST_TEMPERATURE.value, written_temeprature
    )
    temperature_value = temperature_interface.read_column(
        SharedDataColumns.LAST_TEMPERATURE.value
    )
    assert (
        written_temeprature == temperature_value
    ), "Temperature values don't match in the datbase"
    print("all good son")
