'''
Database server module

This module implements a database server for emotional data management.
1. Provides API for training module to fetch training data and store trained models.
2. Provides API for frontEnd module to demonstrate model performance, as well as storing new labels by mechanic turk.
3. It inherits from baseServer. It uses database module as the backend.
'''

import multiprocessing
import sys
sys.path.append('./')
from baseServer import baseServer
from database import databaseAPI
from configparser import ConfigParser
from train.model import pretrained_ft, pretrained_fixed, base_model
from train.preprocess import preprocess
import logging

class dbServer(baseServer):
    labels=['None',
                'amusement',
                'awe',
                'contentment',
                'anger',
                'disgust',
                'excitement',
                'fear',
                'sadness']
    def predict(self, imgfile):
        class_names = ['disgust','excitement','anger','fear','awe','sadness','amusement','contentment','none']
        X = self._processor.processRaw(imgfile)
        predicted_score = self._model.predict(X)[0]
        snl = [(predicted_score[i], class_names[i]) for i in range(8)]
        snl.sort(key=lambda x: x[0], reverse=True)
        return snl

    def predict_and_insert(self,folderPath,source='other',label=0,confidence=5,comment='NULL'):
        top2=self.predict(folderPath)[:2]
        logging.info(str(top2))
        hashid=self._database.insertImage(folderPath,source,label,confidence,comment).split(' ')[0]
        logging.info(hashid)
        self._database.insertModelLabel("testing",hashid,self.labels.index(top2[0][1].lower()),top2[0][0])
        self._database.insertModelLabel("testing",hashid,self.labels.index(top2[1][1].lower()),top2[1][0])
        return True
        
    def __init__(self,portNum=None):
        self.parser = ConfigParser()
        self.parser.read('config.ini')
        if portNum==None:
            portNum=int(self.parser.get('dbServer','port'))
        host = self.parser.get('dbServer','host')
        db=self.parser.get('dbServer','database')
        data=self.parser.get('dbServer','fileSystem')

        super(dbServer, self).__init__(portNum,host)
        self._processor = preprocess("resnet")
        logging.info("processor loaded")
        self._model = base_model()
        self._model.load('train/local/model.h5')
        logging.info("model loaded")

        logging.info("server:  server starting, listening on port")

        # % str(portNum))

        self._database = databaseAPI(db,data)

    def process(self, dat, conn):
        """
        Process message from frontEnd
        Messages are stored in dat (a dict)
        Use self._database to communicate with database backend
        Use multi-threading to support concurrent usage
        """

        '''
        Example
        '''
        try:
            logging.info("server: command received %s" % str(dat))
            task = dat['task']
            command = dat.get('command',None)

            if task == "query_meta":
                result = self._database.query_meta(command)

            elif task == "insertImage":
                result = self._database.insertImage(*command)

            elif task == "insertModel":
                result = self._database.insertModel(*command)

            elif task == "insertModelLabel":
                result = self._database.insertModelLabel(*command)

            elif task == "insertMultipleImagesParallel":
                result = self._database.insertMultipleImagesParallel(*command)

            elif task =="getRandomImageWithWeakLabel":
                result = self._database.getRandomImageWithWeakLabel()

            elif task =="predict":
                result = self.predict(command)[0][1]

            elif task =="predict_and_insert":
                result = self.predict_and_insert(*command)


        except Exception as e:
            return str(e)
        return result

    def process_offline(self):
        """
        API for offline jobs.
        Example: Performance analysis, database organization.
        :return:
        """


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) > 1:
        server = dbServer(int(sys.argv[1]))
    else:
        server = dbServer()
    server.start()