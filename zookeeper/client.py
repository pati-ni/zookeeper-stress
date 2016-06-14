import socket
import logging
import timeit
import time
import random
from threading import Lock, Timer
from kazoo.client import KazooClient
from kazoo.recipe.queue import Queue

logger_timeout = 10

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
        l = timeit.Timer(lambda : method(self, *args, **kwargs)).timeit(number=1)
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
    counter = {'success':0}
    log_hosts = 'node09:9066'
    lock = Lock()

    def __init__(self, id, logger_node='/logger', logger_interval=None):
        logging.basicConfig()
        self.logger_z_node = logger_node
        self.hostname = socket.gethostname()
        self.id = id

        self.z_node = '/default'

        if logger_interval is None:
            self.logger_timeout = logger_timeout
        else:
            self.logger_timeout = logger_interval

        self.zk_log = KazooClient(self.log_hosts)
        self.zk_log.start()
        self.zk_log.ensure_path(self.logger_z_node)
        self.queue = Queue(self.zk_log, self.logger_z_node)
        self.log_queue = []
        self.logger()


    def logger(self):
        with self.lock:
            if self.log_queue:
                log_packet = {'hostname':self.hostname,'node':self.z_node,'type':'client_log','request_data':self.log_queue}
                message = str(log_packet)
                del self.log_queue[:]
        if 'message' in locals():
            self.queue.put(message)

        Timer(self.logger_timeout, self.logger).start()


    def _log_dump(self, record):
        with self.lock:
            self.log_queue.append(record)

    def __del__(self):
        self.zk_log.stop()

        print 'Lock Acquired', self.counter['success'], 'times'



class ZkBase(ClientBase):
    dynamic_reconfiguration = True

    def __init__(self, z_node, id):
        self.hosts = read_nodes()
        self.z_node = z_node
        self.connect()
        self.zk.ensure_path(self.z_node)

        if self.dynamic_reconfiguration:
            @self.zk.DataWatch('/zookeeper/config')
            def config_watch(data, stat):
                servers = []
                for server in data.split("\n")[:-1]:
                    server_str = server.split("=")[1]
                    tokens = server_str.split(":")
                    node = tokens[0]
                    port = tokens[-1]
                    servers.append(node+":"+port)
                hosts = ','.join(servers)
                print 'New host string',hosts
                self.zk.set_hosts(hosts)
                return True
        ClientBase.__init__(self, id)

    def connect(self):
        self.zk = KazooClient(self.hosts)
        self.zk.start()

    def disconnect(self):
        self.zk.stop()

    def __del__(self):
        self.disconnect()

