FROM python:3.8-slim-buster

# install make
RUN apt-get update && apt-get install make

# build app
WORKDIR /app

COPY prod_requirements.txt build.py build_Makefile ./

RUN make -f build_Makefile setup NO_VENV=True DEV=False

COPY . .

CMD [ "python3", "-u", "-m", "src.main" ]