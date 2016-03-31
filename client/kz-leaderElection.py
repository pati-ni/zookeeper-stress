from kazoo.client import KazooClient
from kazoo.recipe.election import Election
from kazoo.client import KazooState
from kazoo.client import KeeperState
import socket
import sys
import logging
import time
import random
import timeit
import threading
import stopwatch
#logging.basicConfig(level=logging.INFO)




def readNodes(file='/home/students/cs091747/zookeeper/server/nodes_list',port=9666):
    nodes=[]
    with open(file) as fp:
        for line in fp:
            for word in line.rstrip('\n').split(' '):
                nodes.append(word+':'+str(port))
    return ','.join(nodes)


class ClientElection:

    def __init__(self, znode):
        self.hosts=readNodes()
        self.hostname = socket.gethostname()
        self.znode = znode
        self.counter = 0

        self.zk= KazooClient(self.hosts)
        self.zk.start()
        self.zk.ensure_path(self.znode)

        @self.zk.DataWatch(self.znode)
        def erection_handler(data,stat,event):
            logging.info('Data:',data,'Version:', stat.version,'Event:', event)
            #print 'Contenders:', self.election.contenders()


    def leaderElection(self):
        self.election = Election(self.zk,self.znode,identifier=self.hostname)
        self.election.run(self.leaderEnd,self.hostname)

    def leaderEnd(self,hostname):
        
        #print 'Success',hostname,'Synthetic workload running...'
        self.counter+=1
        #self.zk.set(self.znode,str(self.counter))
        #time.sleep(random.gammavariate(0.7,0.2))
        #print 'Exiting...'

    def __del__(self):
        self.zk.stop()
        print self.counter


def loggerThread():
    
    return

if __name__ == '__main__':
    logging.basicConfig()
    client = ClientElection('/erection')
    
    while True:
	print 'Here'
        t = stopwatch.Timer()
        l = timeit.Timer(lambda: client.leaderElection()).repeat(number=4)
        t.stop()
        total = 0
        for timer in l:
            total+=timer
        print(t.elapsed-total)
