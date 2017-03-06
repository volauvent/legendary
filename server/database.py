'''
This module implements API to communicate with database backend.
'''

class databaseAPI:

    def __init__(self):
        '''
        Initialization, either use SQL or NoSQL
        All image data and model data are stored under data folder (possibly under image and model, separately)
        The database backend should manage metadata only (i.e., store PATH to data, instead of storing data itself) to
        achieve efficiency.
        '''
        pass

    def connect(self):
        """
        connect to database
        """

    def create(self):
        """
        create a table
        """

    def insert(self, data):
        """
        insert an entry
        """

    def query(self, command):
        """
        send query to backend, and get data back
        """
        return None

    def query_meta(self, command):
        """
        send query to backend, and get metadata (e.g., PATH to data) back
        """
        return None

    def close(self):
        """
        close connection to database
        """
