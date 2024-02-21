import sqlite3 
import logging 
from enum import Enum

DB_NAME = 'DeviceHistory.db' 
SHARED_DATA_TABLE = "SharedData"   

logger = logging.getLogger(__name__) 

class SharedDataColumns(Enum):
    ID = "id" 
    DEVICE_STATUS = "device_status" 
    LAST_TEMPERATURE = "last_temperature" 
    LAST_TURNED_ON = "last_turned_on" 
    LAST_TURNED_OFF = "last_turned_off" 
    LAST_UPDATED = "last_updated"

class CreateTable:
    def __init__(self):
        self.db_name = DB_NAME 

    def create_shared_datatable(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {SHARED_DATA_TABLE} (
                    {SharedDataColumns.ID.value} INTEGER PRIMARY KEY, 
                    {SharedDataColumns.DEVICE_STATUS.value} TEXT,
                    {SharedDataColumns.LAST_TEMPERATURE.value} REAL,
                    {SharedDataColumns.LAST_TURNED_ON.value} TEXT,
                    {SharedDataColumns.LAST_TURNED_OFF.value} TEXT,
                    {SharedDataColumns.LAST_UPDATED.value} TEXT
                )
            ''')

            conn.commit()
            logger.info(f"Table {SHARED_DATA_TABLE} created successfully.")

        except sqlite3.Error as e:
            logger.info("Error creating table:", e)

        finally:
            if conn:
                conn.close()

if __name__ == "__main__":
    table_creator = CreateTable()
    table_creator.create_shared_datatable()