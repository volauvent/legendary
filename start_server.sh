#!/bin/sh

export FLASK_APP=./frontend/view.py
PYTHONPATH=./ python3 server/dbServer.py 
