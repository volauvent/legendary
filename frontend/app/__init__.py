from flask import Flask
from flask_bootstrap import Bootstrap
import os
import sys

sys.path.append(os.path.abspath('./'))
from server.baseClient import dbClient

app = Flask(__name__)

# app.config.from_object('config')

client = dbClient()
Bootstrap(app)

UPLOAD_FOLDER = os.path.abspath('.') + '/frontend/upload'
REQUEST_FOLDER = '/static/reqImg'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REQUEST_FOLDER'] = REQUEST_FOLDER

from frontend.app import views, models
