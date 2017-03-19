#!/bin/sh

export FLASK_APP=./frontend/view.py
PYTHONPATH=./ python3 server/dbServer.py 50000 &
PYTHONPATH=./ python3 -m frontend.view
flask run
