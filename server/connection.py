import logging
import multiprocessing as mp
import os.path
import sqlite3 as lite
import threading
from shutil import copyfile

import dbUtility
from sqlWrapper import sqliteWrapper


class myConnection():
    '''
    this is the connection object
    '''

    def __init__(self, dbtype, dbPath, filePath, lock):
        if dbtype == "sqlite":
            self.db = sqliteWrapper(dbPath)
        self.filePath = filePath
        self.fileManage = dbUtility.fileManager(filePath)
        self.lock = lock

    def close(self):
        return self.db.close()

    def execute(self, command):
        return self.db.execute(command)

    def query_meta(self, command):
        return self.db.query_meta(command)

    def printSchemas(self):
        string = []
        for (tableName,) in self.query_meta(
                """
            select NAME from SQLITE_MASTER where TYPE='table' order by NAME;
            """
        ):
            string.append("{}:\n".format(tableName))
            for (
                    columnID, columnName, columnType,
                    columnNotNull, columnDefault, columnPK,
            ) in self.execute("pragma table_info('{}');".format(tableName)):
                string.append("  {id}: {name}({type}){null}{default}{pk} \n".format(
                    id=columnID,
                    name=columnName,
                    type=columnType,
                    null=" not null" if columnNotNull else "",
                    default=" [{}]".format(columnDefault) if columnDefault else "",
                    pk=" *{}".format(columnPK) if columnPK else "",
                ))
        return "".join(string)

    def insertModelLabel(self, model, image_id, label, confidence):
        self.execute("INSERT INTO modelLabels VALUES(NULL,'%s','%s',%d,%d)"
                     % (model, image_id, int(label), float(confidence)))
        return True

    def removeModelLabel(self, model=None, image_id=None):
        if model is not None and image_id is not None:
            self.execute("DELETE FROM modelLabels WHERE model='%s' AND image_id='%s'" % (model, image_id))
        elif model is None and image_id is not None:
            self.execute("DELETE FROM modelLabels WHERE image_id='%s'" % image_id)
        elif model != None and image_id is None:
            self.execute("DELETE FROM modelLabels WHERE model='%s'" % model)
        return True

    def getRandomImageWithWeakLabel(self):
        '''
        this method is suppose to return a random image with weak labels
        '''
        count = self.query_meta("SELECT COUNT(*) FROM modelLabels")[0][0]
        #imagecount = self.query_meta("SELECT COUNT(*) FROM images WHERE label=0")[0][0]

        # if imagecount!=0 and random.random()>(count/(imagecount)) and False:
        #    image=self.query_meta("SELECT path,id FROM images WHERE label=0 ORDER BY RANDOM() LIMIT 1")
        #    return {"path":os.path.abspath(image[0][0]),"id":image[0][1],"labels":list(range(1,9))}

        # if there are no weak labels, we return a image with label none and all 8 classes.
        if count == 0:
            image = self.query_meta("SELECT path,id FROM images WHERE label=0 ORDER BY RANDOM() LIMIT 1")
            if len(image) == 0:
                raise Exception("there's no weak label image")
            return {"path": os.path.abspath(image[0][0]), "id": image[0][1], "labels": list(range(1, 9))}
        else:
            entry = self.query_meta("SELECT image_id FROM modelLabels ORDER BY RANDOM() LIMIT 1")[0][0]
            labels = self.query_meta("SELECT label FROM modelLabels WHERE image_id = '%s'" % entry)
            path = self.query_meta("SELECT path FROM images WHERE id='%s'" % entry)[0][0]
            return {"path": os.path.abspath(path), "id": entry, "labels": list(set([i[0] for i in labels]))}

    def insertImage(self, path, source='other', label=0, confidence=5, comment="NULL", hashid=None):
        with self.lock:
            self.__insertImage(path, source, label, confidence, comment, hashid)

    def insertMultipleImages(self, folderPath, source='other', label=0, confidence=5, comment='NULL'):
        with self.lock:
            self.__insertMultipleImages(folderPath, source, label, confidence, comment)

    def removeImage(self, image_id):
        with self.lock:
            self.__removeImage(image_id)

    def insertModel(self, path, name='', accuracy=0):
        with self.lock:
            self.__insertModel(path, name, accuracy)

    def removeModel(self, name):
        with self.lock:
            self.__removeModel(name)

    def synchronize(self):
        with self.lock:
            self.__synchronize()

    def insertMultipleImagesParallel(self, folderPath, hashThreadNum=2, source='other', label=0, confidence=5,
                                     comment='NULL'):
        with self.lock:
            self.__insertMultipleImagesParallel(folderPath, hashThreadNum, source, label, confidence, comment)

    def __insertImage(self, path, source='other', label=0, confidence=5, comment="NULL", hashid=None):

        if hashid == None:
            hashid = str(dbUtility.utility.hashImage(path))
        new_path = self.fileManage.getImagePath(hashid + "." + path.split('.')[-1], source)
        # put possible duplicate file to temp handler
        if path != new_path:
            tempFile = dbUtility.tempFileHandler(self.filePath, new_path)
        else:
            tempFile = dbUtility.tempFileHandler(self.filePath, '')

        copyfile(path, new_path)

        try:
            self.execute("INSERT INTO images VALUES('%s','%s',%d,%d,'%s','%s')"
                         % (hashid, new_path, int(label), int(confidence), source, comment))
        except lite.IntegrityError:
            os.remove(new_path)
            tempFile.copyBack()
            tempFile.remove()
            logging.warning("%s duplicated entry, insert reverted" % (hashid))
            return "%s duplicated entry, insert reverted" % (hashid)

        except:
            # with exception, roll back
            os.remove(new_path)
            tempFile.copyBack()
            tempFile.remove()
            logging.error("exception happened in SQL, command cancelled")
            raise
        # If the file is in file system, remove it for duplication
        if (self.filePath in path) and path != new_path:
            os.remove(path)
        return hashid

    def __insertMultipleImages(self, folderPath, source='other', label=0, confidence=5, comment='NULL'):
        for root, dirs, files in os.walk(folderPath):
            for file in files:
                if file != ".DS_Store":
                    logging.info("%s inserting" % (file))
                    self.insertImage(root + os.sep + file, source, int(label), int(confidence), comment)
        return True

    def __removeImage(self, image_id):
        path = self.query_meta("SELECT path FROM images WHERE id= '%s'" % image_id)[0][0]
        if path == None or path == '':
            logging.warning("not exist")
            return

        tempFile = dbUtility.tempFileHandler(self.filePath, path)
        try:
            self.execute("DELETE FROM images WHERE id='%s'" % image_id)
        except:
            tempFile.copyBack()
            tempFile.remove()
            logging.error("exception happend in SQL, command cancelled")
            raise
        return True

    def __insertModel(self, path, name='', accuracy=0):

        new_path = self.fileManage.getModelPath(path.split('/')[-1])

        if new_path != path:
            tempFile = dbUtility.tempFileHandler(self.filePath, new_path)
        else:
            tempFile = dbUtility.tempFileHandler(self.filePath, '')

        copyfile(path, new_path)

        if name == '':
            name = path.split('/')[-1]
        try:
            self.execute("INSERT INTO models VALUES('%s','%s',%d)"
                         % (name, new_path, float(accuracy)))
        except:
            tempFile.copyBack()
            tempFile.remove()
            logging.error("exception happend in SQL, command cancelled")
            raise
        return True

    def __removeModel(self, name):
        path = self.query_meta("SELECT path FROM models WHERE name=" + name)[0][0]
        if path == None or path == '':
            print("not exist")
            return
        tempFile = dbUtility.tempFileHandler(self.filePath, path)
        try:
            self.execute("DELETE FROM models WHERE name=" + name)
        except:
            tempFile.copyBack()
            tempFile.remove()
            logging.error("exception happend in SQL, command cancelled")
            raise
        return True

    def __synchronize(self):
        """
        check whether sqlDB and file system is consistent
        """
        logging.info("checking images")
        files = self.fileManage.getAllImageList()
        rows = self.query_meta("SELECT path, id from images")
        for row in rows:
            if row[0] not in files:
                logging.warning("%s not in file system" % (row[1]))
                self.removeImage(row[1])
            else:
                files.discard(row[0])
        if len(files) != 0:
            for file in files:
                logging.warning("%s not in database" % file)
                self.insertImage(file, file.split('/')[-2])
        logging.info("checking models")
        files = self.fileManage.getAllModelList()
        rows = self.query_meta("SELECT path, name from models")
        for row in rows:
            if row[0] not in files:
                logging.warning("%s not in file system" % (row[1]))
                self.removeModel(row[1])
            else:
                files.discard(row[0])
        if len(files) != 0:
            for file in files:
                logging.warning("%s not in database" % (file))
                self.insertModel(file)
        logging.info("Done")
        return True

    @staticmethod
    def feedprocess(path, source, label, confidence, comment, num_workers, inq, outq):
        workers = [mp.Process(target=myConnection.hasherProcess, args=(inq, outq)) for i in range(num_workers)]
        # printer=mp.Process(target=test.f3,args=(outq,))

        for w in workers:
            w.start()
        # printer.start()

        for root, dirs, files in os.walk(path):
            for file in files:
                if file != ".DS_Store":
                    # print("feed %s" % file)
                    inq.put([root + os.sep + file, source, label, confidence, comment])
        for i in range(num_workers):
            inq.put(None)

        for w in workers:
            w.join()
        outq.put(None)
        # printer.join()

    @staticmethod
    def hasherProcess(inq, outq):
        while True:
            val = inq.get()
            if val is None:
                break
            hashed = dbUtility.utility.hashImage(val[0])
            # print(val[0])
            val.append(hashed)
            outq.put(val)

    def __insertMultipleImagesParallel(self, folderPath, hashThreadNum=2, source='other', label=0, confidence=5,
                                       comment='NULL'):
        inq = mp.Queue()
        outq = mp.Queue()
        feeder = mp.Process(target=myConnection.feedprocess,
                            args=(folderPath, source, int(label), int(confidence), comment, hashThreadNum, inq, outq))
        # self.insertImage(root+os.sep+file,source,label,confidence,comment)

        feeder.start()
        # db=database.databaseAPI('test.db','data')
        while True:
            val = outq.get()
            if val is None:
                break
            self.insertImage(*val)
            print(val)


class connectionPool:
    def __init__(self, dbType, location, filePath):
        self.dbType = dbType
        self.location = location
        self.connectionPool = []
        self.filePath = filePath
        self.lock = threading.RLock()

    def pop(self):
        if len(self.connectionPool) > 0:
            return self.connectionPool.pop()
        else:
            return myConnection(self.dbType, self.location, self.filePath, self.lock)

    def append(self, connection):
        self.connectionPool.append(connection)

    def clear(self):
        while len(self.connectionPool) > 0:
            i = self.connectionPool.pop()
            i.close()