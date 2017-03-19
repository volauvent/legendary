from flask import Flask
from flask_bootstrap import Bootstrap
import os
import sys

sys.path.append(os.path.abspath('../'))
from server.baseClient import dbClient



app = Flask(__name__)
app.config.from_object('config')
client = dbClient()
Bootstrap(app)


UPLOAD_FOLDER = os.path.abspath('.') + '/upload'
REQUEST_FOLDER = '/static/reqImg'
# REQUEST_FOLDER = '/server/data/images/other/2be81673893dc596.jpg'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REQUEST_FOLDER'] = REQUEST_FOLDER

from app import views, models
