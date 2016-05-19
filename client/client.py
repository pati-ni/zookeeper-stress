import socket
import logging
import timeit
import time
from threading import Lock
from twisted.internet import task
from kazoo.client import KazooClient
import copy



def read_nodes(file='/home/students/cs091747/zookeeper/server/nodes_list',port=9666):
    nodes=[]
    with open(file) as fp:
        for line in fp:
            for word in line.rstrip('\n').split(' '):
                nodes.append(word+':'+str(port))
    return ','.join(nodes)

def insert_client_nodes(client_file):
    nodes=[]

    with open(client_file) as fp:
        for line in fp:
            for word in line.rstrip('\n').split(' '):
                nodes.append(word)
    return nodes




def timer(method):

    def timed(self, *args, **kwargs):
        stamp = time.time()
        if self.reconnect:
            self.zk = KazooClient(self.hosts)
            self.zk.start()
        l = timeit.Timer(lambda : method(self, *args, **kwargs)).timeit(number=1)
        if self.reconnect:
            self.zk.stop()
        #Append to queue
        with self.lock:
            record = (stamp,l,self.id)
            self.log_queue.append(record)

    return timed


def complete_task(method):

    def success(self, *args, **kwargs):
        self.counter['success']+=1
        method(self, *args, **kwargs)

    return success

class ClientBase:

    finished = False
    counter = {'success':0}

    def __init__(self, z_node, id, logger_node='/logger',reconnect=False):

        logging.basicConfig()
        self.hosts = read_nodes()
        self.logger_z_node = logger_node
        self.hostname = socket.gethostname()
        self.reconnect = reconnect
        self.z_node = z_node
        self.id = id

        self.zk = KazooClient(self.hosts)
        self.zk.start()
        self.lock = Lock()
        self.zk.ensure_path(self.z_node)
        self.zk.ensure_path(self.logger_z_node)
        if self.reconnect:
            self.zk.stop()

        self.log_queue = []
        self.log = task.LoopingCall(self.logger)
        self.log.start(5)


    def logger(self):

        zk_log = KazooClient(self.hosts)
        zk_log.start()
        with self.lock:
            if self.log_queue:
                log_packet = {'hostname':self.hostname,'node':self.z_node,'type':'client_log','request_data':self.log_queue}
                message = str(log_packet)
                zk_log.set(self.logger_z_node, message)
                log_packet.clear()
                del self.log_queue[:]
                del message

        zk_log.stop()
        del zk_log


    def _log_dump(self,record):
        with self.lock:
            self.log_queue.append(record)

    def __del__(self):
        self.log.stop()
        if not self.reconnect:
            self.zk.stop()
        print self.counter['success']

