import json
import os
import pika
import string
import random


# Generate random content for messages
def generate_random_id(n):
    characters = list(string.ascii_letters + string.digits + "") # characters set
    random.shuffle(characters) # shuffle characters
    ID = [random.choice(characters) for i in range(n)] # pick random n characters
    random.shuffle(ID) # shuffle the password
    return "".join(ID) # convert to string and return


# Connect to RabbitMQ
username = os.environ.get("RABBITMQ_USERNAME")
password = os.environ.get("RABBITMQ_PASSWORD")
host = os.environ.get("RABBITMQ_HOST")
credentials = pika.PlainCredentials(username=username, password=password)
parameters = pika.ConnectionParameters(host, credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Publish push notification requests to RabbitMQ
queue = "notification.fcm"
channel.queue_declare(queue=queue, durable=True)

for i in range(100):
    msg = {
    "identifier": "fcm-msg-"+generate_random_id(9),
    "type": "device",
    "deviceId": generate_random_id(32),
    "text": "Notification message",
    }
    # Simulate random errors
    if generate_random_id(1) in string.digits:
        msg["type"] = 404
    if generate_random_id(1) in string.digits:
        del msg["type"]
    channel.basic_publish(exchange='', routing_key=queue,
                       body=json.dumps(msg), properties=pika.BasicProperties(delivery_mode=2))
    print("Push notification requests sent")


# Consume the notification.done topic from RabbitMQ
def receive_msg(channel, method, properties, body):
    channel.basic_ack(delivery_tag=method.delivery_tag)
    print(json.loads(body))


queue = "done"
exchange = "notification"
routing_key = "notification.done"

channel.queue_declare(queue=queue, durable=True)
channel.exchange_declare(exchange=exchange, exchange_type='topic', durable=True)
channel.queue_bind(queue=queue, exchange=exchange, routing_key=routing_key)
channel.basic_consume(queue=queue, on_message_callback=receive_msg)

# Start consuming
print("Producer: Start consuming")
channel.start_consuming()