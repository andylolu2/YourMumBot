FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim

WORKDIR /app

COPY ./api/requirements.torch.txt ./api/requirements.txt ./api/build.py ./

RUN pip install -r requirements.torch.txt && \
    pip install -r requirements.txt && \
    python build.py

COPY ./helper ./helper

COPY ./api ./api
