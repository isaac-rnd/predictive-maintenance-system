import time
import threading
from confluent_kafka import Producer
import paho.mqtt.client as mqtt

MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'maintainence'
username = "isaac"
password = "isaac"

# Global variable to store the latest message
latest_message = None

# MQTT on_message callback
def on_message(client, userdata, msg):
    global latest_message
    latest_message = msg.payload.decode()
    print(f"Received message from MQTT topic {msg.topic}: {latest_message}")

def mqtt_client_thread():
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(username, password)
    mqtt_client.on_message = on_message

    # Connect to the MQTT broker
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.subscribe(MQTT_TOPIC)
    mqtt_client.loop_forever()

def get_latest_message():
    global latest_message
    while latest_message is None:
        time.sleep(1)
    return latest_message

def read_config():
    return {
        'bootstrap.servers': 'pkc-12576z.us-west2.gcp.confluent.cloud:9092',
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': '',
        'sasl.password': ''
    }

def produce(topic, config):
    producer = Producer(config)

    key = "engine_data"
    value = get_latest_message()
    producer.produce(topic, key=key, value=value)
    print(f"Produced message to topic {topic}: key = {key:12} value = {value:12}")
    producer.flush()

def main():
    # Start the MQTT client in a separate thread
    mqtt_thread = threading.Thread(target=mqtt_client_thread)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    config = read_config()
    topic = "maintenance"
    while True:
        try:
            produce(topic, config)
            time.sleep(60)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()