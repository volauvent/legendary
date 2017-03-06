'''
baseClient module

This module provides basic implementation of a client which supports sending query to the server.
'''

from socket import *
import pickle
from concurrent.futures import ThreadPoolExecutor


class baseClient:
    '''
    A basic client that can communicate with Server.
    '''
    def __init__(self, port_num):
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._socket.connect(('localhost', port_num))

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

if __name__ == "__main__":
    num = 20
    tp_pool = ThreadPoolExecutor(num)
    result = []
    for i in range(num):
        client = baseClient(int(sys.argv[1]))
        result.append(tp_pool.submit(client.sender, i))
    for i in range(num):
        print(result[i].result())