from train.model import pretrained_ft, pretrained_fixed, base_model
from train.preprocess import preprocess
import logging

class predictor:
    '''
    this class is used to do predictions on the fly.
    '''
    class_names = ['disgust','excitement','anger','fear','awe','sadness','amusement','contentment','none']
    
    def __init__(self,model_path='train/local/model.h5',preprocessor="resnet"):
        '''
        init tensorflow instance
        '''
        self._processor = preprocess(preprocessor)
        logging.info("processor loaded")
        self._model = base_model()
        self._model.load(model_path)
        logging.info("model loaded")

    def predict(self, imgfile):
        
        X = self._processor.processRaw(imgfile)
        predicted_score = self._model.predict(X)[0]
        snl = [(predicted_score[i], predictor.class_names[i]) for i in range(8)]
        snl.sort(key=lambda x: x[0], reverse=True)
        return snl
	
