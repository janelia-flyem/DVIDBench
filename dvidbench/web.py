from gevent import wsgi
from flask import Flask, make_response, request, render_template
import dvidbench
import os

app = Flask(__name__)
app.debug = True
app.root_path = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    return render_template("index.html",
        version=dvidbench.__version__
    )

def start(options):
    print "Server started and listening at http://{0}:{1}/".format(options.console_host or "*", options.console_port)
    wsgi.WSGIServer((options.console_host, options.console_port), app, log=None).serve_forever()
