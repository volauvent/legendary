from flask import Flask
from flask_bootstrap import Bootstrap
import os
import sys

sys.path.append(os.path.abspath('./'))

app = Flask(__name__)

# app.config.from_object('config')

Bootstrap(app)

UPLOAD_FOLDER = os.path.abspath('.') + '/frontend/upload'
REQUEST_FOLDER = '/static/reqImg'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REQUEST_FOLDER'] = REQUEST_FOLDER

from frontend.app import views, models
