from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
import os

app = Flask(__name__)

app.config.from_object('config')
db = SQLAlchemy(app)
Bootstrap(app)

UPLOAD_FOLDER = os.path.abspath('.') + '/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from app import views, models
