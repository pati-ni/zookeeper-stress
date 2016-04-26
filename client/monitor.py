__author__ = 'main'

import logging
import kazoo
from kazoo.client import KazooClient
from twisted.internet import reactor
from threading import Lock
from twisted.internet import task
import client
import ast

class Monitor:
    timeout = 5
    requests = 0

    def __init__(self, z_node='/logger'):
        logging.basicConfig()
        self.hosts = client.read_nodes()
        self.z_node = z_node
        self.lock = Lock()
        self.zk = KazooClient(self.hosts)
        self.zk.start()
        self.zk.ensure_path(self.z_node)
        self.log = task.LoopingCall(self.throughput)
        self.log.start(self.timeout)




        @self.zk.DataWatch(self.z_node)
        def erection_handler(data,stat,event):
            if not data:
                return
            try:
                requests = ast.literal_eval(data)
                with self.lock:
                    self.requests += len(requests)
                    
            except (ValueError):
                pass

            #logging.info('Received update','Event:')

    def throughput(self):
        with self.lock:
            print 'Throughput',self.requests/float(self.timeout),'requests/second'
            self.requests = 0


    def __del__(self):
        self.zk.stop()
        self.log.stop()
        print 'Monitor Ended'


m = Monitor()

reactor.run()