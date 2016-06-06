__author__ = 'main'

import pandas as pd
import numpy as np
import random
import subprocess
import zookeeper.client
import sys
from flask import Flask
from threading import Lock
from twisted.internet import reactor

def nodes_throughput(df):

    if df.empty:
        return 0
    groups = df.groupby('id')['timestamp'].aggregate(lambda x : x.count()/float(x.max()-x.min()))
    return groups.mean()

class FeedbackMonitor:
    clients_spawned = 0
    def __init__(self, node, client_nodes='node_list'):
        self.client = {'read':"leaderElection.py", 'write':"leaderElectionWrite.py"}
        self.df = pd.DataFrame(columns=['timestamp','response_time','id','hostname','node'])
        self.nodes = client.insert_client_nodes(client_nodes)
        self.monitoring_node = node
        self.seed = random.choice(range(len(self.nodes)))
        self.client_lock = Lock()
        #self.start(probability_read_bias=0)
        #self.start(probability_read_bias=1)
        for _ in range(1):
            self.start(probability_read_bias=1)


    def _improve_throughput(self,data):

        if not 'request_data' in data:
            return

        new_df = pd.DataFrame(data['request_data'],columns=['timestamp','response_time','id'])
        new_df['hostname'] = pd.Series([data['hostname']] * len(new_df))
        new_df['node'] = pd.Series([data['node']] * len(new_df))
        with self.lock:

            new_performance =nodes_throughput(new_df)/new_df['response_time'].mean()
            self.df = self.df.append(new_df,ignore_index=True)
            performance = nodes_throughput(self.df)/self.df['response_time'].mean()

        print new_performance,performance
        return new_performance/performance > 1.1



    def _data_handler(self,response):
        if response['node'] == self.monitoring_node:
            if self._improve_throughput(response):
                print 'Mean Latency',self.df['response_time'].mean()
                self.start()

    def start(self, probability_read_bias=0.9):

        project_dir = "/home/students/cs091747/zookeeper"
        script_dir = "client/scripts"
        print self.nodes
        if random.random()< probability_read_bias:
            client_file = self.client['read']
        else:
            client_file = self.client['write']

        with self.client_lock:
            self.clients_spawned += 1
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


if __name__ == '__main__':

    m = []

    total_clients =  int(sys.argv[1])
    for i in range(total_clients):
        m.append(FeedbackMonitor('/erection' + str(i)))

    app = Flask(__name__)

    app.run(host="0.0.0.0", port=20666, debug=True, use_reloader=False)



