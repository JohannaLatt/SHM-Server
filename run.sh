#!/bin/sh

pip install --upgrade -e .

cd Server
export FLASK_APP=__init__.py
export PYTHONDONTWRITEBYTECODE=yes
flask run
