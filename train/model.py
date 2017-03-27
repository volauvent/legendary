import matplotlib.pyplot as plt
from keras import applications
from keras.layers import Dense, Activation, Dropout, Flatten
from keras.models import Sequential, load_model, Model
from keras.optimizers import SGD
from keras.utils.np_utils import to_categorical
from sklearn.metrics import confusion_matrix

import sys
sys.path.append("./")
from train.utils import plot_confusion_matrix

class base_model(object):
    """
    Base class for models
    """

    def __init__(self, opt="adam"):
        self._model = None
        if opt == "sgd":
            self._opt = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
        else:
            self._opt = opt

    def fit(self, num_classes, train_X, train_y, val_X=None, val_y=None, np_epoch=30):
        self._model.fit(train_X, to_categorical(train_y, num_classes),
                        nb_epoch=np_epoch,
                        validation_data=(val_X, to_categorical(val_y, num_classes)))

    def train_on_batch(self, X, y):
        print(X.shape, y.shape)
        self._model.train_on_batch(X, y)

    def predict(self, X):
        return self._model.predict(X)

    def predict_classes(self, X):
        return self._model.predict_classes(X)

    def conf_mat(self, X, y, class_names, savefile="confusion_matrix.png"):
        predicted_label = self._model.predict_classes(X)
        cnf_matrix = confusion_matrix(y, predicted_label)
        plt.figure()
        plot_confusion_matrix(cnf_matrix, classes=class_names, normalize=True,
                              title='Normalized confusion matrix')
        plt.savefig(savefile)

    def save(self, filename):
        self._model.save(filename)

    def load(self, filename):
        self._model = load_model(filename)

    def summary(self):
        self._model.summary()


class pretrained_fixed(base_model):
    """
    A model that combines a pre-trained ImageNet model with
    simple fully connected layers. Pre-trained layers will be fixed.
    """
    def __init__(self, opt="adam", input_dim=2048):
        super(pretrained_fixed, self).__init__(opt)
        m = Sequential()
        m.add(Dense(256, input_dim=input_dim))
        m.add(Dropout(0.5))
        m.add(Activation("relu"))
        m.add(Dense(128))
        m.add(Dropout(0.5))
        m.add(Activation("relu"))
        m.add(Dense(8))
        m.add(Activation("softmax"))
        m.compile(optimizer=self._opt,
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
        self._model = m

class pretrained_ft(base_model):
    """
    A model that combines a pre-trained ImageNet model with
    simple fully connected layers. Pre-trained layers will be fine-tuned.
    """
    def __init__(self, opt="adam"):
        super(pretrained_ft, self).__init__(opt)
        self._model = applications.ResNet50(weights='imagenet', include_top=True)
        self._model.layers.pop()
        x = self._model.layers[-1].output
        x = Dense(256, activation='relu', name='fc1')(x)
        x = Dense(8, activation='softmax', name='predictions')(x)
        self._model = Model(input=self._model.input, output=x)
        self._model.compile(optimizer=self._opt, loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        self._model.summary()
