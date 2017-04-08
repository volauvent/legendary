import logging
import os.path
import sqlite3 as lite
import sys

import dbUtility


class sqliteWrapper:
    '''
    this is a wrapper of sqlite
    '''

    def __init__(self, dbPath):
        try:
            exist = self.checkDB(dbPath)
            self.con = lite.connect(dbPath)
            if not exist:
                logging.info(dbPath + " doesn't exist, will create a new one \n")
                self.initDB()
        except:

            e = sys.exc_info()[0]
            logging.error(e)
            sys.exit(0)

    def checkDB(self, dbPath):
        return os.path.isfile(dbPath)

    def initDB(self):

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