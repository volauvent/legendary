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
VALIDATION_PERCENT = .3
TEST_PERCENT = .2
IMAGE_SIZE = 50 #resize & compress size
MAX_SIZE = 50000 #maximum image array length
NUM_CHANNELS = 3  # RGB channels
PIXEL_DEPTH = 255.0
NUM_EMOTIONS = 11
PARTITION_TEST = False


def make_origin_image_date():
    emotion_path = DATA_PATH + 'raw_images'
    emotion_files = [x for x in os.listdir(emotion_path) if x != '.DS_Store']

    train_data, train_labels = make_origin_dataset_arrays()
    val_data, val_labels = make_origin_dataset_arrays()
    test_data, test_labels = make_origin_dataset_arrays()
    num_train = num_val = num_test = 0

    for label, emotion in enumerate(emotion_files):
        # create a one-hot encoding of this artist's label
        emotion_label = (np.arange(NUM_EMOTIONS) == label).astype(np.float32)
        emotion_data_origin, emotion_data = loadEmotionImg(emotion)
        emotion_data_origin = scale_pixel_values(emotion_data_origin)
        num_emotion_imgs = len(emotion_data_origin)

        # randomly shuffle the data to ensure random validation and test sets
        # np.random.shuffle(emotion_data_origin)

        nv = int(num_emotion_imgs * VALIDATION_PERCENT)

        # partition validation data
        temp_val = emotion_data_origin[0:nv, :, :]
        val_data[num_val:num_val + nv, :, :] = temp_val
        val_labels[num_val:num_val + nv, :] = emotion_label
        num_val += nv

        # partition test data
        if PARTITION_TEST:
            nt = int(num_emotion_imgs * TEST_PERCENT)
            temp_test = emotion_data_origin[nv:nv + nt, :, :]
            test_data[num_test:num_test + nt, :, :] = temp_test
            test_labels[num_test:num_test + nt, :] = emotion_label
            num_test += nt
        else:
            nt = 0

        # patition train data
        img_train = emotion_data_origin[nv + nt:, :, :]
        ntr = len(img_train)
        train_data[num_train:num_train + ntr, :, :] = img_train
        train_labels[num_train:num_train + ntr, :] = emotion_label
        num_train += ntr

    # throw out extra allocated rows
    train_data, train_labels = trim_origin_dataset_arrays(train_data, train_labels, num_train)
    val_data, val_labels = trim_origin_dataset_arrays(val_data, val_labels, num_val)

    # shuffle the data to distribute samples from artists randomly
    #train_data, train_labels = randomize(train_data, train_labels)
    #val_data, val_labels = randomize(val_data, val_labels)

    print ('Training set:', train_data.shape, train_labels.shape)
    print ('Validation:', val_data.shape, val_labels.shape)

    if PARTITION_TEST:
        test_data, test_labels = trim_origin_dataset_arrays(test_data, test_labels, num_test)
        #test_data, test_labels = randomize(test_data, test_labels)
        print ('Testing:', test_data.shape, test_labels.shape)
        print ('')

    # save all the datasets in a pickle file
    pickle_file = 'origin_emotion_image_data.pickle'
    save = {
        'train_data': train_data,
        'train_labels': train_labels,
        'val_data': val_data,
        'val_labels': val_labels
    }
    if PARTITION_TEST:
        save['test_data'] = test_data
        save['test_labels'] = test_labels
    save_pickle_file(pickle_file, save)
    return


def make_standard_image_date():
    emotion_path = DATA_PATH + 'raw_images'
    emotion_files = [x for x in os.listdir(emotion_path) if x != '.DS_Store']

    train_data, train_labels = make_dataset_arrays()
    val_data, val_labels = make_dataset_arrays()
    test_data, test_labels = make_dataset_arrays()
    num_train = num_val = num_test = 0

    for label, emotion in enumerate(emotion_files):
        # create a one-hot encoding of this artist's label
        emotion_label = (np.arange(NUM_EMOTIONS) == label).astype(np.float32)
        emotion_data_origin, emotion_data = loadEmotionImg(emotion)
        emotion_data = scale_pixel_values(emotion_data)
        num_emotion_imgs = len(emotion_data)

        # randomly shuffle the data to ensure random validation and test sets
        # np.random.shuffle(emotion_data_origin)

        nv = int(num_emotion_imgs * VALIDATION_PERCENT)

        # partition validation data
        temp_val = emotion_data[0:nv, :, :, :]
        val_data[num_val:num_val + nv, :, :, :] = temp_val
        val_labels[num_val:num_val + nv, :] = emotion_label
        num_val += nv

        # partition test data
        if PARTITION_TEST:
            nt = int(num_emotion_imgs * TEST_PERCENT)
            temp_test = emotion_data[nv:nv + nt, :, :, :]
            test_data[num_test:num_test + nt, :, :, :] = temp_test
            test_labels[num_test:num_test + nt, :] = emotion_label
            num_test += nt
        else:
            nt = 0

        # patition train data
        img_train = emotion_data[nv + nt:, :, :, :]
        ntr = len(img_train)
        train_data[num_train:num_train + ntr, :, :, :] = img_train
        train_labels[num_train:num_train + ntr, :] = emotion_label
        num_train += ntr

    # throw out extra allocated rows
    train_data, train_labels = trim_dataset_arrays(train_data, train_labels, num_train)
    val_data, val_labels = trim_dataset_arrays(val_data, val_labels, num_val)

    # shuffle the data to distribute samples from artists randomly
    #train_data, train_labels = randomize(train_data, train_labels)
    #val_data, val_labels = randomize(val_data, val_labels)

    print ('Training set:', train_data.shape, train_labels.shape)
    print ('Validation:', val_data.shape, val_labels.shape)

    if PARTITION_TEST:
        test_data, test_labels = trim_dataset_arrays(test_data, test_labels, num_test)
        #test_data, test_labels = randomize(test_data, test_labels)
        print ('Testing:', test_data.shape, test_labels.shape)
        print ('')

    # save all the datasets in a pickle file
    pickle_file = 'std_emotion_image_data.pickle'
    save = {
        'train_data': train_data,
        'train_labels': train_labels,
        'val_data': val_data,
        'val_labels': val_labels
    }
    if PARTITION_TEST:
        save['test_data'] = test_data
        save['test_labels'] = test_labels
    save_pickle_file(pickle_file, save)
    return


def make_datasets():
    make_origin_image_date()
    make_standard_image_date()


def loadEmotionImg(emotion):
    '''Load the images for a category.'''
    print('')
    print ("Loading images from file ", emotion, "...")
    folder = DATA_PATH + 'raw_images/' + emotion + '/'
    image_files = [x for x in os.listdir(folder) if '.png' in x]
    dataset_origin = np.ndarray(shape = (len(image_files), MAX_SIZE, NUM_CHANNELS),
                                dtype=np.float32)
    dataset = np.ndarray(shape=(len(image_files), IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS),
                         dtype=np.float32)
    num_images = 0
    for image in image_files:
        image_file = os.path.join(folder, image)
        try:
            image_origin_data, raw_data = read_image_from_file(image_file)
            image_data = resize_image(raw_data)
            dataset_origin[num_images, :, :] = image_origin_data[:MAX_SIZE,:]
            dataset[num_images, :, :, :] = image_data
            num_images = num_images + 1
        except IOError as e:
            print('Could not read:', image_file, ':', e)

    dataset = dataset[0:num_images, :, :, :]
    dataset_origin = dataset_origin[0:num_images, :, :]

    print ('Resized dataset size:', dataset.shape)
    print ('Mean:', np.mean(dataset))
    print ('Standard deviation:', np.std(dataset))
    print ('')
    return dataset_origin, dataset


def read_image_from_file(file_path):
    img = Image.open(file_path)
    pixel_values = np.array(img.getdata())
    return pixel_values, img


def resize_image(img):
    img = img.resize((IMAGE_SIZE, IMAGE_SIZE), Image.ANTIALIAS)
    pixel_values = np.array(img.getdata())
    return np.reshape(pixel_values, [IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS])


def make_dataset_arrays(num_rows=2000):
    data = np.ndarray((num_rows, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS), dtype=np.float32)
    labels = np.ndarray((num_rows, NUM_EMOTIONS), dtype=np.int32)
    return data, labels


def make_origin_dataset_arrays(num_rows=2000):
    data = np.ndarray((num_rows, MAX_SIZE, NUM_CHANNELS), dtype=np.float32)
    labels = np.ndarray((num_rows, NUM_EMOTIONS), dtype=np.int32)
    return data, labels


def scale_pixel_values(dataset):
    return (dataset - PIXEL_DEPTH / 2.0) / PIXEL_DEPTH


def trim_dataset_arrays(data, labels, new_size):
    data = data[0:new_size, :, :, :]
    labels = labels[0:new_size, :]
    return data, labels


def trim_origin_dataset_arrays(data, labels, new_size):
    data = data[0:new_size, :, :]
    labels = labels[0:new_size, :]
    return data, labels


def save_pickle_file(pickle_file, save_dict):
    try:
        f = open(DATA_PATH + pickle_file, 'wb')
        pickle.dump(save_dict, f, pickle.HIGHEST_PROTOCOL)
        f.close()
    except Exception as e:
        print('Unable to save data to', pickle_file, ':', e)
        raise
    print ("Datasets saved to file", DATA_PATH + pickle_file)


def randomize(dataset, labels):
    permutation = np.random.permutation(labels.shape[0])
    shuffled_dataset = dataset[permutation, :, :, :]
    shuffled_labels = labels[permutation, :]
    return shuffled_dataset, shuffled_labels


if __name__ == '__main__':
    print ("Making artist dataset and saving it to:", DATA_PATH)
    print ("To change this and other settings, edit the flags at the top of this file.")

    #makeOriginImageDate()
    #makeStandardImageDate()
    make_datasets()


"""
def fast_warp(img, tf, output_shape=(50, 50), mode='constant', order=1):
    m = tf.params # tf._matrix is
    return skimage.transform._warps_cy._warp_fast(img, m, output_shape=output_shape, mode=mode, order=order)


#
def build_centering_transform(image_shape, target_shape=(50, 50)):
    rows, cols = image_shape
    trows, tcols = target_shape
    shift_x = (cols - tcols) / 2.0
    shift_y = (rows - trows) / 2.0
    return skimage.transform.SimilarityTransform(translation=(shift_x, shift_y))


def perturb(img, augmentation_params, target_shape=(50, 50), rng=np.random):
    # # DEBUG: draw a border to see where the image ends up
    # img[0, :] = 0.5
    # img[-1, :] = 0.5
    # img[:, 0] = 0.5
    # img[:, -1] = 0.5
    tform_centering = build_centering_transform(img.shape, target_shape)
    #tform_center, tform_uncenter = build_center_uncenter_transforms(img.shape)
    #tform_augment = random_perturbation_transform(rng=rng, **augmentation_params)
    #tform_augment = tform_uncenter + tform_augment + tform_center # shift to center, augment, shift back (for the rotation/shearing)
    return fast_warp(img, tform_centering , output_shape=target_shape, mode='constant').astype('float32')
"""
