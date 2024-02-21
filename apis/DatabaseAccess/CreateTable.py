import sqlite3 
import logging

DB_NAME = 'DeviceHistory.db' 
SHARED_DATA_TABLE = "SharedData"   

logger = logging.getLogger(__name__)

class CreateTable:
    def __init__(self):
        self.db_name = DB_NAME 

    def create_shared_datatable(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {SHARED_DATA_TABLE} (
                    id INTEGER PRIMARY KEY, 
                    device_status TEXT,
                    last_temperature REAL,
                    last_turned_on TEXT,
                    last_turned_off TEXT,
                    last_updated TEXT
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