import sys
import pickle
import numpy as np

sys.path.append("../")
from train.model import pretrained_ft, pretrained_fixed
from train.preprocess import preprocess

"""
Example for online training
model = pretrained_ft()
data_src = preprocess()
for X, y in data_src.read(128):
    model.train_on_batch(X, y)
"""


"""
Example for offline training
"""
train_prop = 0.7
model = pretrained_fixed()
with open("local/data.pkl", 'rb') as f:
    dat = pickle.load(f)
X, y, class_names = dat
sample_num = X.shape[0]
train_num = int(sample_num*train_prop)
trainX = X[:train_num, :]
trainy = y[:train_num]
valX = X[train_num:, :]
valy = y[train_num:]
model.fit(trainX, trainy, valX, valy, np_epoch=10)
model.save("model.h5")
model.conf_mat(valX, valy, class_names)
