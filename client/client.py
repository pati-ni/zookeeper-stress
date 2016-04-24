import socket
import logging
import timeit
import time
from threading import Lock
from twisted.internet import reactor
from kazoo.client import KazooClient


def read_nodes(file='/home/students/cs091747/zookeeper/server/nodes_list',port=9666):
    nodes=[]
    with open(file) as fp:
        for line in fp:
            for word in line.rstrip('\n').split(' '):
                nodes.append(word+':'+str(port))
    return ','.join(nodes)

class ClientBase:

    def __init__(self, z_node, logger_node='/logger'):

        logging.basicConfig()
        self.hosts = read_nodes()
        self.logger_z_node = logger_node
        self.hostname = socket.gethostname()
        self.z_node = z_node
        self.counter = {'success':0}
        self.zk = KazooClient(self.hosts)
        self.zk.start()
        self.lock = Lock()
        self.zk.ensure_path(self.z_node)
        self.log_queue = []
        self.id = self.hostname
        reactor.run()
        reactor.callWhenRunning()
        #@self.zk.DataWatch('/logger')
        #def erection_handler(data,stat,event):
            #logging.info('Data:',data,'Version:', stat.version,'Event:', event)
            #print 'Contenders:', self.election.contenders()

    def logger(self):

        if not self.finished:
            reactor.callLater(60, self.logger)

        zk_log = KazooClient(self.hosts)
        zk_log.start()

        with self.lock:
            if not self.log_queue:
                zk_log.set(self.logger_z_node, str(self.log_queue))
            del self.log_queue[:]
        zk_log.stop()


    def complete_task(self, method):

        def success(*args,**kwargs):
            self.counter['success']+=1
            method(*args, **kwargs)

        return success

    @reactor.callWhenRunning
    def stopwatch(self, method):

        def timed(*args, **kwargs):

            l = timeit.Timer(lambda : method(*args, **kwargs)).timeit()
            #Append to queue
            with self.lock:
                self.log_queue.append((time.time(), self.id, l,))

        return timed


    def __del__(self):

        self.zk.stop()
        reactor.stop()
        print self.counter['success']

