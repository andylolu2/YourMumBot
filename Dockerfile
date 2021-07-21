FROM adoptopenjdk/openjdk14:jre-14.0.1_7-alpine

COPY --from=python:3.8-slim-buster / /

# install make
RUN apt-get update && apt-get install make

# build app
WORKDIR /app
COPY . .

RUN make setup NO_VENV=True DEV=False

CMD [ "python3", "-u", "-m", "src.main" ]