# -*- coding: utf-8 -*-
import numpy as np
import os
import sys
import random
from PIL import Image
from PIL import ImageEnhance
import PIL.ImageOps
import tensorflow as tf
from six.moves import cPickle as pickle


DATA_PATH = 'emotion_images/'
VALIDATION_PERCENT = .2
TEST_PERCENT = .2
IMAGE_SIZE = 50 #resize & compress size
MAX_SIZE = 50000 #maximum image array length
NUM_CHANNELS = 3  # RGB channels
PIXEL_DEPTH = 255.0
NUM_EMOTIONS = 8
PARTITION_TEST = False


def augment_training_set():
    print ("\nAugmenting training data...")
    with open(DATA_PATH + 'std_emotion_image_data.pickle', 'rb') as f:
        save = pickle.load(f)
        train_X = save['train_data']
        train_Y = save['train_labels']

    train_RGB = (train_X * PIXEL_DEPTH) + PIXEL_DEPTH / 2.0
    new_train, new_labels = data_augmentation(train_RGB, train_Y)
    new_train = scale_pixel_values(new_train)

    save['train_data'] = new_train
    save['train_labels'] = new_labels
    save_pickle_file('augmented_image_data.pickle', save)


def data_augmentation(dataset, labels):
    graph = tf.Graph()
    with graph.as_default():
        tf_img = tf.placeholder(tf.float32, shape=(IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS))

        flipped_image = tf.image.random_flip_left_right(tf_img)

        brightened_image = tf.image.random_brightness(tf_img, max_delta=50)
        brightened_image = tf.clip_by_value(brightened_image, 0.0, PIXEL_DEPTH)

        contrasted_image = tf.image.random_contrast(tf_img, lower=0.5, upper=1.5)
        contrasted_image = tf.clip_by_value(brightened_image, 0.0, PIXEL_DEPTH)

    '''Supplement dataset with flipped, rotated, etc images'''
    n = len(dataset)
    new_data, new_labels = make_dataset_arrays(num_rows=n * 4)
    num_new = 0

    with tf.Session(graph=graph) as session:
        for i in range(len(dataset)):
            img = np.reshape(dataset[i, :, :, :], (IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS))
            img = np.asarray(img)
            img = img.astype(np.float32)
            label = labels[i, :]
            for _ in range(3):
                r = random.uniform(0, 1)
                new_img = session.run(flipped_image, feed_dict={tf_img: img})
                if r < 0.5:
                    new_img = session.run(brightened_image, feed_dict={tf_img: new_img})
                    new_img = session.run(contrasted_image, feed_dict={tf_img: new_img})
                else:
                    new_img = session.run(contrasted_image, feed_dict={tf_img: new_img})
                    new_img = session.run(brightened_image, feed_dict={tf_img: new_img})
                new_data[num_new, :, :, :] = new_img
                new_labels[num_new, :] = label
                num_new += 1

    assert num_new == n * 3
    new_data[num_new:, :, :, :] = dataset
    new_labels[num_new:, :] = labels
    #new_data, new_labels = randomize(new_data, new_labels)
    return new_data, new_labels


def make_invariance_sets():
    print ("\nMaking invariance datasets...")
    with open(DATA_PATH + 'std_emotion_image_data.pickle', 'rb') as f:
        save = pickle.load(f)
        val_X = save['val_data']
        val_Y = save['val_labels']
        del save  # hint to help gc free up memory

    n = len(val_X)
    translated_val_X = np.ndarray((n, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS), dtype=np.float32)
    flipped_val_X = np.ndarray((n, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS), dtype=np.float32)
    inverted_val_X = np.ndarray((n, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS), dtype=np.float32)
    dark_val_X = np.ndarray((n, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS), dtype=np.float32)
    bright_val_X = np.ndarray((n, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS), dtype=np.float32)
    high_contrast_val_X = np.ndarray((n, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS), dtype=np.float32)
    low_contrast_val_X = np.ndarray((n, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS), dtype=np.float32)

    print ("\tFlipping and inverting images...")
    val_X_RGB = (val_X * PIXEL_DEPTH) + PIXEL_DEPTH / 2.0
    for i in range(n):
        npimg = val_X_RGB[i, :, :, :]
        img = Image.fromarray(np.uint8(npimg))

        translated_val_X[i, :, :, :] = translate_img(npimg)
        flipped_val_X[i, :, :, :] = np.array(img.rotate(180))
        inverted_val_X[i, :, :, :] = np.array(PIL.ImageOps.invert(img))

        bright_mod = ImageEnhance.Brightness(img)
        dark_val_X[i, :, :, :] = bright_mod.enhance(0.75)
        bright_val_X[i, :, :, :] = bright_mod.enhance(1.5)

        contrast_mod = ImageEnhance.Contrast(img)
        low_contrast_val_X[i, :, :, :] = bright_mod.enhance(0.75)
        high_contrast_val_X[i, :, :, :] = bright_mod.enhance(1.5)

    print ("\tScaling pixel values...")
    translated_val_X = scale_pixel_values(translated_val_X)
    flipped_val_X = scale_pixel_values(flipped_val_X)
    inverted_val_X = scale_pixel_values(inverted_val_X)
    dark_val_X = scale_pixel_values(dark_val_X)
    bright_val_X = scale_pixel_values(bright_val_X)
    high_contrast_val_X = scale_pixel_values(high_contrast_val_X)
    low_contrast_val_X = scale_pixel_values(low_contrast_val_X)

    print ("\tPickling file...")
    save = {
        'translated_val_data': translated_val_X,
        'flipped_val_data': flipped_val_X,
        'inverted_val_data': inverted_val_X,
        'bright_val_data': bright_val_X,
        'dark_val_data': dark_val_X,
        'high_contrast_val_data': high_contrast_val_X,
        'low_contrast_val_data': low_contrast_val_X,
    }
    save_pickle_file('invariance_image_data.pickle', save)


def translate_img(img):
    # translate down
    slice_pix = img[-10:, :, :]
    rest = img[:-10, :, :]
    new = np.concatenate((slice_pix, rest))

    # translate right
    slice_pix = new[:, -10:, :]
    rest = new[:, :-10, :]
    new = np.concatenate((slice_pix, rest), axis=1)

    return new


def save_pickle_file(pickle_file, save_dict):
    try:
        f = open(DATA_PATH + pickle_file, 'wb')
        pickle.dump(save_dict, f, pickle.HIGHEST_PROTOCOL)
        f.close()
    except Exception as e:
        print('Unable to save data to', pickle_file, ':', e)
        raise

    print ("Datasets saved to file", DATA_PATH + pickle_file)


def scale_pixel_values(dataset):
    return (dataset - PIXEL_DEPTH / 2.0) / PIXEL_DEPTH


def make_dataset_arrays(num_rows=2000):
    data = np.ndarray((num_rows, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS), dtype=np.float32)
    labels = np.ndarray((num_rows, NUM_EMOTIONS), dtype=np.int32)
    return data, labels


def randomize(dataset, labels):
    permutation = np.random.permutation(labels.shape[0])
    shuffled_dataset = dataset[permutation, :, :, :]
    shuffled_labels = labels[permutation, :]
    return shuffled_dataset, shuffled_labels

if __name__ == '__main__':
    print ("Making artist dataset and saving it to:", DATA_PATH)
    print ("To change this and other settings, edit the flags at the top of this file.")

    #make_invariance_sets()
    augment_training_set()