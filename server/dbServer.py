'''
Database server module

This module implements a database server for emotional data management.
1. Provides API for training module to fetch training data and store trained models.
2. Provides API for frontEnd module to demonstrate model performance, as well as storing new labels by mechanic turk.
3. It inherits from baseServer. It uses database module as the backend.
'''

import multiprocessing
import sys
sys.path.append('../')
from baseServer import baseServer
from database import databaseAPI
from configparser import SafeConfigParser
from train.model import pretrained_ft, pretrained_fixed, base_model
from train.preprocess import preprocess


class dbServer(baseServer):

    def predict(self,imgfile):
        class_names = labels=['disgust','excitement','anger','fear','awe','sadness','amusement','contentment','none']
        processor = preprocess("resnet")
        model = base_model()
        model.load('../train/local/model.h5')
        model.summary()
        X = processor.processRaw(imgfile)
        predicted_label = class_names[model.predict_classes(X)[0]]
        return predicted_label

    def __init__(self,portNum=None):
        self.parser = SafeConfigParser()
        self.parser.read('config.ini')
        if portNum==None:
            portNum=int(self.parser.get('dbServer','port'))
        host = self.parser.get('dbServer','host')
        db=self.parser.get('dbServer','database')
        data=self.parser.get('dbServer','fileSystem')

        super(dbServer, self).__init__(portNum,host)
        self._database = databaseAPI('test.db','data')

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
            print(dat)
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
                result = self.predict(command)

            


        except Exception as e:
            result=e
            raise
        return result

    def process_offline(self):
        """
        API for offline jobs.
        Example: Performance analysis, database organization.
        :return:
        """


if __name__ == "__main__":
    if len(sys.argv) > 1:
        server = dbServer(int(sys.argv[1]))
    else:
        server = dbServer()
    server.start()