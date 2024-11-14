import json
import paho.mqtt.client as mqtt
import sqlite3
import logging
from typing import Any, Dict
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve configuration from environment variables
DATABASE_NAME = os.getenv('DATABASE_NAME', 'sensor_data.db')
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))


def init_db() -> None:
    """
    Initializes the database by creating a table if it doesn't exist.

    Returns:
        None
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id TEXT NOT NULL,
            pm25 REAL,
            pm10 REAL,
            temperature REAL,
            humidity REAL,
            heca_temperature REAL,
            heca_humidity REAL,
            pressure REAL,
            pressure_sea_level REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def save_to_db(sensor_id: str, data: dict) -> None:
    """
    Saves sensor data to the database.

    Args:
        sensor_id (str): The ID of the sensor.
        data (dict): The sensor data to be saved.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sensor_data (
            sensor_id,
            pm25,
            pm10,
            temperature,
            humidity,
            heca_temperature,
            heca_humidity,
            pressure,
            pressure_sea_level
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        sensor_id,
        data.get('sds011', {}).get('pm25'),
        data.get('sds011', {}).get('pm10'),
        data.get('sht', {}).get('temperature')
        or data.get('bmp', {}).get('temperature'),
        data.get('sht', {}).get('humidity'),
        data.get('sht_heca', {}).get('temperature'),
        data.get('sht_heca', {}).get('humidity'),
        data.get('bmp', {}).get('pressure'),
        data.get('bmp', {}).get('pressure_sea_level')
    ))
    conn.commit()
    conn.close()


def on_connect(
        client: mqtt.Client, userdata: Any, flags: Dict[str, int], rc: int) -> None:
    """
    Callback function. Called when the client connects to the broker.

    Parameters:
    - client: The MQTT client instance.
    - userdata: The private user data as set in the MQTT client constructor.
    - flags: Response flags sent by the MQTT broker.
    - rc: The connection result code.
    """
    logger.info("Connected with result code %s", str(rc))
    client.subscribe("smog/sensor0")
    client.subscribe("smog/sensor1")


def on_message(client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
    """
    Callback function that is called when a message is received.

    Args:
        client: The MQTT client instance for this callback.
        userdata: The private user data as set in the MQTT client constructor.
        msg: An instance of MQTTMessage. This object contains the topic
            and payload of the received message.

    Raises:
        json.JSONDecodeError: If the payload cannot be decoded as JSON.
    """
    logger.info("Received message from %s: %s", msg.topic, msg.payload.decode())
    sensor_id = msg.topic.split('/')[-1]
    try:
        data = json.loads(msg.payload.decode())
        save_to_db(sensor_id, data)
    except json.JSONDecodeError as e:
        logger.error("Failed to decode JSON: %s", e)


def main() -> None:
    """
    Main function that initializes the database, connects to the MQTT broker,
    and starts the loop to process network traffic.
    """
    init_db()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    client.loop_forever()


if __name__ == "__main__":
    main()
