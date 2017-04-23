'''
baseClient module

This module provides basic implementation of a client which supports sending query to the server.
'''

from socket import *
import pickle
from concurrent.futures import ProcessPoolExecutor
from configparser import ConfigParser
import logging
import sys
sys.path.append('../')
logging.basicConfig(level=logging.INFO)


class baseClient:
    '''
    A basic client that can communicate with Server.
    '''
    def __init__(self, port_num,host='localhost'):
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._socket.connect(('localhost', port_num))
        logging.info("client: starting at %s" % str(port_num))

    def shutdown(self):
        self._socket.close()

    def sender(self, obj):
        '''
        Send object to server, and get message back from server
        '''
        msg = pickle.dumps(obj)
        msghead = str(len(msg))
        if len(msghead) < 10:
            msghead = "0"* (10-len(msghead)) + msghead
            self._socket.send(pickle.dumps(msghead))
        while len(msg):
            nsent = self._socket.send(msg)
            msg = msg[nsent:]

        return_msghead = self._socket.recv(20)
        if not return_msghead:
            return None
        return_msglen = int(pickle.loads(return_msghead))
        return_msg = self._socket.recv(return_msglen)
        if not return_msg:
            return None
        return_dat = pickle.loads(return_msg)
        return return_dat

    def query(self, q):
        return self.sender(q)

class dbClient(baseClient):
    def __init__(self,port_num = None):
        self.parser = ConfigParser()
        self.parser.read('config.ini')
        if port_num==None:
            port_num=int(self.parser.get('dbServer', 'port'))
        host = self.parser.get('dbServer', 'host')
        super(dbClient, self).__init__(port_num,host)


    def query(self,q):
        logging.info("client: sending query")
        return self.sender({"task":"query_meta","command":q})

    def insertImage(self,path,source='other',label=0,confidence=5,comment="NULL"):
        logging.info("client: sending insert")
        return self.sender({"task":"insertImage","command":("frontend/upload/"+path,source,label,confidence,comment)})

    def insertModelLabel(self,image_id,label=0,confidence=1,model='manual'):
        logging.info("client: sending label")
        return self.sender({"task":"insertModelLabel","command":(model,image_id,label,confidence)})

    def getRandomImageWithWeakLabel(self):
        logging.info("client: requesting weak label")
        return self.sender({"task":"getRandomImageWithWeakLabel","command":""})

    def predict(self,filePath):
        logging.info("client: sending prediction request")
        out=self.sender({"task":"predict","command":"frontend/upload/"+filePath})
        out.sort(key= lambda i:i[0])
        return out
    
    def predict_and_insert(self,filePath,source='other',label=0,confidence=5,comment='NULL'):
        logging.info("client: sending predict_and_insert request")
        return self.sender({"task":"predict_and_insert","command":("frontend/upload/"+filePath,source,label,confidence,comment)})


if __name__ == "__main__":
    num = 1000
    def testfun(port_num, msg):
        client = baseClient(port_num)
        result = client.sender(msg)
        client.shutdown()
        return result

    with ProcessPoolExecutor(10) as tp_pool:
        result = []
        for i in range(num):
            # client = baseClient(int(sys.argv[1]))
            result.append(tp_pool.submit(testfun, int(sys.argv[1]), i))
        for i in range(num):
            print(result[i].result())
