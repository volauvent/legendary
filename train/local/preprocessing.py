import sys
sys.path.append("../../third-party/deep-learning-models")
from resnet50 import ResNet50
from keras.preprocessing import image
from imagenet_utils import preprocess_input, decode_predictions
import tensorflow as tf
from six.moves import cPickle
import os
import numpy as np
from PIL import Image
from PIL import ImageEnhance
import PIL.ImageOps


PIXEL_DEPTH = 255.0

def cal_img_num():
    labelNames = os.listdir("images")
    sample_num = 0
    for labname in labelNames:
        if labname != '.DS_Store':
            sample_num += len(os.listdir('images/' + labname))
    return sample_num


def load_preprocess_img():
    print("Begin load and preprocess images...")
    labelNames = os.listdir("images")
    sample_num = cal_img_num()
    # rawX = np.zeros((sample_num, 224, 224, 3))
    X = np.zeros((sample_num, 1000))
    y = np.zeros(sample_num, dtype=int)
    model = ResNet50(weights='imagenet')

    cnt = 0
    for lab, labname in enumerate(labelNames):
        if labname == '.DS_Store':
            continue
        imagefiles = os.listdir('images/'+labname)
        for imagefile in imagefiles:
            img_path = 'images/'+labname+'/'+imagefile
            img = image.load_img(img_path, target_size=(224, 224))
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x = preprocess_input(x)

            # rawX[cnt, :] = x
            X[cnt, :] = model.predict(x)
            y[cnt] = lab
            cnt += 1

            if cnt%100 == 0:
                print(cnt)
                # break
    with open('./origin_data.pkl', 'wb') as f:
        cPickle.dump((X[:cnt, :], y[:cnt]), f)
    print("Done!")
    print("")

def load_augment_preprocess_img():
    print("Begin augment images...")
    sample_num = cal_img_num()
    labelNames = os.listdir("images")
    # rawX = np.zeros((sample_num, 224, 224, 3))
    X = np.zeros((sample_num * 4, 1000))
    y = np.zeros(sample_num * 4, dtype=int)
    model = ResNet50(weights='imagenet')

    cnt = 0
    for lab, labname in enumerate(labelNames):
        if labname == '.DS_Store':
            continue
        imagefiles = os.listdir('images/'+labname)
        for imagefile in imagefiles:
            img_path = 'images/'+labname+'/'+imagefile
            img = image.load_img(img_path, target_size=(224, 224))
            x = image.img_to_array(img)
            #x = np.expand_dims(x, axis=0)

            trans_x = translate_img(x)
            flip_x = flip_img(x)
            inv_x = inverse_img(x)
            # brig_x = bright_img(x)
            # cons_x = contrast_img(x)

            trans_x = np.expand_dims(trans_x, axis=0)
            flip_x = np.expand_dims(flip_x, axis=0)
            inv_x = np.expand_dims(inv_x, axis=0)
            # brig_x = np.expand_dims(brig_x, axis=0)
            # cons_x = np.expand_dims(cons_x, axis=0)
            x = np.expand_dims(x, axis=0)

            x = preprocess_input(x)
            # trans_x = preprocess_input(trans_x)
            # flip_x = preprocess_input(flip_x)
            # inv_x = preprocess_input(inv_x)
            # brig_x = preprocess_input(brig_x)
            # cons_x = preprocess_input(cons_x)
            # trans_x = scale_pixel_values(trans_x)
            # flip_x = scale_pixel_values(flip_x)
            # inv_x = scale_pixel_values(inv_x)
            # brig_x = scale_pixel_values(brig_x)
            # cons_x = scale_pixel_values(cons_x)

            # rawX[cnt, :] = x
            X[cnt, :] = model.predict(x)
            y[cnt] = lab
            cnt += 1
            X[cnt, :] = model.predict(trans_x)
            y[cnt] = lab
            cnt += 1
            X[cnt, :] = model.predict(flip_x)
            y[cnt] = lab
            cnt += 1
            X[cnt, :] = model.predict(inv_x)
            y[cnt] = lab
            cnt += 1
            # X[cnt, :] = model.predict(brig_x)
            # y[cnt] = lab
            # cnt += 1
            # X[cnt, :] = model.predict(cons_x)
            # y[cnt] = lab
            # cnt += 1
            if cnt%100 == 0:
                print(cnt)
                # break
    with open('./augment_data.pkl', 'wb') as f:
        cPickle.dump((X[:cnt, :], y[:cnt]), f)
    print("Done!")
    print("")

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

def flip_img(img):
    new_image = Image.fromarray(np.uint8(img))
    return np.array(new_image.rotate(180))

def inverse_img(img):
    new_image = Image.fromarray(np.uint8(img))
    return np.array(PIL.ImageOps.invert(new_image))

def bright_img(img):
    new_image = Image.fromarray(np.uint8(img))
    bright_mod = ImageEnhance.Brightness(new_image)
    return bright_mod.enhance(1.5)

def contrast_img(img):
    new_image = Image.fromarray(np.uint8(img))
    contrast_mod = ImageEnhance.Contrast(new_image)
    return contrast_mod.enhance(1.5)

def scale_pixel_values(dataset):
    return (dataset[0:,:,:,:] - PIXEL_DEPTH / 2.0) / PIXEL_DEPTH

# def data_augmentation(dataset, labels):
#     graph = tf.Graph()
#     with graph.as_default():
#         tf_img = tf.placeholder(tf.float32, shape=(IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS))
#
#         flipped_image = tf.image.random_flip_left_right(tf_img)
#
#         brightened_image = tf.image.random_brightness(tf_img, max_delta=50)
#         brightened_image = tf.clip_by_value(brightened_image, 0.0, PIXEL_DEPTH)
#
#         contrasted_image = tf.image.random_contrast(tf_img, lower=0.5, upper=1.5)
#         contrasted_image = tf.clip_by_value(brightened_image, 0.0, PIXEL_DEPTH)
#
#     '''Supplement dataset with flipped, rotated, etc images'''
#     n = len(dataset)
#     new_data, new_labels = make_dataset_arrays(num_rows=n * 4)
#     num_new = 0
#
#     with tf.Session(graph=graph) as session:
#         for i in range(len(dataset)):
#             img = np.reshape(dataset[i, :, :, :], (IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS))
#             img = np.asarray(img)
#             img = img.astype(np.float32)
#             label = labels[i, :]
#             for _ in range(3):
#                 r = random.uniform(0, 1)
#                 new_img = session.run(flipped_image, feed_dict={tf_img: img})
#                 if r < 0.5:
#                     new_img = session.run(brightened_image, feed_dict={tf_img: new_img})
#                     new_img = session.run(contrasted_image, feed_dict={tf_img: new_img})
#                 else:
#                     new_img = session.run(contrasted_image, feed_dict={tf_img: new_img})
#                     new_img = session.run(brightened_image, feed_dict={tf_img: new_img})
#                 new_data[num_new, :, :, :] = new_img
#                 new_labels[num_new, :] = label
#                 num_new += 1
#
#     assert num_new == n * 3
#     new_data[num_new:, :, :, :] = dataset
#     new_labels[num_new:, :] = labels
#     #new_data, new_labels = randomize(new_data, new_labels)
#     return new_data, new_labels


if __name__ == '__main__':
    # load_preprocess_img()
    load_augment_preprocess_img()