"""
Preprocess Module

This module implements pre-processing methods and data augmentation for training and testing.
"""
import numpy as np
import pickle


class preprocess():
    """
    Preprocessing Module
    User calls imageFeed
    """

    def __init__(self, metadata, method):
        self._metadata = metadata
        self._method = method
        pass

    def read(self, metadata):
        '''
        Read one image
        '''
        return None

    def augmentation(self, img):
        '''
        data augmentation
        '''
        for newimg in [img]*10:
            yield newimg

    def process(self, img):
        '''
        Preprocessing
        '''
        if self._method == 1:
            pass
        elif self._method == 2:
            pass

        return np.random.randn(100,100)

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
        result = np.asarray(self.imageFeed(), dtype=np.float, shape=(10,10))
        with open(filename, 'rb') as f:
            pickle.dump(result, f)

