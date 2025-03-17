from kafka import KafkaProducer
import json
import time
import random


producer = KafkaProducer(
    bootstrap_servers=['IP Address'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    api_version=(0, 10, 1)
)


def generate_random_data():
    return {
        'engine_rpm': random.randint(800, 6000),
        'lub_oil_pressure': random.uniform(20.0, 80.0), 
        'fuel_pressure': random.uniform(30.0, 70.0),
        'coolant_pressure': random.uniform(15.0, 50.0),  
        'lub_oil_temp': random.uniform(30.0, 120.0),  
        'coolant_temp': random.uniform(30.0, 100.0), 
        'temp_difference': random.uniform(-10.0, 10.0),
        'timestamp': time.time()  
    }

# Function to send data to Kafka
def send_data():
    data = generate_random_data()
    producer.send('streamingsrc', value=data)
    print(f"Sent data: {data}")

# Send data every 30 seconds
while True:
    send_data()
    time.sleep(30)