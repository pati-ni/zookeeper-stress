__author__ = 'main'

from monitor import Monitor
import pandas as pd
import numpy as np
import random
import subprocess
import client
import sys
from twisted.internet import reactor
from flask import Flask, make_response, render_template
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
        self.df = pd.DataFrame(columns=['timestamp','response_time','id','hostname','node'])
        self.nodes = client.insert_client_nodes(client_nodes)
        self.monitoring_node = node
        self.seed = random.choice(range(len(self.nodes)))
        Monitor.__init__(self, timeout=2)
        self.start(probability_read_bias=0)
        self.start(probability_read_bias=1)



    def _improve_throughput(self,data):

        if not 'request_data' in data:
            return

        new_df = pd.DataFrame(data['request_data'],columns=['timestamp','response_time','id'])
        new_df['hostname'] = pd.Series([data['hostname']] * len(new_df))
        new_df['node'] = pd.Series([data['node']] * len(new_df))
        with self.lock:
            node_df = self.df.loc[self.df.node == data['node']]
            performance = len(node_df['hostname'].unique()) / node_df['response_time'].mean()
            self.df = self.df.append(new_df,ignore_index=True)
            node_df = self.df.loc[self.df.node == data['node']]
            new_performance = len(node_df['hostname'].unique()) / node_df['response_time'].mean()

        return new_performance/performance > 1.3



    def _data_handler(self,response):
        if self._improve_throughput(response):
            print 'Mean Latency',self.df['response_time'].mean()
            self.start()

    def start(self, probability_read_bias=0.8):

        project_dir = "/home/students/cs091747/zookeeper"
        script_dir = "client/scripts"
        print self.nodes
        if random.random()< probability_read_bias:
            client_file = self.client['read']
        else:
            client_file = self.client['write']

        with self.lock:
            node = self.nodes[(self.seed + self.clients_spawned) % len(self.nodes)]
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
    #app = Flask(__name__)

    for i in range(int(sys.argv[1])):
        m = FeedbackMonitor('/erection'+str(i))
    reactor.run()
    #app.run(host="0.0.0.0", port=20666, debug=True)



