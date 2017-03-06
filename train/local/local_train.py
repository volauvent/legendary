from keras.layers import Dense, Activation, Dropout
from keras.models import Sequential
from keras.optimizers import SGD
from keras.utils.np_utils import to_categorical
from keras.models import load_model
from sklearn.metrics import confusion_matrix
import pickle
import numpy as np
import os.path
import itertools

import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix


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


training_samples = 20000
X, y = pickle.load(open("data.pkl", 'rb'))

shuf = np.arange(X.shape[0])
np.random.shuffle(shuf)

X = X[shuf, :]
y = y[shuf]
train_X = X[:training_samples, :]
train_y = y[:training_samples]
val_X = X[training_samples:, :]
val_y = y[training_samples:]

if not os.path.exists("model.h5"):
    model = Sequential()
    model.add(Dense(output_dim=128, input_dim=1000))
    model.add(Dropout(0.2))
    model.add(Activation("tanh"))
    model.add(Dense(output_dim=64, input_dim=128))
    model.add(Dropout(0.5))
    model.add(Activation("tanh"))
    model.add(Dense(output_dim=8))
    model.add(Activation("softmax"))
    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(optimizer=sgd,
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    # print X.shape, to_categorical(y, nb_classes=8).shape
    model.fit(train_X, to_categorical(train_y, nb_classes=8),
              nb_epoch=50,
              validation_data=(val_X, to_categorical(val_y, nb_classes=8)))
    model.save('model.h5')

else:
    model = load_model('model.h5')
    predicted_label = model.predict_classes(val_X)
    cnf_matrix = confusion_matrix(val_y, predicted_label)
    np.set_printoptions(precision=2)
    class_names = os.listdir("images")

    # Plot non-normalized confusion matrix
    plt.figure()
    plot_confusion_matrix(cnf_matrix, classes=class_names,
                          title='Confusion matrix, without normalization')

    # Plot normalized confusion matrix
    plt.figure()
    plot_confusion_matrix(cnf_matrix, classes=class_names, normalize=True,
                          title='Normalized confusion matrix')

    # plt.show()
    plt.savefig("confusion_matrix.png")
