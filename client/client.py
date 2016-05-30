import socket
import logging
import timeit
import time
import random
from threading import Lock
from twisted.internet import task
from kazoo.client import KazooClient
from kazoo.recipe.queue import Queue



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
        if hasattr(self, 'wait'):
            time.sleep(random.range(0,self.wait,0.1))

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
    log_hosts = 'node09:9066'
    def __init__(self, z_node, id, logger_node='/logger', reconnect=False, dynamicReconfig=False, timeout=20):
        logging.basicConfig()
        self.hosts = read_nodes()
        self.logger_z_node = logger_node
        self.hostname = socket.gethostname()
        self.reconnect = reconnect
        self.z_node = z_node
        self.logger_timeout = timeout
        self.id = id
        self.zk = KazooClient(self.hosts)
        self.zk.start()
        self.lock = Lock()
        self.zk.ensure_path(self.z_node)
        self.zk.ensure_path(self.logger_z_node)
        self.zk_log = KazooClient(self.log_hosts)
        self.zk_log.start()
        self.queue = Queue(self.zk_log, self.logger_z_node)
        if self.reconnect:
            self.zk.stop()

        if dynamicReconfig:
            self.reconfig_lock = Lock()
            @self.zk.DataWatch('/zookeeper/config')
            def config_watch(data, stat, event):
                print 'Data', data
                print 'Stat', stat
                print 'Event', event

        self.log_queue = []
        self.log = task.LoopingCall(self.logger)
        self.log.start(self.logger_timeout)


    def logger(self):
        with self.lock:
            if self.log_queue:
                log_packet = {'hostname':self.hostname,'node':self.z_node,'type':'client_log','request_data':self.log_queue}
                message = str(log_packet)
                self.queue.put(message)
                del self.log_queue[:]


    def configWatch(self):
        pass

    def _log_dump(self,record):
        with self.lock:
            self.log_queue.append(record)

    def __del__(self):
        self.zk_log.stop()
        if not self.reconnect:
            self.zk.stop()
        print self.counter['success']

