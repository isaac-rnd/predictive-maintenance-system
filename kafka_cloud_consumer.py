import threading
from confluent_kafka import Consumer
import json
import predict_for_data

# Global variable to store the latest message
latest_message = None

def read_config():
    return {
        'bootstrap.servers': 'pkc-12576z.us-west2.gcp.confluent.cloud:9092',
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': '',
        'sasl.password': '',
        'group.id': 'python-group-1',
        'auto.offset.reset': 'latest',
        'enable.auto.commit': True  # Enable automatic offset commits
    }

def kafka_consumer_thread(topic, config):
    global latest_message
    consumer = Consumer(config)
    consumer.subscribe([topic])

    try:
        while True:
            msg = consumer.poll(10.0)
            if msg is not None and msg.error() is None:
                value = msg.value().decode("utf-8")
                latest_message = value
                print(f"Consumed message from Cloud Kafka topic {topic}: {value}")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

def start_kafka_consumer(topic, config):
    thread = threading.Thread(target=kafka_consumer_thread, args=(topic, config))
    thread.daemon = True
    thread.start()

def get_latest_message():
    global latest_message
    return latest_message

def predictForThis(data):
    try:
        data_dict = json.loads(data)
        engine_rpm = data_dict.get('engine_rpm', None)
        lub_oil_pressure = data_dict.get('lub_oil_pressure', None)
        fuel_pressure = data_dict.get('fuel_pressure', None)
        coolant_pressure = data_dict.get('coolant_pressure', None)
        lub_oil_temp = data_dict.get('lub_oil_temp', None)
        coolant_temp = data_dict.get('coolant_temp', None)
        temp_difference = data_dict.get('temp_difference', None)
        
        if None in [engine_rpm, lub_oil_pressure, fuel_pressure, coolant_pressure, lub_oil_temp, coolant_temp, temp_difference]:
            raise ValueError("Missing or invalid data fields")

        result, confidence = predict_for_data.predict_condition(
            engine_rpm, lub_oil_pressure, fuel_pressure, coolant_pressure,
            lub_oil_temp, coolant_temp, temp_difference
        )
        print("Result: ", result)
        print("Confidence: ", confidence)
        return result, confidence

    except json.JSONDecodeError:
        print("Error decoding JSON data")
    except ValueError as ve:
        print(f"ValueError: {ve}")
    except Exception as e:
        print(f"Unexpected error: {e}")
