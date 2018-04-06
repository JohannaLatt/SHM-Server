#!/bin/sh

pip install --upgrade -e .

cd Server
export FLASK_APP=__init__.py
flask run
