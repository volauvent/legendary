import sys
import pickle
import os
import numpy as np

sys.path.append("../")
from train.model import pretrained_ft, pretrained_fixed, base_model
from train.preprocess import preprocess

job = "predict"

if job == "ontrain":
    """
    Example for online training
    """
    model = pretrained_ft()
    data_src = preprocess()
    for X, y in data_src.read(128):
        model.train_on_batch(X, y)


elif job == "offtrain":
    """
    Example for offline training
    """
    train_prop = 0.7
    model = pretrained_fixed()
    with open("data.pkl", 'rb') as f:
        dat = pickle.load(f)
    X, y, class_names = dat
    sample_num = X.shape[0]
    train_num = int(sample_num*train_prop)
    trainX = X[:train_num, :]
    trainy = y[:train_num]
    valX = X[train_num:, :]
    valy = y[train_num:]
    model.fit(len(class_names), trainX, trainy, valX, valy, np_epoch=25)
    model.save("model.h5")
    model.conf_mat(valX, valy, class_names)

elif job == "predict":
    """
    Example for predicting
    """
    imgfile = "images/contentment/0dc2862cfc9711e2a73722000a1f9317_7.jpg"
    class_names = os.listdir("images")
    processor = preprocess("resnet")
    model = base_model()
    model.load('model.h5')
    model.summary()
    X = processor.processRaw(imgfile)
    predicted_label = class_names[model.predict_classes(X)[0]]
    print(predicted_label)