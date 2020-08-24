#!/bin/bash

# cd to current directory
cd "$(dirname "$0")"

# delete migration history
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete

# pip install
pip3 install -r requirements.txt

# make db schema
python3 manage.py makemigrations
python3 manage.py migrate

# create super user
python3 manage.py createsuperuser