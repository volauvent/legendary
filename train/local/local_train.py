from keras.layers import Dense, Activation
from keras.models import Sequential
from keras.utils.np_utils import to_categorical
import cPickle
import numpy as np

training_samples = 20000
X, y = cPickle.load(open("data.pkl", 'rb'))

shuf = np.arange(X.shape[0])
np.random.shuffle(shuf)

X = X[shuf, :]
y = y[shuf]
train_X = X[:training_samples, :]
train_y = y[:training_samples]
val_X = X[training_samples:, :]
val_y = y[training_samples:]

model = Sequential()
model.add(Dense(output_dim=128, input_dim=1000))
model.add(Activation("tanh"))
model.add(Dense(output_dim=64, input_dim=1000))
model.add(Activation("tanh"))
model.add(Dense(output_dim=8))
model.add(Activation("softmax"))
model.compile(optimizer='adadelta',
              loss='categorical_crossentropy',
              metrics=['accuracy'])
# print X.shape, to_categorical(y, nb_classes=8).shape
model.fit(train_X, to_categorical(train_y, nb_classes=8),
          nb_epoch=50,
          validation_data=(val_X, to_categorical(val_y, nb_classes=8)))
