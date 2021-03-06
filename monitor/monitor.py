import logging
from kazoo.client import KazooClient
from kazoo.recipe.queue import Queue
from datetime import date
import os

from threading import Lock
from flask import Flask, render_template
import bokeh.plotting as plt
import numpy as np
import pandas as pd
import ast
import time
from datetime import datetime


def bokeh_plot(my_plt):
    """Return filename of plot of the damped_vibration function."""
    # t = linspace(0, T, resolution+1)
    # u = damped_vibrations(t, A, b, w)
    # create a new plot with a title and axis labels
    # TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select,lasso_select"
    from bokeh.embed import components
    script, div = components(my_plt)
    return script, div


def plot_line(x,y,**kwargs):
    TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"

    p = plt.figure(title=kwargs['title'],
                   tools=TOOLS,
                   x_axis_label=kwargs['x_axis'],
                   y_axis_label=kwargs['y_axis'],
                   plot_height=kwargs['height'],
                   plot_width=kwargs['width'])
    p.line(x,y,legend=kwargs['legend'])
    return p


def plot_throughput(df):
    ts = df['timestamp']
    bins_count = int(ts.max() - ts.min())
    timeframes = np.linspace(ts.min(), ts.max(), num=bins_count, endpoint=False)
    bins = pd.cut(ts, timeframes)
    t = np.linspace(0, bins_count, num=bins_count, endpoint=False)
    throughput = df.groupby(bins).size()
    p = plot_line(t, throughput.values,
                  legend="Requests per second",
                  title="Throughput",
                  x_axis="Seconds",
                  y_axis="Requests",
                  width=1600,
                  height=800)
    return p


def plot_latency(df):
    ts = df['timestamp']
    bins_count = int(ts.max() - ts.min())
    timeframes = np.linspace(ts.min(), ts.max(), num=bins_count, endpoint=False)
    bins = pd.cut(ts, timeframes)
    t = np.linspace(0, bins_count, num=bins_count, endpoint=False)
    latency = df['response_time'].groupby(bins).mean() * 1000
    p = plot_line(t, latency.values,
                  legend="160",
                  title="Latency",
                  x_axis="Seconds",
                  y_axis="Requests",
                  width=1600,
                  height=800)
    return p


class Monitor(Flask):

    def __init__(self, z_node='/logger'):
        logging.basicConfig()
        self.dirty = False
        self.file = '/media/localhd/cs091747/'+datetime.now().strftime('exp%m.%d_%h%H:%M')+'.csv'

        self.hosts = 'node09:9066'
        self.z_node = z_node
        self.lock = Lock()
        self.df_lock = Lock()
        self.zk = KazooClient(self.hosts)
        self.zk.start()
        self.requests = []
        self.zk.ensure_path(self.z_node)
        self.queue = Queue(self.zk,self.z_node)
        Flask.__init__(self,__name__)

        @self.zk.ChildrenWatch(self.z_node)
        def logger_handler(children):
            l = len(self.queue)
            print l
            for _ in range(l):
                data = self.queue.get()
                if data:
                    try:
                        t0 = time.time()
                        request_log = ast.literal_eval(data)
                        with self.lock:
                            self._data_handler(request_log)
                        print 'Request of size', len(data), ' handled in', time.time() - t0, request_log['hostname'], request_log['node']
                    except ValueError:
                        print 'ValueError'
            return True

        @self.route('/', methods=['GET', 'POST'])
        def main():
            throughput, latency = self.plots()
            return render_template('view.html', throughput=bokeh_plot(throughput), latency=bokeh_plot(latency))

    def _data_handler(self,response):
        if 'request_data' in response:
            client_responses = response['request_data']
            for resp in client_responses:
                extra = (response['hostname'], response['node'])
                self.requests.append(resp + extra)

    def plots(self):
        with self.lock:
            current_requests = self.requests
            df = pd.DataFrame(current_requests, columns=['timestamp', 'response_time', 'id', 'hostname', 'node'])
            self.requests = []
        if not self.dirty:
            print 'Dumping operations to file', file
            df.to_csv(self.file)
            self.dirty = True
        else:
            df.to_csv(self.file, mode='a', header=False)
        with self.df_lock:
            throughput = plot_throughput(df)
            latency = plot_latency(df)

        return throughput, latency

    def __del__(self):
        self.zk.stop()
        print 'Monitor Ended'

if __name__ == '__main__':
    m = Monitor()
    m.run(host="0.0.0.0", port=20080, debug=False)