import sys
import pickle
import os
import numpy as np

sys.path.append("./")
from train.model import pretrained_ft, pretrained_fixed, base_model, small_CNN
from train.preprocess import preprocess
from train.utils import topk_acc
from keras.utils.vis_utils import plot_model
from keras import applications
from keras.models import load_model
from keras.utils.np_utils import to_categorical

job = sys.argv[1]

if job == "ontrain_small":
    """
    Example for online training
    """
    model = small_CNN()
    model.summary()
    data_src = preprocess()
    for X, y in data_src.online_read(128):
        model.train_on_batch(X, y)
        print(model._model.test_on_batch(X, y))

elif job == "ontrain_big":
    """
    Example for online training
    """
    model = pretrained_ft()
    model.summary()
    data_src = preprocess()
    for X, y in data_src.online_read(128):
        model.train_on_batch(X, y)
        print(model._model.test_on_batch(X, y))


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
    weight = [np.sum(trainy == i) for i in range(len(class_names))]
    weight = {i: np.min(weight)*1.0/weight[i] for i in range(len(class_names))}
    # weight = {}
    model.fit(len(class_names), trainX, trainy, valX, valy,  np_epoch=8, class_weight=weight)
    model.save("train/local/model.h5")
    model.conf_mat(valX, valy, class_names)

    predicted_score = model.predict(valX)
    print("Overall classificaiton rate: {}".format(topk_acc(predicted_score, valy, 1)))
    print("Top 2 classificaiton rate: {}".format(topk_acc(predicted_score, valy, 2)))
    print("Top 3 classificaiton rate: {}".format(topk_acc(predicted_score, valy, 3)))

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

elif job == "plot":
    model1 = applications.ResNet50(weights='imagenet', include_top=True)
    model1.layers.pop()
    plot_model(model1, to_file='train/local/model1.png')

    model2 = load_model('train/local/model.h5')
    plot_model(model2, to_file='train/local/model2.png')

elif job == "legendary":
    datapath = "train/local/legendary/images/"
    processor = preprocess("resnet")

    valX, valy, label_names = processor.offline_read(datapath=datapath, savefile=None)
    model = base_model()
    model.load('train/local/model.h5')
    predicted_score = model.predict(valX)

    print("Overall classificaiton rate: {}".format(topk_acc(predicted_score, valy, 1)))
    print("Top 2 classificaiton rate: {}".format(topk_acc(predicted_score, valy, 2)))
    print("Top 3 classificaiton rate: {}".format(topk_acc(predicted_score, valy, 3)))

    model.conf_mat(valX, valy, label_names, savefile="train/legendary_confusion.png")

elif job == "random":
    train_prop = 0.7
    with open("train/local/data.pkl", 'rb') as f:
        dat = pickle.load(f, encoding='latin1')
    X, y, class_names = dat
    sample_num = X.shape[0]
    train_num = int(sample_num * train_prop)
    valX = X[train_num:, :]
    trainy = y[:train_num]
    valy = y[train_num:]

    p = [np.sum(trainy == i)/train_num for i in range(len(class_names))]
    predicted_score = np.random.randn(valX.shape[0], 8)
    print("Random Prediction without Reweighting (baseline)")
    print("  validation set")
    print("    Overall classificaiton rate: {}".format(topk_acc(predicted_score, valy, 1)))
    print("    Top 2 classificaiton rate: {}".format(topk_acc(predicted_score, valy, 2)))
    print("    Top 3 classificaiton rate: {}".format(topk_acc(predicted_score, valy, 3)))
    predicted_score = np.random.multinomial(10, p, valX.shape[0])
    print("Random Prediction with Reweighting (baseline)")
    print("  validation set")
    print("    Overall classificaiton rate: {}".format(topk_acc(predicted_score, valy, 1)))
    print("    Top 2 classificaiton rate: {}".format(topk_acc(predicted_score, valy, 2)))
    print("    Top 3 classificaiton rate: {}".format(topk_acc(predicted_score, valy, 3)))

    datapath = "train/local/legendary/images/"
    processor = preprocess("resnet")
    valX, valy, label_names = processor.offline_read(datapath=datapath, savefile=None)
    predicted_score = np.random.randn(valX.shape[0], 8)
    print("Random Prediction without Reweighting (baseline)")
    print("  legendary test set")
    print("    Overall classificaiton rate: {}".format(topk_acc(predicted_score, valy, 1)))
    print("    Top 2 classificaiton rate: {}".format(topk_acc(predicted_score, valy, 2)))
    print("    Top 3 classificaiton rate: {}".format(topk_acc(predicted_score, valy, 3)))
    predicted_score = np.random.multinomial(10, p, valX.shape[0])
    print("Random Prediction with Reweighting (baseline)")
    print("  legendary test set")
    print("    Overall classificaiton rate: {}".format(topk_acc(predicted_score, valy, 1)))
    print("    Top 2 classificaiton rate: {}".format(topk_acc(predicted_score, valy, 2)))
    print("    Top 3 classificaiton rate: {}".format(topk_acc(predicted_score, valy, 3)))
else:
    raise ValueError("argument should be: ontrain_small, ontrain_big, offtrain, predict, legendary, random")