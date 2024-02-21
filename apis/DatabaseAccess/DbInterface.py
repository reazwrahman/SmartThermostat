import sqlite3  
import logging

DB_NAME = "DeviceHistory.db"
SHARED_DATA_TABLE = "SharedData" 

logger = logging.getLogger(__name__)

class DbInterface:
    def __init__(self):
        self.db_name = DB_NAME

    def update_temperature(self, temperature:float):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

           # Check if the table is empty
            cursor.execute(f'SELECT COUNT(*) FROM {SHARED_DATA_TABLE}')
            count = cursor.fetchone()[0]

            if count == 0:
                # Insert the initial temperature value
                cursor.execute(f'''
                    INSERT INTO {SHARED_DATA_TABLE} (id, last_temperature)
                    VALUES (1, ?)
                ''', (temperature,))
            else:
                # Update the temperature value in the database
                cursor.execute(f'''
                    UPDATE {SHARED_DATA_TABLE}
                    SET last_temperature = ?
                    WHERE id = 1
                ''', (temperature,))

            conn.commit()
            logger.info("Temperature value updated successfully.")

        except sqlite3.Error as e:
            logger.error("Error updating temperature value:", e)

        finally:
            if conn:
                conn.close()


    def read_temperature(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Read the temperature value from the database
            cursor.execute(f'''
                SELECT last_temperature
                FROM {SHARED_DATA_TABLE}
                WHERE id = 1
            ''')
            temperature = cursor.fetchone()

            if temperature: 
                logger.info(f"temeprature read from db: {temperature[0]}")
                return temperature[0]
            else:
                logger.warn("No temperature data found.")
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
    written_temeprature = 19.6
    temperature_interface.update_temperature(written_temeprature) 
    temperature_value = temperature_interface.read_temperature() 
    assert written_temeprature == temperature_value, "Temperature values don't match in the datbase"