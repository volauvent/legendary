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
import logging


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


class databaseAPI:

    image_table_columns=[("id","TEXT PRIMATY KEY UNIQUE"), ("path","TEXT"),("label","INTEGER"),("confidence","INTEGER"),("source","TEXT"),("comment","TEXT")]
    model_table_columns=[("name","TEXT"),("path","TEXT"),("accuracy","REAL")]
    score_table_columns=[("id","INTEGER PRIMARY KEY"),("model","TEXT"),("image_id","TEXT"),("label","INTEGER"),("confidence","REAL")]
    labeltype_table_columns=[("id","INTEGER PRIMARY KEY"),("name","TEXT")]
    def __init__(self,dbPath=None,filePath=None):
        '''
        Initialization, either use SQL or NoSQL
        All image data and model data are stored under data folder (possibly under image and model, separately)
        The database backend should manage metadata only (i.e., store PATH to data, instead of storing data itself) to
        achieve efficiency.
        '''
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)


        if not os.path.isfile(dbPath):
            self.logger.info(dbPath+" doesn't exist, will create a new one \n")
            self.con = self.__connect(dbPath)
            # create the three tables
            self.__initDB()

        else:
            self.con = self.__connect(dbPath)
            
        if not os.path.isdir(filePath):
            self.logger.info(filePath+" doesn't exist, will create a new one \n")
            os.makedirs(filePath)
        self.dbPath=dbPath
        self.filePath=filePath
        self.fileManage=fileManager(filePath)

    def __initDB(self):
            create_image_table = "CREATE TABLE images (" +','.join([i+" "+j for i,j in databaseAPI.image_table_columns])+");"
            self.execute(create_image_table)
            create_model_table = "CREATE TABLE models (" +','.join([i+" "+j for i,j in databaseAPI.model_table_columns])+");"
            self.execute(create_model_table)
            create_score_table = "CREATE TABLE modelLabels (" +','.join([i+" "+j for i,j in databaseAPI.score_table_columns])+");"
            self.execute(create_score_table)
            create_labeltype_table = "CREATE TABLE labelType (" +','.join([i+" "+j for i,j in databaseAPI.labeltype_table_columns])+");"
            self.execute(create_labeltype_table)
            self.execute("""
                INSERT INTO labelType VALUES(0,'None');
                INSERT INTO labelType VALUES(1,'amusement');
                INSERT INTO labelType VALUES(2,'owe');
                INSERT INTO labelType VALUES(3,'contentment');
                INSERT INTO labelType VALUES(4,'anger');
                INSERT INTO labelType VALUES(5,'disgust');
                INSERT INTO labelType VALUES(6,'excitement');
                INSERT INTO labelType VALUES(7,'fear');
                INSERT INTO labelType VALUES(8,'sadness');
                """)


    def close(self):
        self.con.close()

    def __connect(self,name):
        
        try:
            conn = lite.connect(name)
            return conn
        except:
            e = sys.exc_info()[0]
            self.logger.error(e)
     
        return None

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


    def insertImage(self,path,source='other',label=0,confidence=5,comment="NULL"):
        hashid = str(utility.hashImage(path))
        
        new_path=self.fileManage.getImagePath(hashid+"."+path.split('.')[-1],source)
        # put possible duplicate file to temp handler
        if path!=new_path:
            tempFile = tempFileHandler(self.filePath,new_path)
        else:
            tempFile=tempFileHandler(self.filePath,'')

        copyfile(path, new_path)

        try:
        	self.execute("INSERT INTO images VALUES('%s','%s',%d,%d,'%s','%s')"
                    % (hashid,new_path,label,confidence,source,comment))
        except lite.IntegrityError:
            os.remove(new_path)
            tempFile.copyBack()
            tempFile.remove()
            self.logger.warning("%s duplicated entry, insert reverted" % (hashid))
            raise
        except:
            # with exception, roll back
            os.remove(new_path)
            tempFile.copyBack()
            tempFile.remove()
            self.logger.error("exception happend in SQL, command cancelled")
            raise
        # If the file is in file system, remove it for duplication
        if (self.filePath in path) and path!=new_path:
            os.remove(path)

    def removeImage(self,image_id):
        path=self.query_meta("SELECT path FROM images WHERE id= '%s'" % image_id)[0][0]
        if path==None or path=='':
            self.logger.warning("not exist")
            return

        tempFile = tempFileHandler(self.filePath,path)
        try:
        	self.execute("DELETE FROM images WHERE id='%s'"%image_id)
        except:
        	tempFile.copyBack()
        	tempFile.remove()
        	self.logger.error("exception happend in SQL, command cancelled")
        	raise

    def insertModel(self,path,name='',accuracy=0):
        
        new_path=self.fileManage.getModelPath(path.split('/')[-1])

        
        if new_path!=path:
            tempFile = tempFileHandler(self.filePath,new_path)
        else:
            tempFile=tempFileHandler(self.filePath,'')

        copyfile(path, new_path)

        if name=='':
            name = path.split('/')[-1]
        try:
        	self.execute("INSERT INTO models VALUES('%s','%s',%d)"
                    % (name,new_path,accuracy))
        except:
        	tempFile.copyBack()
        	tempFile.remove()
        	self.logger.error("exception happend in SQL, command cancelled")        	
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
        	self.logger.error("exception happend in SQL, command cancelled")
        	raise

    def insertModelLabel(self,model,image_id,label,confidence):
        self.execute("INSERT INTO modelLabels VALUES(NULL,'%s','%s',%d,%d)"
                    % (model,image_id,label,confidence))

    def deleteModelLabel(self,model=None,image_id=None):
        if model!=None and image_id!=None:
            self.execute("DELETE FROM modelLabels WHERE model='%s' AND image_id='%s'" % (model,image_id))
        elif model==None and image_id!=None:
            self.execute("DELETE FROM modelLabels WHERE image_id='%s'" % (image_id))
        elif model!=None and image_id==None:
            self.execute("DELETE FROM modelLabels WHERE model='%s'" % (model))


    def synchronize(self):
        """
        check whether sqlDB and file system is consistent
        """
        self.logger.info("checking images")
        files=self.fileManage.getAllImageList()
        rows=self.query_meta("SELECT path, id from images")
        for row in rows:
            if row[0] not in files:
                self.logger.warning("%s not in file system" % row[1])
                self.removeImage(row[1])
            else:
                files.discard(row[0])
        if len(files)!=0:
            for file in files:
                self.logger.warning("%s not in database" % file)
                self.insertImage(file,file.split('/')[-2])
        self.logger.info("checking models")
        files=self.fileManage.getAllModelList()
        rows=self.query_meta("SELECT path, name from models")
        for row in rows:
            if row[0] not in files:
                self.logger.warning("%s not in file system" % row[1])
                self.removeModel(row[1])
            else:
                files.discard(row[0])
        if len(files)!=0:
            for file in files:
                self.logger.warning("%s not in database" % file)
                self.insertModel(file)
        self.logger.info("Done")



        
class TestDataBase(unittest.TestCase):
    def test_insert_delete_image(self):
        utility.checkFolder('testDatabase')
        db=databaseAPI('testDatabase/test.db','testDatabase/data')
        try:
            im=Image.new("RGB", (512, 512), "red")
            im.save('testDatabase/test.jpg')
            #print(utility.hashImage(im))
            
            db.insertImage('testDatabase/test.jpg')
            self.assertTrue(os.path.isfile('testDatabase/data/images/other/0000000000000000.jpg'))
            self.assertEqual(db.query_meta('SELECT * FROM images where id = "0000000000000000"'),[('0000000000000000', 'testDatabase/data/images/other/0000000000000000.jpg', 0, 5, 'other', 'NULL')])
            db.removeImage('0000000000000000')
            self.assertFalse(os.path.isfile('testDatabase/data/images/other/0000000000000000.jpg'))
            self.assertEqual(db.query_meta('SELECT * FROM images where id = "0000000000000000"'),[])
        finally:
            shutil.rmtree('testDatabase')
    def test_sync(self):
        utility.checkFolder('testDatabase/data/images/you')
        db=databaseAPI('testDatabase/test.db','testDatabase/data')
        try:
            im=Image.new("RGB", (512, 512), "red")
            
            im.save('testDatabase/test.jpg')
            db.insertImage('testDatabase/test.jpg')
            im2=Image.new("RGB", (512, 512))
            data=[(i//3,0,i//3) for i in range(512)]
            im2.putdata(data)
            im2.save('testDatabase/data/images/you/asd.jpg')
            shutil.rmtree('testDatabase/data/images/other')
            db.synchronize()
            self.assertTrue(os.path.isfile('testDatabase/data/images/you/f800000000000000.jpg'))
            self.assertFalse(os.path.isfile('testDatabase/data/images/you/asd.jpg'))
            self.assertEqual(db.query_meta("SELECT * FROM images"),[('f800000000000000', 'testDatabase/data/images/you/f800000000000000.jpg', 0, 5, 'you', 'NULL')])
        finally:
            shutil.rmtree('testDatabase')


    def test_insert_remove_model(self):
        pass

    def test_insert_remove_model_labels(self):
        pass

    def test_update(self):
        pass

if __name__=='__main__':
    unittest.main()
