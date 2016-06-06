
from kazoo.client import KazooClient
import logging

logging.basicConfig()

class WWatcher:
    def __init__(self):
        self.zk = KazooClient('node01:2181')
        self.zk.start()



    def __del__(self):
        self.zk.stop()




class SSetter:
    def __init__(self):
        self.zk = KazooClient('node01:2181')
        self.zk.start()
        self.zk.ensure_path('/test')
        self.zk.set('/test','data')


    def __del__(self):
        self.zk.stop()

watch = WWatcher()

@watch.zk.DataWatch('/test')
def erection_handler(data,stat,event):
    print 'No please'




print 'test'