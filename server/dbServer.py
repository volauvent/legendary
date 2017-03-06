'''
Database server module

This module implements a database server for emotional data management.
1. Provides API for training module to fetch training data and store trained models.
2. Provides API for frontEnd module to demonstrate model performance, as well as storing new labels by mechanic turk.
3. It inherits from baseServer. It uses database module as the backend.
'''


import sys
sys.append('./')
from baseServer import baseServer
from database import databaseAPI


class dbServer(baseServer, portNum):
    def __init__(self):
        super(dbServer, self).__init__(portNum)
        self._database = databaseAPI()

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
        task = dat['task']
        command = dat['command']
        if task == "sql":
            result = self._postgres.query(task)

        return result

    def process_offline(self):
        """
        API for offline jobs.
        Example: Performance analysis, database organization.
        :return:
        """


if __name__ == "__main__":
    server = dbServer()
    server.start()