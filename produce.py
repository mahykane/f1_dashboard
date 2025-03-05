import pika
import requests
import json
import time

# Setup RabbitMQ Connection
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='telemetry_data')
channel.queue_declare(queue='lap_data')

def fetch_car_data(driver_number):
    url = f'https://api.openf1.org/v1/car_data?session_key=latest&driver_number={driver_number}'
    response = requests.get(url)
    return response.json() if response.status_code == 200 else []

def fetch_lap_data(driver_number):
    url = f'https://api.openf1.org/v1/laps?session_key=latest&driver_number={driver_number}'
    response = requests.get(url)
    return response.json() if response.status_code == 200 else []

# Define multiple drivers for live comparison
drivers = [44, 1, 16]  # Example: Hamilton, Verstappen, Leclerc

while True:
    for driver_number in drivers:
        telemetry_data = fetch_car_data(driver_number)
        lap_data = fetch_lap_data(driver_number)

        if telemetry_data:
            for entry in telemetry_data:
                entry["driver_number"] = driver_number
                message = json.dumps(entry)
                channel.basic_publish(exchange='', routing_key='telemetry_data', body=message)

        if lap_data:
            for entry in lap_data:
                entry["driver_number"] = driver_number
                message = json.dumps(entry)
                channel.basic_publish(exchange='', routing_key='lap_data', body=message)

    time.sleep(5)  # Fetch updates every 2 seconds

connection.close()