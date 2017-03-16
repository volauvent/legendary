'''
This module implements API to communicate with database backend.
'''
import sqlite3 as lite
import os.path
import sys
from shutil import copyfile
from PIL import Image
import imagehash
import shutil
import unittest




class utility:
    @staticmethod
    def checkFolder(path):
        if not os.path.isdir(path):
            os.makedirs(path)

    @staticmethod
    def isSelect(command):
        if (command.split(' ')[0]).lower()!='select':
            return False
        return True

    @staticmethod  
    def hashImage(image):
        """
        using average hash

        """
        # if iamge is path, read it
        if type(image) is str:
            image =Image.open(image)
        return str(imagehash.average_hash(image))


class tempFileHandler:
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
    def __init__(self,filePath):
        self.filePath=filePath
        utility.checkFolder(self.filePath+"/models")

    def getImagePath(self,name,source='other'):
        utility.checkFolder(self.filePath+"/images/"+source)
        return "%s/images/%s/%s" % (self.filePath,source,name)

    def getModelPath(self,name):
        return "%s/models/%s" % (self.filePath,name)

    def getAllFileList(self):

        return set()


class databaseAPI:

    image_table_columns=[("id","TEXT PRIMATY KEY UNIQUE"), ("path","TEXT"),("label","TEXT"),("confidence","INTEGER"),("source","TEXT"),("comment","TEXT")]
    model_table_columns=[("name","TEXT"),("path","TEXT"),("accuracy","REAL")]
    score_table_columns=[("id","INTEGER PRIMATY KEY"),("model","TEXT"),("image_id","TEXT"),("label","TEXT"),("confidence","REAL")]
    def __init__(self,dbPath=None,filePath=None):
        '''
        Initialization, either use SQL or NoSQL
        All image data and model data are stored under data folder (possibly under image and model, separately)
        The database backend should manage metadata only (i.e., store PATH to data, instead of storing data itself) to
        achieve efficiency.
        '''

        if not os.path.isfile(dbPath):
            print (dbPath+" doesn't exist, will create a new one \n")
            self.con = lite.connect(dbPath)
            # create the three tables
            create_image_table = "CREATE TABLE images (" +','.join([i+" "+j for i,j in databaseAPI.image_table_columns])+");"
            self.execute(create_image_table)
            create_model_table = "CREATE TABLE models (" +','.join([i+" "+j for i,j in databaseAPI.model_table_columns])+");"
            self.execute(create_model_table)
            create_score_table = "CREATE TABLE modelLabels (" +','.join([i+" "+j for i,j in databaseAPI.score_table_columns])+");"
            self.execute(create_score_table)
        else:
            self.con = lite.connect(dbPath)
            
        if not os.path.isdir(filePath):
            print (filePath+" doesn't exist, will create a new one \n")
            os.makedirs(filePath)
        self.dbPath=dbPath
        self.filePath=filePath
        self.fileManage=fileManager(filePath)
        
    def close(self):
        self.con.close()

    def execute(self,command):
        self.con.executescript(command)
        
    def query_meta(self,command):
        #only excute SELECT commands
        if not utility.isSelect(command):
            raise ValueError('query can only excute SELECT commands')
            return
        return self.con.execute(command).fetchall()



    def printSchemas(self):
        for (tableName,) in self.con.execute(
            """
            select NAME from SQLITE_MASTER where TYPE='table' order by NAME;
            """
        ):
            print("{}:".format(tableName))
            for (
                columnID, columnName, columnType,
                columnNotNull, columnDefault, columnPK,
            ) in self.con.execute("pragma table_info('{}');".format(tableName)):
                print("  {id}: {name}({type}){null}{default}{pk}".format(
                    id=columnID,
                    name=columnName,
                    type=columnType,
                    null=" not null" if columnNotNull else "",
                    default=" [{}]".format(columnDefault) if columnDefault else "",
                    pk=" *{}".format(columnPK) if columnPK else "",
                ))


    def insertImage(self,path,source="other",label="NULL",confidence=5,comment="NULL"):
        hashid = str(utility.hashImage(path))
        
        new_path=self.fileManage.getImagePath(hashid+"."+path.split('.')[-1],source)
        # put possible duplicate file to temp handler
        tempFile = tempFileHandler(self.filePath,new_path)

        copyfile(path, new_path)

        try:
        	self.execute("INSERT INTO images VALUES('%s','%s','%s',%d,'%s','%s')"
                    % (hashid,new_path,label,confidence,source,comment))
        except:
            os.remove(new_path)
            tempFile.copyBack()
            tempFile.remove()
            print("exception happend in SQL, command cancelled")
            raise

    def removeImage(self,image_id):
        path=self.query_meta("SELECT path FROM images WHERE id= '%s'" % image_id)[0][0]
        if path==None or path=='':
            print("not exist")
            return

        tempFile = tempFileHandler(self.filePath,path)
        try:
        	self.execute("DELETE FROM images WHERE id='%s'"%image_id)
        except:
        	tempFile.copyBack()
        	tempFile.remove()
        	print("exception happend in SQL, command cancelled")
        	raise

    def insertModel(self,path,name='',accuracy=0):
        
        new_path=self.fileManage.getModelPath(path.split('/')[-1])
        tempFile = tempFileHandler(self.filePath,new_path)
        copyfile(path, new_path)

        if name=='':
            name = path.split('/')[-1]
        try:
        	self.execute("INSERT INTO models VALUES('%s','%s',%d)"
                    % (name,new_path,accuracy))
        except:
        	tempFile.copyBack()
        	tempFile.remove()
        	print("exception happend in SQL, command cancelled")        	
        	raise

    def removeModel(self,name):
        path=self.query_meta("SELECT path FROM models WHERE name="+name)[0][0]
        if path==None or path=='':
            print("not exist")
            return
        tempFile = tempFileHandler(self.filePath,path)
        try:
        	self.execute("DELETE FROM models WHERE name="+name)
        except:
        	tempFile.copyBack()
        	tempFile.remove()
        	print("exception happend in SQL, command cancelled")
        	raise

    def insertModelLabel(self,model,image_id,label,confidence):
        self.execute("INSERT INTO modelLabels VALUES(NULL,'%s',%s,'%s',%d)"
                    % (model,image_id,label,confidence))


    def connect(self):
        """
        connect to database
        """
        pass

    def create(self):
        """
        create a table
        """
        pass

    def insert(self, data):
        """
        insert an entry
        """
        pass

    def query(self, command):
        """
        send query to backend, and get data back
        """
        return None


        
class TestDataBase(unittest.TestCase):
    def test_insert_delete(self):
        im=Image.new("RGB", (512, 512), "red")
        utility.checkFolder('testDatabase')
        im.save('testDatabase/test.jpg')
        #print(utility.hashImage(im))
        db=databaseAPI('testDatabase/test.db','testDatabase/data')
        db.insertImage('testDatabase/test.jpg')
        self.assertTrue(os.path.isfile('testDatabase/data/images/other/0000000000000000.jpg'))
        self.assertEqual(db.query_meta('SELECT * FROM images where id = "0000000000000000"'),[('0000000000000000', 'testDatabase/data/images/other/0000000000000000.jpg', 'NULL', 5, 'other', 'NULL')])
        db.removeImage('0000000000000000')
        self.assertFalse(os.path.isfile('testDatabase/data/images/other/0000000000000000.jpg'))
        self.assertEqual(db.query_meta('SELECT * FROM images where id = "0000000000000000"'),[])
        shutil.rmtree('testDatabase')
if __name__=='__main__':
    unittest.main()
