import sys
sys.path.append("../../third-party/deep-learning-models")
from resnet50 import ResNet50
from keras.preprocessing import image
from imagenet_utils import preprocess_input, decode_predictions
#import cPickle
import os
import numpy as np

labelNames = os.listdir("emotion_images/raw_images/")
sample_num = 0
for labname in labelNames:
    if labname != '.DS_Store':
        sample_num += len(os.listdir('emotion_images/raw_images/'+labname))


# rawX = np.zeros((sample_num, 224, 224, 3))
X = np.zeros((sample_num, 1000))
y = np.zeros(sample_num, dtype=int)
model = ResNet50(weights='imagenet')

cnt = 0
for lab, labname in enumerate(labelNames):
    if labname == '.DS_Store':
        continue
    imagefiles = os.listdir('emotion_images/raw_images/'+labname)
    for imagefile in imagefiles:
        img_path = 'emotion_images/raw_images/'+labname+'/'+imagefile
        img = image.load_img(img_path, target_size=(224, 224))
        #print("---", img.shape)
        x = image.img_to_array(img)
        print("---", x.shape)
        x = np.expand_dims(x, axis=0)
        #print(x.shape)
        x = preprocess_input(x)
        print(x.shape)
        # rawX[cnt, :] = x
        X[cnt, :] = model.predict(x)
        print(X.shape)
        y[cnt] = lab
        cnt += 1

        if cnt%100 == 0:
            print(cnt)
            # break

with open('./data.pkl', 'wb') as f:
    cPickle.dump((X[:cnt, :], y[:cnt]), f)
