__author__ = 'main'

from monitor import Monitor
import pandas as pd
import random
import subprocess
import client
import sys
from twisted.internet import reactor
#Monitoring class with load assertion
#Optimizing system throughput

def get_throughput(df):

    if df.empty:
        return 0

    t0 = df['timestamp'].min()
    t1 = df['timestamp'].max()

    return len(df)/(t1-t0)

class FeedbackMonitor(Monitor):
    clients_spawned = 0
    def __init__(self, node, client_nodes='node_list'):
        self.client = {'read':"leaderElection.py", 'write':"leaderElectionWrite.py"}
        self.df = pd.DataFrame(columns=['timestamp','response_time','id'])
        self.nodes = client.insert_client_nodes(client_nodes)
        self.monitoring_node = node

        Monitor.__init__(self, timeout=2)
        self.start(probability_read_bias=0)
        self.start(probability_read_bias=1)



    def _improve_throughput(self,data):
        if not 'request_data' in data:
            return

        new_df = pd.DataFrame(data['request_data'],columns=['timestamp','response_time','id'])

        new_throughput = get_throughput(new_df)
        with self.lock:
            self.df = pd.concat([self.df,new_df])
            throughput = get_throughput(self.df)
        return new_throughput > throughput



    def _data_handler(self,response):
        if response['node'] == self.monitoring_node:
            if self._improve_throughput(response):
                print 'Mean Latency',self.df['response_time'].mean()
                print get_throughput(self.df)
                self.start()

    def start(self, probability_read_bias=0.8):

        node = random.choice(self.nodes)
        project_dir = "/home/students/cs091747/zookeeper"
        script_dir = "client/scripts"

        if random.random()< probability_read_bias:
            client_file = self.client['read']
        else:
            client_file = self.client['write']

        script_path = "/".join([project_dir,script_dir,"start-client.sh"])
        screen_name = self.monitoring_node[1:] + client_file.split('.')[0] + str(self.clients_spawned)
        command = ["ssh", node,"screen","-dmS",screen_name,script_path,client_file,self.monitoring_node,node+screen_name]
        new_client = subprocess.call(command)

        if new_client != 0:
            print 'client could not be spawned',command
        else:
            #debug message, to be commented
            print ' '.join(command),'client successfully launched',self.clients_spawned
            self.clients_spawned += 1

if __name__ == '__main__':
    for i in range(int(sys.argv[1])):
        m = FeedbackMonitor('/erection'+str(i))
    reactor.run()



