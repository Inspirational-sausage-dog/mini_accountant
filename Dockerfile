FROM python:3.8

WORKDIR /home

ENV TELEGRAM_TOKEN="1441859100:AAHC0wuFqFka4f73lqRAAe9NkmRk8DYUPng"

RUN pip install -U pip python-telegram-bot && apt-get update && apt-get install sqlite3
COPY *.py ./
COPY createdb.sql ./

ENTRYPOINT ["python", "server.py"]
