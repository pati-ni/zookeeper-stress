import logging
from kazoo.client import KazooClient
from twisted.internet import reactor
from threading import Lock
from twisted.internet import task
import client
import ast
from abc import abstractmethod
class Monitor:
    requests = 0
    def __init__(self, z_node='/logger',timeout=5):
        logging.basicConfig()
        self.hosts = client.read_nodes()
        self.z_node = z_node
        self.timeout = timeout
        self.lock = Lock()
        self.zk = KazooClient(self.hosts)
        self.zk.start()
        self.zk.ensure_path(self.z_node)


        @self.zk.DataWatch(self.z_node)
        def erection_handler(data,stat,event):
            if not data:
                return
            try:
                request_log = ast.literal_eval(data)
                self._data_handler(request_log)
            except ValueError:
                pass

    def start(self):
        self.log = task.LoopingCall(self.throughput)
        self.log.start(self.timeout)

    def _data_handler(self,response):
        with self.lock:
            self.requests += len(response['request_data'])


    def throughput(self):
        with self.lock:
            print 'Throughput',self.requests/float(self.timeout),'requests/second'
            self.requests = 0

    def __del__(self):
        self.zk.stop()
        self.log.stop()
        print 'Monitor Ended'

if __name__ == '__main__':
    m = Monitor()
    m.start()

    reactor.run()