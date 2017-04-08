'''
This module implements API to communicate with database backend.
'''
import logging
import os.path
import sys
sys.path.append('../')
from connection import connectionPool


'''
                (0,'None');
                (1,'amusement');
                (2,'awe');
                (3,'contentment');
                (4,'anger');
                (5,'disgust');
                (6,'excitement');
                (7,'fear');
                (8,'sadness');
'''

class databaseAPI:
    """
    This is the API portal to grab connections
    """

    def __init__(self, dbPath=None, filePath=None):
        '''
        Initialization, either use SQL or NoSQL
        All image data and model data are stored under data folder (possibly under image and model, separately)
        The database backend should manage metadata only (i.e., store PATH to data, instead of storing data itself) to
        achieve efficiency.
        '''
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        dbType = "sqlite"
        # self.logger.addHandler(ch)
        self.__connectSQL(dbType, dbPath, filePath)

        if not os.path.isdir(filePath):
            logging.info(filePath + " doesn't exist, will create a new one \n")
            os.makedirs(filePath)

    def close(self):
        self.__pool.clear()

    def __connectSQL(self, dbType, name, filePath):
        self.__pool = connectionPool(dbType, name, filePath)
        # self.sql=myConnection(dbType,name)

    def popConnection(self):
        return self.__pool.pop()

    def appendConnection(self, connection):
        return self.__pool.append(connection)

    # ----------------------------------
    # those are just wrapper methods
    #-----------------------------------
    def execute(self, command):
        sql = self.__pool.pop()
        out = sql.execute(command)
        self.__pool.append(sql)
        return out

    def query_meta(self, command):
        sql = self.__pool.pop()
        out = sql.query_meta(command)
        self.__pool.append(sql)
        return out

    def printSchemas(self):
        sql = self.__pool.pop()
        out = sql.printSchemas()
        self.__pool.append(sql)
        return out

    def insertModelLabel(self, model, image_id, label, confidence):
        sql = self.__pool.pop()
        out = sql.insertModelLabel(model, image_id, label, confidence)
        self.__pool.append(sql)
        return out

    def removeModelLabel(self, model=None, image_id=None):
        sql = self.__pool.pop()
        out = sql.removeModelLabel(model, image_id)
        self.__pool.append(sql)
        return out

    def getRandomImageWithWeakLabel(self):
        sql = self.__pool.pop()
        out = sql.getRandomImageWithWeakLabel()
        self.__pool.append(sql)
        return out

    def insertImage(self, path, source='other', label=0, confidence=5, comment="NULL", hashid=None):
        sql = self.__pool.pop()
        out = sql.insertImage(path, source, label, confidence, comment, hashid)
        self.__pool.append(sql)
        return out

    def insertMultipleImages(self, folderPath, source='other', label=0, confidence=5, comment='NULL'):
        sql = self.__pool.pop()
        out = sql.insertMultipleImages(folderPath, source, label, confidence, comment)
        self.__pool.append(sql)
        return out

    def removeImage(self, image_id):
        sql = self.__pool.pop()
        out = sql.removeImage(image_id)
        self.__pool.append(sql)
        return out

    def insertModel(self, path, name='', accuracy=0):
        sql = self.__pool.pop()
        out = sql.insertModel(path, name, accuracy)
        self.__pool.append(sql)
        return out

    def removeModel(self, name):
        sql = self.__pool.pop()
        out = sql.removeModel(name)
        self.__pool.append(sql)
        return out

    def synchronize(self):
        sql = self.__pool.pop()
        out = sql.synchronize()
        self.__pool.append(sql)
        return out

    def insertMultipleImagesParallel(self, folderPath, hashThreadNum=2, source='other', label=0, confidence=5,
                                     comment='NULL'):
        sql = self.__pool.pop()
        out = sql.insertMultipleImagesParallel(folderPath, hashThreadNum, source, label, confidence, comment)
        self.__pool.append(sql)
        return out


if __name__ == '__main__':
    pass
