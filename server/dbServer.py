'''
Database server module

This module implements a database server for emotional data management.
1. Provides API for training module to fetch training data and store trained models.
2. Provides API for frontEnd module to demonstrate model performance, as well as storing new labels by mechanic turk.
3. It inherits from baseServer. It uses database module as the backend.
'''

import multiprocessing
import sys
import os
from os.path import isfile, join
sys.path.append('./')
from baseServer import baseServer
from database import databaseAPI
from configparser import ConfigParser
from predictor import predictor
import logging

class dbServer(baseServer):

    @staticmethod
    def isImg(file):
        imgExtensions=['.jpg','.png']
        file=file.lower()
        for i in imgExtensions:
            if i in file:
                return True
        return False

    def predictAndInsert(self,filePath,source='other',label=0,confidence=5,comment='NULL'):
        top2=self._predictor.predict(filePath)[:2]
        logging.info(str(top2))
        hashid=self._database.insertImage(filePath,source,label,confidence,comment).split(' ')[0]
        logging.info(hashid)
        self._database.insertModelLabel("testing",hashid,databaseAPI.labels.index(top2[0][1].lower()),top2[0][0])
        self._database.insertModelLabel("testing",hashid,databaseAPI.labels.index(top2[1][1].lower()),top2[1][0])
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

        self._predictor = predictor()

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
                result = self._predictor.predict(command)[0][1]

            elif task =="predict_and_insert":
                result = self.predictAndInsert(*command)


        except Exception as e:
            return str(e)
        logging.info(str(result))
        return result


    def PredictAndInsertMany(self,folderPath="frontend/upload",source='other',label=0,confidence=5,comment='NULL'):
        """
        API for online predict and insert a folder of images
        """
        #find all jpg and png files inside

        onlyfiles = [f for f in os.listdir(folderPath) if (
            os.path.isfile(os.path.join(folderPath, f)) and dbServer.isImg(f))]

        for f in onlyfiles:
            # print(f)
            logging.info(f+str(self.predictAndInsert(f,source,label,confidence,comment)))
        logging.info("Done")



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) > 1:
        server = dbServer(int(sys.argv[1]))
    else:
        server = dbServer()
    server.start()