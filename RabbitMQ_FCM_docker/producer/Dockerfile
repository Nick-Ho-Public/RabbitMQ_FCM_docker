FROM python:3.7-alpine

RUN pip install pika

# Python output can be sent straight to terminal (container log)
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app/producer
COPY producer.py .
CMD [ "python", "producer.py" ]
