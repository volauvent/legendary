'''
This module implements API to communicate with database backend.
'''
import sqlite3 as lite
import os.path
import sys
from shutil import copyfile
from PIL import Image
import imagehash

import unittest




class utility:
    @staticmethod
    def checkFolder(path):
        if not os.path.isdir(path):
            os.makedirs(path)

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

class databaseAPI:

    image_table_columns=[("id","TEXT PRIMATY KEY"), ("path","TEXT"),("label","TEXT"),("confidence","INTEGER"),("source","TEXT"),("comment","TEXT")]
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
            print (dbPath+" doesn't exist, do you wish to create a new one?[Y/N] \n")
            feedback = input()
            if str(feedback).lower() not in ["y","yes"]:
                print("exiting")
                sys.exit()
            else:
                self.con = lite.connect(dbPath)
                create_image_table = "CREATE TABLE images (" +','.join([i+" "+j for i,j in databaseAPI.image_table_columns])+");"
                self.execute(create_image_table)
                create_model_table = "CREATE TABLE models (" +','.join([i+" "+j for i,j in databaseAPI.model_table_columns])+");"
                self.execute(create_model_table)
                create_score_table = "CREATE TABLE modelLabels (" +','.join([i+" "+j for i,j in databaseAPI.score_table_columns])+");"
                self.execute(create_score_table)
        else:
            self.con = lite.connect(dbPath)
            
        if not os.path.isdir(filePath):
            print (filePath+" doesn't exist, do you wish to create a new one?[Y/N] \n")
            feedback = input()
            if str(feedback).lower() not in ["y","yes"]:
                print("exiting")
                sys.exit()
            else:
                os.makedirs(filePath)
        self.dbPath=dbPath
        self.filePath=filePath
        
    def close(self):
        self.con.close()
        
    def execute(self,command):
        self.con.executescript(command)
        
    def query_meta(self,command):
        return self.con.execute(command).fetchall()

    @staticmethod
    def checkFolder(path):
        if not os.path.isdir(path):
            os.makedirs(path)

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
    @staticmethod  
    def hashImage(path):
    	"""
    	using average hash

    	"""
    	return str(imagehash.average_hash(Image.open(path)))




    def insertImage(self,path,source="other",label="NULL",confidence=5,comment="NULL"):
        hashid = str(imagehash.average_hash(Image.open(path)))
        self.checkFolder(self.filePath+"/images/"+source)
        new_path=self.filePath+"/images/"+source+"/"+hashid+"."+path.split('.')[-1]
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
        #print(path)
        #sys.exit()

        tempFile = tempFileHandler(self.filePath,path)
        try:
        	self.execute("DELETE FROM images WHERE id='%s'"%image_id)
        except:
        	tempFile.copyBack()
        	tempFile.remove()
        	print("exception happend in SQL, command cancelled")
        	raise

    def insertModel(self,name,path,accuracy):
        checkFolder(self.filePath+"/models")
        new_path=self.filePath+"/models/"+path.split('/')[-1]
        tempFile = tempFileHandler(self.filePath,new_path)
        copyfile(path, new_path)
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
        db=databaseAPI('test.db','data')
        db.insertImage('excitement.jpg')
        self.assertTrue(os.path.isfile('data/images/other/8080707efec1c3f7.jpg'))
        self.assertEqual(db.query_meta('SELECT * FROM images where id = "8080707efec1c3f7"'),[('8080707efec1c3f7', 'data/images/other/8080707efec1c3f7.jpg', 'NULL', 5, 'other', 'NULL')])
        db.removeImage('8080707efec1c3f7')
        self.assertFalse(os.path.isfile('data/images/other/8080707efec1c3f7.jpg'))
        self.assertEqual(db.query_meta('SELECT * FROM images where id = "8080707efec1c3f7"'),[])
if __name__=='__main__':
    unittest.main()
