# -*- coding: utf-8 -*-


import numpy as np
import os
import sys

sys.path.append("../../third-party/deep-learning-models")


import random
from PIL import Image
from PIL import ImageEnhance
import PIL.ImageOps
import tensorflow as tf
from six.moves import cPickle as pickle
from resnet50 import ResNet50
from keras.preprocessing import image
from imagenet_utils import preprocess_input, decode_predictions
#import cPickle





DATA_PATH = 'emotion_images/'
VALIDATION_PERCENT = 0.0
TEST_PERCENT = .2
IMAGE_SIZE = 224 #resize & compress size
MAX_SIZE = 160000 #maximum image array length
NUM_CHANNELS = 3  # RGB channels
PIXEL_DEPTH = 255.0
NUM_EMOTIONS = 8
PARTITION_TEST = False

def make_datasets():
    #make_origin_image_date()
    make_standard_image_date()

"""
def make_origin_image_date():
    emotion_path = DATA_PATH + 'raw_images'
    emotion_files = [x for x in os.listdir(emotion_path) if x != '.DS_Store']

    total_images_num = cal_image_nums()

    train_data, train_labels = make_origin_dataset_arrays(total_images_num)
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
"""

def make_standard_image_date():
    emotion_path = DATA_PATH + 'raw_images'
    emotion_files = [x for x in os.listdir(emotion_path) if x != '.DS_Store']

    total_images_num = cal_image_nums()

    train_data, train_labels = make_dataset_arrays(total_images_num)
    val_data, val_labels = make_dataset_arrays()
    test_data, test_labels = make_dataset_arrays()
    num_train = num_val = num_test = 0

    train_data_model, train_labels_model = make_model_dataset_arrays(total_images_num)
    val_data_model, val_labels_model = make_model_dataset_arrays()
    test_data_model, test_labels_model = make_model_dataset_arrays()


    # use ResNet50 preprocess image
    #model_date = np.zeros((total_images_num, 1000))
    #model = ResNet50(weights='imagenet')

    for label, emotion in enumerate(emotion_files):
        # create a one-hot encoding of this artist's label
        emotion_label = (np.arange(NUM_EMOTIONS) == label).astype(np.float32)
        emotion_data_origin, emotion_data = loadEmotionImg(emotion)

        #print(emotion_data[0].shape)

        emotion_data_for_model = resNet_preprocess(emotion_data)

        emotion_data = scale_pixel_values(emotion_data)


        num_emotion_imgs = emotion_data.shape[0]

        # randomly shuffle the data to ensure random validation and test sets
        # np.random.shuffle(emotion_data_origin)

        nv = int(num_emotion_imgs * VALIDATION_PERCENT)

        # partition validation data
        temp_val = emotion_data[0:nv, :, :, :]
        val_data[num_val:num_val + nv, :, :, :] = temp_val
        val_labels[num_val:num_val + nv, :] = emotion_label


        # for model
        #print(emotion_data_for_model.shape)
        temp_val_model = emotion_data_for_model[0:nv, :]
        val_data_model[num_val:num_val + nv, :] = temp_val_model
        val_labels_model[num_val:num_val + nv, :] = emotion_label
        num_val += nv

        # partition test data
        if PARTITION_TEST:
            nt = int(num_emotion_imgs * TEST_PERCENT)
            temp_test = emotion_data[nv:nv + nt, :, :, :]
            test_data[num_test:num_test + nt, :, :, :] = temp_test
            test_labels[num_test:num_test + nt, :] = emotion_label

            temp_test_model = emotion_data_for_model[nv:nv + nt, :]
            test_data_model[num_test:num_test + nt, :] = temp_test_model
            test_labels_model[num_test:num_test + nt, :] = emotion_label

            num_test += nt
        else:
            nt = 0

        # patition train data
        img_train = emotion_data[nv + nt:, :, :, :]
        ntr = len(img_train)
        train_data[num_train:num_train + ntr, :, :, :] = img_train
        train_labels[num_train:num_train + ntr, :] = emotion_label

        img_train_model = emotion_data_for_model[nv + nt:, :]
        #ntr = len(img_train)
        train_data_model[num_train:num_train + ntr, :] = img_train_model
        train_labels_model[num_train:num_train + ntr, :] = emotion_label

        num_train += ntr

    # throw out extra allocated rows
    train_data, train_labels = trim_dataset_arrays(train_data, train_labels, num_train)
    val_data, val_labels = trim_dataset_arrays(val_data, val_labels, num_val)

    train_data_model, train_labels_model = trim_model_dataset_arrays(train_data_model, train_labels_model, num_train)
    val_data_model, val_labels_model = trim_model_dataset_arrays(val_data_model, val_labels_model, num_val)

    # shuffle the data to distribute samples from artists randomly
    #train_data, train_labels = randomize(train_data, train_labels)
    #val_data, val_labels = randomize(val_data, val_labels)

    print ('Training set:', train_data.shape, train_labels.shape)
    print ('Validation:', val_data.shape, val_labels.shape)

    if PARTITION_TEST:
        test_data, test_labels = trim_dataset_arrays(test_data, test_labels, num_test)
        #test_data, test_labels = randomize(test_data, test_labels)

        test_data_model, test_labels_model = trim_model_dataset_arrays(test_data_model, test_labels_model, num_test)


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


    pickle_file_model = 'model_emotion_image_data.pickle'
    save = {
        'train_data': train_data_model,
        'train_labels': train_labels_model,
        'val_data': val_data_model,
        'val_labels': val_labels_model
    }
    if PARTITION_TEST:
        save['test_data'] = test_data_model
        save['test_labels'] = test_labels_model
    save_pickle_file(pickle_file_model, save)

    return


def loadEmotionImg(emotion):
    '''Load the images for a category.'''
    print('')
    print ("Loading images from file ", emotion, "...")
    folder = DATA_PATH + 'raw_images/' + emotion + '/'
    image_files = [x for x in os.listdir(folder) if '.jpg' in x]
    dataset_origin = np.ndarray(shape = (len(image_files), MAX_SIZE, NUM_CHANNELS),
                                dtype=np.float32)
    dataset_resize = np.ndarray(shape=(len(image_files), IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS),
                         dtype=np.float32)

    #use ResNet50 preprocess image
    #dataset_model = np.zeros((len(image_files), 1000))
    #model = ResNet50(weights='imagenet')

    num_images = 0
    for image in image_files:
        image_file = os.path.join(folder, image)
        try:
            image_origin_data, raw_data = read_image_from_file(image_file)
            image_data_std = resize_image(raw_data)
            # image_data_model = model.predict(image_data_std)

            dataset_origin[num_images, :, :] = image_origin_data[:MAX_SIZE,:]
            dataset_resize[num_images, :, :, :] = image_data_std
            # dataset_model[num_images, :] = image_data_model

            num_images = num_images + 1
        except IOError as e:
            print('Could not read:', image_file, ':', e)

    dataset_resize = dataset_resize[0:num_images, :, :, :]
    dataset_origin = dataset_origin[0:num_images, :, :]
    # dataset_model = dataset_model[0:num_images, :]

    print ('Resized dataset size:', dataset_resize.shape)
    print ('Mean:', np.mean(dataset_resize))
    print ('Standard deviation:', np.std(dataset_resize))
    print ('')
    return dataset_origin, dataset_resize#, dataset_model


def resNet_preprocess(imagedata):
    # use ResNet50 preprocess image

    image_nums = imagedata.shape[0]
    #print(image_nums)
    dataset_model = np.zeros((image_nums, 1000))

    model = ResNet50(weights='imagenet')

    for i in range(image_nums):

        temp = np.expand_dims(imagedata[i], axis=0)
        imagedata_pro = preprocess_input(temp)

        imagedata_model = model.predict(imagedata_pro)
        dataset_model[i, :] = imagedata_model

    return dataset_model


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

def make_model_dataset_arrays(num_rows=2000):
    data = np.ndarray((num_rows, 1000), dtype=np.float32)
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

def trim_model_dataset_arrays(data, labels, new_size):
    data = data[0:new_size, :]
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


def cal_image_nums():
    labelNames = os.listdir("emotion_images/raw_images/")
    sample_num = 0
    for labname in labelNames:
        if labname!= '.DS_Store':
            sample_num += len(os.listdir('emotion_images/raw_images/' + labname))
    return sample_num

if __name__ == '__main__':
    print ("Making artist dataset and saving it to:", DATA_PATH)
    print ("To change this and other settings, edit the flags at the top of this file.")

    #makeOriginImageDate()
    #makeStandardImageDate()
    make_datasets()

