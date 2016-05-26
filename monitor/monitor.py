import logging
from kazoo.client import KazooClient
from threading import Lock
from flask import Flask, render_template, request
import bokeh.plotting as plt
import numpy as np
import client
import ast
import model



def bokeh_plot(my_plt):
    """Return filename of plot of the damped_vibration function."""
    # t = linspace(0, T, resolution+1)
    # u = damped_vibrations(t, A, b, w)
    # create a new plot with a title and axis labels
    # TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select,lasso_select"

    from bokeh.embed import components
    script, div = components(my_plt)
    return script, div


class Monitor(Flask):

    def __init__(self, z_node='/logger',timeout=5):
        logging.basicConfig()
        self.hosts = client.read_nodes()
        self.z_node = z_node
        self.timeout = timeout
        self.lock = Lock()
        self.zk = KazooClient(self.hosts)
        self.zk.start()
        self.requests = model.model()
        self.zk.ensure_path(self.z_node)
        Flask.__init__(self,__name__)


        @self.zk.DataWatch(self.z_node)
        def erection_handler(data,stat,event):

            if not data:
                return
            try:
                request_log = ast.literal_eval(data)
                self._data_handler(request_log)
            except ValueError:
                pass

        @self.route('/monitor')
        def monitor():
            pass

        @self.route('/', methods=['GET','POST'])
        def main():
            result = bokeh_plot(self.plot_throughput())
            return render_template('view.html', result=result)

    def _data_handler(self,response):

        if not 'request_data' in response:
            return
        with self.lock:
            self.requests = self.requests.append(model.insert_data(response))

    def plot_throughput(self):
        TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"
        p = plt.figure(title="Mean throughput", tools=TOOLS, x_axis_label='t', y_axis_label='y')
        with self.lock:
            values = self.requests['timestamp'].values
        values = np.sort(values,kind='mergesort')
        mean_sec = np.convolve(values, np.ones(1) ,mode='valid')
        # add a line renderer with legend and line thickness
        p.line(values, mean_sec, legend="Requests per second", line_width=2)

        return p



    def __del__(self):
        self.zk.stop()
        print 'Monitor Ended'

if __name__ == '__main__':
    m = Monitor()
    m.run(host="0.0.0.0", port=20080, debug=True)