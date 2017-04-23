from flask import jsonify, render_template, session, url_for, request, g, abort
from app import app#, db
import json
import os
import shutil
import socket
import pickle
import numpy as np
import random
from werkzeug import secure_filename
from server.baseClient import dbClient

client = dbClient()

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'PNG', 'JPG', 'JPEG', 'GIF'])
EMOTIONS = ['amusement', 'awe', 'contentment', 'anger', 'disgust', 'excitement', 'fear', 'sadness']
EMOTIONSLABELS = {'amusement': 1, 'awe': 2, 'contentment': 3, 'anger': 4, 'disgust': 5, 'excitement': 6, 'fear': 7, 'sadness': 8}

DATABASE_IMAGE_PATH = os.path.abspath('./') + "/server/data/images/other/"
WEB_IMAGE_PATH = os.path.abspath('.') + "/frontend/app/static/reqImg/"

WEB_UPLOAD_PATH = os.path.abspath('.') + "/frontend/upload/"
DATABASE_INSERT_PATH = os.path.abspath('.') + "/server/"

def moveImge(imgName, originPath, desPath):
    # print(originPath + imgName)
    # print(desPath)
    shutil.copy(originPath + imgName, desPath)
    return


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/')
@app.route('/predict')
def predict():
    # if request.method == 'GET':
    return render_template('predict.html', title='predict')


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

        # TODO:
        # too complicated, need to be simplified
        fileMeta = request.files["image-up"]
        filename = fileMeta.filename
        if fileMeta and allowedFile(filename):
            filename = secure_filename(filename)
            # fake Data test:
            # fileMeta.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # emotionCategory = 'guess what?'
            # print("")
            # print(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # print("")

            fileMeta.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            #moveImge(filename, WEB_UPLOAD_PATH, DATABASE_INSERT_PATH)

            # client.insertImage(filename)

            emotionCategory = client.predict_and_insert(filename)
            emotionCategory.sort(key=lambda x: -x[0])

            ################
            # add prediction logic
            ################
            # -->call Classification Model get EMOTION_CATEGORY
            # -->call DB Model store image

            # image store folder path: UPLOAD_FOLDER in __init__.py
            # predict result: emotionCategory(string)

            return jsonify(message='success', predictResult=emotionCategory[0][1])
        else:
            print("File format error!")
            return jsonify(message='File format error!')
    else:
        # take the choosen emotion category as an input
        # return example picture of this emotion
        return

# IMGID = ""

@app.route('/imageLable', methods=['POST', 'GET'])
def imageLable():

    if request.method == 'POST':
        # add a new label of given picture into the database
        newLable = request.form.getlist("label[]")
        targetImgID = request.form.get("imgId")
        # print("New label: ", newLable)
        # print("targetImgID: ", targetImgID)

        if targetImgID == "EMPTY":
            return jsonify(message='noImg')

        if len(newLable) > 0:
            # print("New label: ", newLable)
            ################
            # add store new label logic
            ################
            # newLable = ['NEW_EMOTION']
            # TODO:
            # too complicated, need to be simplified

            emotion = newLable[0]
            client.insertModelLabel(targetImgID, EMOTIONSLABELS[emotion])
            # print(emotion)
            # print(EMOTIONSLABELS[emotion])
            return jsonify(message='success')

        else:
            return jsonify(message='empty')
    else:
        # send back un-labeled/week-labeled picture
        # as well as the week-labeled

        # fake Data test:
        # imageName = random.randint(0, 4)
        # reqImage = app.config['REQUEST_FOLDER'] + "/" + str(imageName) + ".jpg"
        # weekLabel = ['awe', 'contentment', 'anger']

        ################
        # add request image and label logic
        ################
        # -->call DB server get img file path and weeklabel

        # TODO:
        # too complicated, need to be simplified

        imgData = client.getRandomImageWithWeakLabel()
        # print("==========start printing important !!!!!!!!!!============")
        # print(imgData)
        # print("==========end printing important !!!!!!!!!!============")

        imgPath = imgData['path']
        imgName = imgPath.split('/')[-1]
        print(imgName)

        moveImge(imgName, DATABASE_IMAGE_PATH, WEB_IMAGE_PATH)
        reqImage = app.config['REQUEST_FOLDER'] + "/" + imgName

        weekLabelNum = imgData['labels']
        imgID = imgData['id']
        # IMGID = imgID
        weekLabel = []
        for i in range(len(weekLabelNum)):
            weekLabel.append(EMOTIONS[weekLabelNum[i] - 1])
        print(weekLabel)
        # print(imgPath)
        return jsonify(img=reqImage, label=weekLabel, id=imgID)

# print("test: ")
# print(client.getRandomImageWithWeakLabel())
# print("Finish test.")