__author__ = 'main'
from flask import Flask, make_response, render_template

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

import StringIO

app = Flask(__name__)


import numpy as np
import cStringIO
import matplotlib.pyplot as plt


app = Flask(__name__)

@app.route('/plot')
def build_plot():

  # Generate the plot
  x = np.linspace(0, 10)
  line, = plt.plot(x, np.sin(x))

  f = cStringIO.StringIO()
  plt.savefig(f, format='png')

  # Serve up the data
  header = {'Content-type': 'image/png'}
  f.seek(0)
  data = f.read()

  return data, 200, header

@app.route('/')
def home(methods=['GET']):

   return render_template('index.html', title='Monitor')



if __name__ == "__main__":
   app.run(host="0.0.0.0", port=20080,debug=True)
