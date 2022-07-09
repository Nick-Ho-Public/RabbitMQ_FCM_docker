FROM python:3.7-alpine

RUN apk add --no-cache \
    build-base \
    libressl-dev \
    musl-dev \
    libffi-dev
RUN pip install cryptography
RUN pip install pika
RUN pip install pymysql
RUN pip install requests

# Python output can be sent straight to terminal (container log)
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app/consumer
COPY consumer.py .
CMD [ "python", "consumer.py" ]
