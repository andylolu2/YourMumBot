#!/bin/bash

set -e

virtualenv virtualenv
source virtualenv/bin/activate
pip install -r requirements.txt
deactivate

cp -r ../../../lib lib
