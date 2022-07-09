# Descriptions

A docker container including below services: 

* RabbitMQ: A middleware to handle the message queue for producer and consumer
* Firebase: Assuming a correct config, should deliver messages to mobile devices (out-of-scope)
* Producer:
*	Publish 100 push notification requests to "notification.fcm" queue
*	Wait and consume "notification.done" topic published by consumer 
* Consumer:
*	Consume push notification requests from "notification.fcm" queue
*	Send requests to Firebase (Needs Firebase project ID and token)
*	Publish "notification.done" topic to done "queue" through "notification" exchange
* MySQL: Record all the status of FCM delivery
* phpMyAdmin: MySQL WEB access

* Total no. of push notification requests (100) = 
* no. of UNACK messages in RabbitMQ + Rows in fcm_job + Rows in fcm_job_failed

## Requirements

* OS (tested in Windows 10)
* Docker 19.03.0+ (tested in 20.10.14)
* Docker Compose 1.27.1+ (tested in 2.5.1)

## Images

* Compose file format 3.9
* MySQL 8.0.28
* phpMyAdmin 5
* RabbitMQ 3.10-management-alpine
* Python 3.7-alpine

## Run the program

* Run `docker-compose up`

* RabbitMQ dashboard can be accessed by http://localhost:15672/ with [Username/Password] as [root/root]
* Queue:
*	notification.fcm
*	done
* Exchange: notification
* Routing key: notification.done

* phpMyAdmin can be accessed by http://localhost:8080/ with [Username/Password] as [user/password]
* Tables:
*	FCM_job
*	FCM_job_failed