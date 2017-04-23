"""
Preprocess Module

This module implements pre-processing methods and data augmentation for training and testing.
"""
import sys
sys.path.append("./")
import numpy as np
import pickle
import os
import logging
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input
from keras import applications
from train.utils import translate_img, flip_img, inverse_img

class preprocess():
    """
    Preprocessing Module
    User calls imageFeed
    """

    def __init__(self, method=None, metadata=None):
        self._metadata = metadata
        self._save = True
        if method == "resnet":
            self._model = applications.ResNet50(weights='imagenet', include_top=False)
            self._model.layers.pop()
            # self._model.summary()
        elif not method:
            self._model = None
        else:
            raise NotImplementedError("Method " + str(method) + " not implemented.")

    def online_read(self, train_batch_size=128, train_prop=0.7, val_batch_size=128, metadata=None):
        '''
        Read some image
        '''
        datapath = "train/local/images/"
        labelNames = os.listdir(datapath)
        img_paths = []
        for lab, labname in enumerate(labelNames):
            imagefiles = os.listdir(datapath + labname)
            for imagefile in imagefiles:
                img_paths.append((datapath + labname + '/' + imagefile, lab))

        X, y, valX, valy = [], [], [], []
        cur_num = 0
        round_num = 5
        train_num = int(len(img_paths)*train_prop)
        train_img_paths = img_paths[:train_num]
        val_img_paths = img_paths[train_num:]
        while True:
            np.random.shuffle(train_img_paths)
            for img_path, lab in train_img_paths:
                img = image.load_img(img_path, target_size=(224, 224))
                x = image.img_to_array(img)
                x = self.augmentation(x)
                x = preprocess_input(np.array(x))
                X.append(x)
                y += [lab] * x.shape[0]
                cur_num += x.shape[0]
                if cur_num >= train_batch_size:
                    if round_num >= 5:
                        np.random.shuffle(val_img_paths)
                        for val_img_path, val_lab in val_img_paths[:val_batch_size]:
                            img = image.load_img(val_img_path, target_size=(224, 224))
                            x = image.img_to_array(img)
                            x = preprocess_input(np.array([x]))
                            valX.append(x)
                            valy += [val_lab]
                        yield np.vstack(X), np.array(y), np.vstack(valX), np.vstack(valy)
                        round_num = 0
                    else:
                        yield np.vstack(X), np.array(y), None, None
                    round_num += 1
                    cur_num = 0
                    X, y, valX, valy = [], [], [], []

    def offline_read(self, datapath="train/local/images/", savefile="train/local/data.pkl"):
        """
        Read and process images.
        """

        labelNames = os.listdir(datapath)
        img_paths = []
        for lab, labname in enumerate(labelNames):
            imagefiles = os.listdir(datapath + labname)
            for imagefile in imagefiles:
                img_paths.append((datapath + labname + '/' + imagefile, lab))

        X, y = [], []
        y = []
        np.random.shuffle(img_paths)
        for img_path, lab in img_paths:
            img = image.load_img(img_path, target_size=(224, 224))
            x = image.img_to_array(img)
            x = self.augmentation(x)
            x = preprocess_input(np.array(x))
            x = self.process(x)
            X.append(x[:, 0, 0, :])
            y += [lab] * x.shape[0]
            if len(y) % 100 == 0:
                logging.info("Processed...{}".format(len(y)))
        if savefile:
            with open(savefile, 'wb') as f:
                pickle.dump((np.vstack(X), np.array(y), labelNames), f)
        return (np.vstack(X), np.array(y), labelNames)


    def augmentation(self, img):
        '''
        data augmentation
        '''
        X = [img]
        X.append(translate_img(img))
        X.append(flip_img(img))
        X.append(inverse_img(img))
        return X

    def process(self, img):
        '''
        Preprocessing internal implementation
        '''
        if not self._model:
            return img
        return self._model.predict(np.array(img))

    def processRaw(self, imgfile):
        """
        Preprocessing an raw imagefile
        """
        img = image.load_img(imgfile, target_size=(224, 224))
        x = image.img_to_array(img)
        x = preprocess_input(np.expand_dims(x, axis=0))
        self._model.predict(np.array(x))
        x = self.process(x)
        return x[:, 0, 0, :]

    def imageFeed(self):
        '''
        Fetching images by metadata and return as a generator
        '''
        for md in self._metadata:
            original_img = self.read(md)
            for img in self.augmentation(original_img):
                yield self.process(img)

    def store(self, filename):
        '''
        Store processed images offline for training
        :param filename:
        :return:
        '''
        result = np.asarray(self.imageFeed(), dtype=np.float, shape=(10, 10))
        with open(filename, 'rb') as f:
            pickle.dump(result, f)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    data_src = preprocess("resnet")
    data_src.offline_read()
