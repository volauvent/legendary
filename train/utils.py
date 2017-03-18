import matplotlib.pyplot as plt
import itertools
import numpy as np
from PIL import Image
from PIL import ImageEnhance
import PIL.ImageOps

PIXEL_DEPTH = 255.0


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
    return (dataset[0:, :, :, :] - PIXEL_DEPTH / 2.0) / PIXEL_DEPTH


def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, "{:.2f}".format(cm[i, j]),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
