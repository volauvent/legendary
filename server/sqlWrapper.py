import logging
import os.path
import sqlite3 as lite
import sys
import dbUtility

"""
Add all SQL DB wrapper here.

please implement all methods
"""


def sqlWrapperFinder(dbtype, dbPath):
    """
    This is the wrapper finder, add new wrapper after it
    :param dbtype: name of db, ex: sqlite
    :param dbPath: connection method, ex: connection string in sqlite
    :return: db connection instance
    """
    if dbtype == "sqlite":
        return sqliteWrapper(dbPath)


class AbstractWrapper(object):
    """
    this is the abstractWrapper, implement it in your wrapper

    in init, it should take in one input that contains your connection info.
    It should also check to see whether that DB exist and init it if required
    """

    def __init__(self, dbPath):
        try:
            exist = self.checkDB(dbPath)

            if not exist:
                logging.info(dbPath + " doesn't exist, will create a new one \n")
                self.con=self.initDB(dbPath)
            else:
                self.con = self.connect(dbPath)
        except:

            e = sys.exc_info()[0]
            logging.error(e)
            sys.exit(0)

    def connect(self, dbPath):
        """
        return an original connection object
        :param dbPath:
        :return: connection object
        """
        raise NotImplementedError("Should have implemented this")

    def checkDB(self, dbPath):
        """
        check whether this DB exist and contains required tables
        :param dbPath: connection into
        :return: bool
        """
        raise NotImplementedError("Should have implemented this")

    def initDB(self,dbPath):
        """
        initialize the database if not properly
        return: connction
        """
        raise NotImplementedError("Should have implemented this")

    def close(self):
        raise NotImplementedError("Should have implemented this")

    def execute(self, command):
        """
        execute a SQL command, mainly for changing the DB
        :param command:
        :return:
        """
        raise NotImplementedError("Should have implemented this")

    def query_meta(self, command):
        """
        query a SELECT and return. Should be read-only
        :param command:
        :return:
        """
        raise NotImplementedError("Should have implemented this")

class sqliteWrapper(AbstractWrapper):
    '''
    this is a wrapper of sqlite
    '''

    def __init__(self, dbPath):
        try:
            exist = self.checkDB(dbPath)

            if not exist:
                logging.info(dbPath + " doesn't exist, will create a new one \n")
                self.con=self.initDB(dbPath)
            else:
                self.con = self.connect(dbPath)
        except:

            e = sys.exc_info()[0]
            logging.error(e)
            sys.exit(0)

    def connect(self,dbPath):
        return lite.connect(dbPath)

    def checkDB(self, dbPath):
        return os.path.isfile(dbPath)

    def initDB(self,dbPath):
        self.con=self.connect(dbPath)
        create_image_table = "CREATE TABLE images (" + ','.join(
            [i + " " + j for i, j in dbUtility.utility.image_table_columns]) + ");"
        self.execute(create_image_table)
        create_model_table = "CREATE TABLE models (" + ','.join(
            [i + " " + j for i, j in dbUtility.utility.model_table_columns]) + ");"
        self.execute(create_model_table)
        create_score_table = "CREATE TABLE modelLabels (" + ','.join(
            [i + " " + j for i, j in dbUtility.utility.score_table_columns]) + ");"
        self.execute(create_score_table)
        create_labeltype_table = "CREATE TABLE labelType (" + ','.join(
            [i + " " + j for i, j in dbUtility.utility.labeltype_table_columns]) + ");"
        self.execute(create_labeltype_table)
        self.execute("""
            INSERT INTO labelType VALUES(0,'None');
            INSERT INTO labelType VALUES(1,'amusement');
            INSERT INTO labelType VALUES(2,'awe');
            INSERT INTO labelType VALUES(3,'contentment');
            INSERT INTO labelType VALUES(4,'anger');
            INSERT INTO labelType VALUES(5,'disgust');
            INSERT INTO labelType VALUES(6,'excitement');
            INSERT INTO labelType VALUES(7,'fear');
            INSERT INTO labelType VALUES(8,'sadness');
            """)
        return self.con

    def close(self):
        self.con.close()
        return True

    def execute(self, command):
        return self.con.executescript(command)

    def query_meta(self, command):
        # only excute SELECT commands
        if not dbUtility.utility.isSelect(command):
            raise ValueError('query can only excute SELECT commands')

        return self.con.execute(command).fetchall()
