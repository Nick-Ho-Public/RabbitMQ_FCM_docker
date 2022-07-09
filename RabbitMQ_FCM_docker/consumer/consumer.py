import datetime
import json
import os
import pika
import pymysql
import string
import requests
import time

# Connect to MySQL
db_settings = {
    "host": os.environ.get("MYSQL_HOST"),
    "port": int(os.environ.get("MYSQL_PORT")),
    "user": os.environ.get("MYSQL_USER"),
    "password": os.environ.get("MYSQL_PASSWORD"),
    "db": os.environ.get("MYSQL_DATABASE"),
}
try:
    conn = pymysql.connect(**db_settings)
    cursor = conn.cursor()
    # Create the tables if needed
    cursor.execute("CREATE TABLE IF NOT EXISTS fcm_job (id INT AUTO_INCREMENT PRIMARY KEY, identifier VARCHAR(255), deliverAt DATETIME)")
    cursor.execute("CREATE TABLE IF NOT EXISTS fcm_job_failed (id INT AUTO_INCREMENT PRIMARY KEY, identifier VARCHAR(255), deliverAt DATETIME)")
    conn.commit()
except Exception as e:
    print(e)


# Callback function for notification.fcm messages
# Send push notification requests to Firebase after validation and ACK
# Publish notification.done after received response 200 from Firebase
def receive_msg(channel, method, properties, body):
    # Validation
    try:
        msg = json.loads(body)
        # Type validation
        if not all(isinstance(value, str) for value in msg.values()):
            raise TypeError("All values must be string", msg)
        # Key validation
        msg_id = msg["identifier"]
        msg_type = msg["type"]
        msg_deviceId = msg["deviceId"]
        msg_text = msg["text"]
        validated = True
    except KeyError as e:
        print('KeyError:', e)
        validated = False
    except TypeError as e:
        print('TypeError:', e)
        validated = False
    
    # Return without ACK if not validated
    if not validated:
        print('failed to consume message:', body)
        return

    # ACK after validation and decoding
    channel.basic_ack(delivery_tag=method.delivery_tag)
    
    # Send FCM message to Firebase(TODO)
    
    # FCM settings (TODO)
    # Assuming the firebase configuration is setup correctly
    project_id = "TODO"
    FCM_token = "TODO"
    
    # Create FCM message
    FCM_msg = {
        "message": {
            "token": FCM_token,
            "data": {
                "body": msg_text,
                "title": "Incoming message"
            }
        }
    }
    
    # Firebase url
    url = "https://fcm.googleapis.com/v1/projects/"+project_id+"/messages:send"
    try:
        response = requests.post(url, json=FCM_msg)
        # Record the time
        deliver_at = datetime.datetime.now()
        
        # Simulate the response status (TODO)
        response = not msg_id[-1] in string.digits # true if last char is not digit
        if response:
            # Insert successful job status to fcm_job table
            command = "INSERT INTO fcm_job (identifier, deliverAt) VALUES (%s, %s)"
            cursor.execute(command, (msg_id, deliver_at.strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()

            # Publish the topic ("notification.done")
            routing_key = "notification.done"
            msg = {
                "identifier": msg_id,
                "deliverAt": deliver_at.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            channel.basic_publish(exchange='notification', routing_key=routing_key,
                           body=json.dumps(msg), properties=pika.BasicProperties(delivery_mode=2))
        else:
            # Insert failed job status to fcm_job_failed table
            command = "INSERT INTO fcm_job_failed (identifier, deliverAt) VALUES (%s, %s)"
            cursor.execute(command, (msg_id, deliver_at.strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
    except Exception as e:
        print(e)

    
# Connect to RabbitMQ
username = os.environ.get("RABBITMQ_USERNAME")
password = os.environ.get("RABBITMQ_PASSWORD")
host = os.environ.get("RABBITMQ_HOST")
credentials = pika.PlainCredentials(username=username, password=password)
parameters = pika.ConnectionParameters(host, credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Declare exchange for publishing notification.done
channel.exchange_declare(exchange='notification', exchange_type='topic', durable=True)

# Consume the notification.fcm message from RabbitMQ
queue = "notification.fcm"
channel.queue_declare(queue=queue, durable=True)
channel.basic_consume(queue=queue,
                   on_message_callback=receive_msg)
print("Consumer: Start consuming")
channel.start_consuming()
