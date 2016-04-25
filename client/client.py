import socket
import logging
import timeit
import time
from threading import Lock
from twisted.internet import reactor
from twisted.internet import task
from kazoo.client import KazooClient


def read_nodes(file='/home/students/cs091747/zookeeper/server/nodes_list',port=9666):
    nodes=[]
    with open(file) as fp:
        for line in fp:
            for word in line.rstrip('\n').split(' '):
                nodes.append(word+':'+str(port))
    return ','.join(nodes)


def timer(method):

    def timed(self, *args, **kwargs):
        stamp = time.time()
        l = timeit.Timer(lambda : method(self, *args, **kwargs)).timeit(number=1)
        #Append to queue
        with self.lock:
            self.log_queue.append((stamp, self.id, l))

    return timed


def complete_task(method):

    def success(self, *args, **kwargs):
        self.counter['success']+=1
        method(self, *args, **kwargs)

    return success

class ClientBase:

    finished = False
    counter = {'success':0}

    def __init__(self, z_node, logger_node='/logger'):

        logging.basicConfig()
        self.hosts = read_nodes()
        self.logger_z_node = logger_node
        self.hostname = socket.gethostname()
        self.z_node = z_node
        self.id = self.hostname
        self.zk = KazooClient(self.hosts)
        self.zk.start()
        self.lock = Lock()
        self.zk.ensure_path(self.z_node)
        self.zk.ensure_path(self.logger_z_node)
        self.log_queue = []
        self.log = task.LoopingCall(self.logger)
        self.log.start(5)
        #@self.zk.DataWatch('/logger')
        #def erection_handler(data,stat,event):
            #logging.info('Data:',data,'Version:', stat.version,'Event:', event)
            #print 'Contenders:', self.election.contenders()

    def logger(self):

        zk_log = KazooClient(self.hosts)
        zk_log.start()
        with self.lock:
            if self.log_queue:
                print 'Logger inserted',len(self.log_queue)
                zk_log.set(self.logger_z_node, str(self.log_queue))
            del self.log_queue[:]
        zk_log.stop()


    def _log_dump(self,record):
        with self.lock:
            self.log_queue.append(record)

    def __del__(self):
        self.log.stop()
        self.zk.stop()
        print self.counter['success']

