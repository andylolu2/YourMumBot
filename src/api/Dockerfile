FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

WORKDIR /app

COPY ./api/requirements.txt ./api/build.py ./

RUN pip install -r requirements.txt && python build.py

COPY ./helper ./helper

COPY ./api ./api
