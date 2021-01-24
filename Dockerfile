FROM python:3.8

WORKDIR /home

ENV TELEGRAM_TOKEN=""

ENV TZ=""
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install -U pip python-telegram-bot && apt-get update && apt-get install sqlite3
COPY *.py ./
COPY createdb.sql ./

ENTRYPOINT ["python", "server.py"]
