import os
import sys
from PIL import Image
from shutil import copyfile
import imagehash




class utility:
    labels = ['None',
              'amusement',
              'awe',
              'contentment',
              'anger',
              'disgust',
              'excitement',
              'fear',
              'sadness']
    image_table_columns = [("id", "TEXT PRIMATY KEY UNIQUE"), ("path", "TEXT"), ("label", "INTEGER"),
                           ("confidence", "INTEGER"), ("source", "TEXT"), ("comment", "TEXT")]
    model_table_columns = [("name", "TEXT"), ("path", "TEXT"), ("accuracy", "REAL")]
    score_table_columns = [("id", "INTEGER PRIMARY KEY"), ("model", "TEXT"), ("image_id", "TEXT"), ("label", "INTEGER"),
                           ("confidence", "REAL")]
    labeltype_table_columns = [("id", "INTEGER PRIMARY KEY"), ("name", "TEXT")]

    @staticmethod
    def checkStrong(topCount,totalCount):
        totalCountThreshold=5
        ratioThreshold=0.6
        return (totalCount>=totalCountThreshold and topCount/totalCount>ratioThreshold)

    @staticmethod
    def checkFolder(path):
        if not os.path.isdir(path):
            os.makedirs(path)

    @staticmethod
    def isSelect(command):
        first=(command.strip().split(' ')[0]).lower()
        if first!='select' and first!='pragma':
            return False
        return True

    @staticmethod
    def hashImage(image):
        """
        using p hash

        """
        # if iamge is path, read it
        if type(image) is str:
            image =Image.open(image)
        return str(imagehash.phash(image))


class tempFileHandler:
    """
    this class handles temporary files
    """
    def __init__(self,folderPath,file):
        if os.path.isfile(file):
            self.originalPath = file
            self.tempPath = folderPath+"/temp/"+file.split("/")[-1]
            utility.checkFolder(folderPath+"/temp")
            copyfile(self.originalPath, self.tempPath)
            os.remove(self.originalPath)
        else:
            self.tempPath=None
    def remove(self):
        if self.tempPath!=None:
            os.remove(self.tempPath)
    def copyBack(self):
        if self.tempPath!=None:
            copyfile(self.tempPath,self.originalPath)

class fileManager:
    """
    this class manages file system locations
    """
    def __init__(self,filePath):
        self.filePath=filePath
        utility.checkFolder(self.filePath+"/models")

    def getImagePath(self,name,source='source'):
        utility.checkFolder(self.filePath+"/images/"+str(source))
        return "%s/images/%s/%s" % (self.filePath,str(source),name)

    def getModelPath(self,name):
        return "%s/models/%s" % (self.filePath,name)

    def getAllImageList(self):
        pathSet=set()
        for root, dirs, files in os.walk(self.filePath+"/images"):
            path = root.split(os.sep)
            for file in files:
                if file != ".DS_Store":
                    pathSet.add(root+os.sep+file)
        return pathSet

    def getAllModelList(self):
        pathSet=set()
        for root, dirs, files in os.walk(self.filePath+"/models"):
            path = root.split(os.sep)
            for file in files:
                if file != ".DS_Store":
                    pathSet.add(root+os.sep+file)
        return pathSet