from flask import jsonify, render_template, session, url_for, request, g, abort
from app import app, db
import json
from sqlalchemy import and_
import os
import socket
import pickle
import numpy as np
import random


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/')
@app.route('/labelling')
def labelling():
    return render_template('labelling.html', title='Labelling')


@app.route('/imageLable', methods=['POST', 'GET'])
def imageLable():
    if request.mothod == 'POST':
        # add a new label of given picture into the database
        return
    else:
        # send back un-labeled/week-labeled picture
        # as well as the week-labeled
        return


@app.route('/imgClassify', methods=['POST', 'GET'])
def imgClassify():
    if request.method == 'POST':
        # take the upload picture as an input
        # carry out emotion classification
        # return emotion category
        return
    else:
        # take the choosen emotion category as an input
        # return example picture of this emotion
        return
