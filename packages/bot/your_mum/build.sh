#!/bin/bash

set -e

virtualenv --without-pip virtualenv

# Uncomment if you're using the Python 3.9 runtime
pip install -r requirements.txt --target virtualenv/lib/python3.9/site-packages

# Uncomment if you're using the Python 3.11 runtime
# pip install -r requirements.txt --target virtualenv/lib/python3.11/site-packages
