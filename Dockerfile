FROM python:3.8-slim-buster

# install java
# ref: https://stackoverflow.com/questions/61815233/install-java-runtime-in-debian-based-docker-image
RUN mkdir -p /usr/share/man/man1 /usr/share/man/man2
RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-11-jre-headless

# install make
RUN apt-get update && apt-get install make

# build app
WORKDIR /app
COPY . .

RUN make setup NO_VENV=True DEV=False

CMD [ "python3", "-u", "-m", "src.main" ]