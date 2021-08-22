FROM python:3.9.6-slim-buster

WORKDIR /app

COPY ./bot/requirements.txt ./

RUN pip install -r requirements.txt

COPY ./helper ./helper

COPY ./bot ./bot

CMD ["python", "-m", "bot.main"]
