from flask import jsonify, render_template, session, url_for, request, g, abort
from app import app, db
import json
from sqlalchemy import and_
import os
import socket
import pickle
import numpy as np
import random
from werkzeug import secure_filename


ALLOWED_EXTENSIONS=set(['png', 'jpg', 'jpeg', 'gif'])


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/')
@app.route('/labelling')
def labelling():
    return render_template('labelling.html', title='Labelling')


def allowedFile(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS


@app.route('/imgClassify', methods=['POST', 'GET'])
def imgClassify():
    if request.method == 'POST':
        # take the upload picture as an input
        # carry out emotion classification
        # return emotion category

        if 'image-up' not in request.files:  # no image
            print("no image!")
            return jsonify(message='Network problem, no image...')

        fileMeta = request.files["image-up"]
        # print(fileMeta)
        filename = fileMeta.filename
        # print(filename)
        if fileMeta and allowedFile(filename):
            filename = secure_filename(filename)
            # print("")
            # print(filename)
            # print(app.config['UPLOAD_FOLDER'])
            # print("")
            fileMeta.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("saved!")

            ################
            # add prediction logic
            ################

            return jsonify(message='success', predictResult='guess what? hahaha')
        else:
            print("File format error!")
            return jsonify(message='File format error!')

    else:
        # take the choosen emotion category as an input
        # return example picture of this emotion
        return


@app.route('/imageLable', methods=['POST', 'GET'])
def imageLable():
    if request.mothod == 'POST':
        # add a new label of given picture into the database
        return
    else:
        # send back un-labeled/week-labeled picture
        # as well as the week-labeled
        return
