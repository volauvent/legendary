import sys
sys.path.append("../../third-party/deep-learning-models")
from resnet50 import ResNet50
from keras.preprocessing import image
from imagenet_utils import preprocess_input, decode_predictions
import cPickle
import os
import numpy as np

labelNames = os.listdir("images")
sample_num = 0
for labname in labelNames:
    sample_num += len(os.listdir('images/'+labname))


# rawX = np.zeros((sample_num, 224, 224, 3))
X = np.zeros((sample_num, 1000))
y = np.zeros(sample_num, dtype=int)
model = ResNet50(weights='imagenet')

cnt = 0
for lab, labname in enumerate(labelNames):
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

with open('./data.pkl', 'wb') as f:
    cPickle.dump((X[:cnt, :], y[:cnt]), f)
