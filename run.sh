#!/bin/sh

export FLASK_APP=Server/__init__.py
pip install --upgrade -e .
flask run
