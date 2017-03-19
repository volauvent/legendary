from flask import jsonify, render_template, session, url_for, request, g, abort
from app import app#, db
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
    # if request.method == 'GET':
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
        filename = fileMeta.filename
        if fileMeta and allowedFile(filename):
            filename = secure_filename(filename)
            
            fileMeta.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            emotionCategory = 'guess what?'

            ################
            # add prediction logic
            ################
            # -->call Classification Model get EMOTION_CATEGORY
            # -->call DB Model store image

            # image store folder path: UPLOAD_FOLDER in __init__.py
            # predict result: emotionCategory(string)

            
            return jsonify(message='success', predictResult=emotionCategory)
        else:
            print("File format error!")
            return jsonify(message='File format error!')
    else:
        # take the choosen emotion category as an input
        # return example picture of this emotion
        return


@app.route('/imageLable', methods=['POST', 'GET'])
def imageLable():
    if request.method == 'POST':
        # add a new label of given picture into the database
        newLable = request.form.getlist("label[]")
        if len(newLable) > 0:
            #print("New label: ", newLable)
            ################
            # add store new label logic
            ################
            # newLable = ['NEW_EMOTION']

            return jsonify(message='success')
        else:
            return jsonify(message='empty')
    else:
        # send back un-labeled/week-labeled picture
        # as well as the week-labeled

        imageName = random.randint(0, 4)
        reqImage = app.config['REQUEST_FOLDER'] + "/" + str(imageName) + ".jpg"
        weekLabel = ['awe', 'contentment', 'anger']
        ################
        # add request image and label logic
        ################
        # -->call DB server get img file path and weeklabel

        return jsonify(img=reqImage, label=weekLabel)
