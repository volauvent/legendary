import matplotlib.pyplot as plt
from keras import applications
from keras.layers import Dense, Activation, Dropout, Flatten
from keras.models import Sequential, load_model, Model
from keras.optimizers import SGD, Adam
from keras.utils.np_utils import to_categorical
from sklearn.metrics import confusion_matrix

import sys
sys.path.append("./")
from train.utils import plot_confusion_matrix
from keras.layers import Input, ZeroPadding2D, Conv2D, BatchNormalization, MaxPooling2D, AveragePooling2D
from keras.applications.resnet50 import conv_block, identity_block

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

    def fit(self, num_classes, train_X, train_y, val_X=None, val_y=None, np_epoch=30, class_weight={}):
        self._model.fit(train_X, to_categorical(train_y, num_classes),
                        nb_epoch=np_epoch,
                        validation_data=(val_X, to_categorical(val_y, num_classes)),
                        class_weight=class_weight)

    def train_on_batch(self, X, y):
        # print(X.shape, y.shape)
        self._model.train_on_batch(X, y)

    def predict(self, X):
        return self._model.predict(X)

    def predict_classes(self, X):
        return self._model.predict_classes(X)

    def conf_mat(self, X, y, class_names, savefile="train/confusion_matrix.png"):
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
    def __init__(self):
        opt = SGD(lr=1e-05, decay=1e-6, momentum=0.5, nesterov=True)
        super(pretrained_ft, self).__init__(opt)
        model1 = applications.ResNet50(weights='imagenet', include_top=True)
        model1.layers.pop()
        model2 = load_model('train/local/model.h5')
        inputs = model1.get_input_at(0)
        hidden = model1.layers[-2].output
        flat_hidden = Flatten()(hidden)
        outputs = model2(flat_hidden)
        self._model = Model(inputs, outputs)
        # x = self._model.layers[-1].output
        # x = Dense(256, activation='relu', name='fc1')(x)
        # x = Dense(8, activation='softmax', name='predictions')(x)
        # self._model = Model(input=self._model.input, output=x)
        self._model.compile(optimizer=self._opt, loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        self._model.summary()

        # self._model = load_model('train/local/model.h5')


class small_CNN(base_model):
    """
    A small CNN model
    """
    def __init__(self, opt="adam"):
        super(small_CNN, self).__init__(opt)
        img_input = Input(shape=(224,224,3))

        bn_axis = 3
        x = ZeroPadding2D((3, 3))(img_input)
        # x = Conv2D(64, (7, 7), strides=(2, 2), name='conv1')(x)
        # x = BatchNormalization(axis=bn_axis, name='bn_conv1')(x)
        # x = Activation('relu')(x)
        # x = MaxPooling2D((3, 3), strides=(2, 2))(x)


        # x = conv_block(x, 3, [64, 64, 256], stage=2, block='a', strides=(1, 1))
        # x = identity_block(x, 3, [64, 64, 256], stage=2, block='b')
        # x = identity_block(x, 3, [64, 64, 256], stage=2, block='c')

        # x = conv_block(x, 3, [128, 128, 512], stage=3, block='a')
        # x = identity_block(x, 3, [128, 128, 512], stage=3, block='b')
        # x = identity_block(x, 3, [128, 128, 512], stage=3, block='c')
        # x = identity_block(x, 3, [128, 128, 512], stage=3, block='d')
        #
        # x = conv_block(x, 3, [256, 256, 1024], stage=4, block='a')
        # x = identity_block(x, 3, [256, 256, 1024], stage=4, block='b')
        # x = identity_block(x, 3, [256, 256, 1024], stage=4, block='c')
        # x = identity_block(x, 3, [256, 256, 1024], stage=4, block='d')
        # x = identity_block(x, 3, [256, 256, 1024], stage=4, block='e')
        # x = identity_block(x, 3, [256, 256, 1024], stage=4, block='f')
        #
        x = conv_block(x, 3, [16, 16, 8], stage=5, block='a')
        # x = identity_block(x, 3, [16, 16, 8], stage=5, block='b')
        # x = identity_block(x, 3, [16, 16, 8], stage=5, block='c')

        x = AveragePooling2D((28, 28), name='avg_pool')(x)
        x = Flatten()(x)
        x = Dense(8, activation='softmax')(x)
        self._model = Model(img_input, x)
        self._model.compile(optimizer=self._opt, loss='sparse_categorical_crossentropy', metrics=['accuracy'])

        self._model.summary()
