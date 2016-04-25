__author__ = 'main'

import logging
import kazoo
from kazoo.client import KazooClient
from twisted.internet import reactor
import client


class Monitor:

    def __init__(self, z_node='/logger'):
        print 'Monitor started'
        logging.basicConfig()
        self.hosts = client.read_nodes()
        self.z_node = z_node
        self.zk = KazooClient(self.hosts)
        self.zk.start()
        self.zk.ensure_path(self.z_node)
        @self.zk.DataWatch(self.z_node)
        def erection_handler(data,stat,event):
            print data
            #logging.info('Received update','Event:')



    def __del__(self):
        self.zk.stop()
        print 'Monitor Ended'


m = Monitor()

reactor.run()