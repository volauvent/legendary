from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
import os

app = Flask(__name__)

app.config.from_object('config')
#db = SQLAlchemy(app)
Bootstrap(app)

UPLOAD_FOLDER = os.path.abspath('.') + '/upload'
REQUEST_FOLDER = '/static/reqImg'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REQUEST_FOLDER'] = REQUEST_FOLDER

from app import views, models
