import time
import json
import random
import paho.mqtt.client as mqtt

MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'maintainence'

# Function to generate random data
def generate_random_data():
    data = {
        # add to choose vehicle name random within mercerdessclass and bmwm2 
        'vehicle_name': random.choice(['mercedessclass', 'bmwm2']),
        'engine_rpm': random.randint(1000, 4000),
        'lub_oil_pressure': random.uniform(1.0, 5.0),
        'fuel_pressure': random.uniform(1.0, 5.0),
        'coolant_pressure': random.uniform(1.0, 5.0),
        'lub_oil_temp': random.uniform(60.0, 120.0),
        'coolant_temp': random.uniform(60.0, 120.0),
        'temp_difference': random.uniform(0.0, 60.0)
    }
    return data

# Function to publish data to MQTT topic every 60 seconds
def publish_data():
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set('isaac', 'isaac')
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()

    try:
        while True:
            data = generate_random_data()
            mqtt_client.publish(MQTT_TOPIC, json.dumps(data))
            print(f"Published data: {data}")
            time.sleep(20)
    except KeyboardInterrupt:
        pass
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

if __name__ == "__main__":
    publish_data()
