import sys
import pickle
import os
import numpy as np

sys.path.append("./")
from train.model import pretrained_ft, pretrained_fixed, base_model
from train.preprocess import preprocess

job = sys.argv[1]

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
    with open("train/local/data.pkl", 'rb') as f:
        dat = pickle.load(f, encoding='latin1')
    X, y, class_names = dat
    sample_num = X.shape[0]
    train_num = int(sample_num*train_prop)
    trainX = X[:train_num, :]
    trainy = y[:train_num]
    valX = X[train_num:, :]
    valy = y[train_num:]
    model.fit(len(class_names), trainX, trainy, valX, valy, np_epoch=8)
    model.save("train/local/model.h5")
    model.conf_mat(valX, valy, class_names)

elif job == "predict":
    """
    Example for predicting
    """
    imgfile = "train/local/images/contentment/0dc2862cfc9711e2a73722000a1f9317_7.jpg"
    class_names = os.listdir("train/local/images")
    processor = preprocess("resnet")
    model = base_model()
    model.load('train/local/model.h5')
    model.summary()
    X = processor.processRaw(imgfile)
    predicted_score = model.predict(X)[0]
    snl = [(predicted_score[i], class_names[i]) for i in range(8)]
    snl.sort(key=lambda x:x[0], reverse=True)
    print(snl)
    print(snl[0][1])

else:
    raise ValueError("argument should be: ontrain, offtrain, predict")