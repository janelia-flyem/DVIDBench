from gevent import wsgi
from flask import Flask, make_response, request, render_template
import dvidbench
import os
import master

app = Flask(__name__)
app.debug = True
app.root_path = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    clients = 0
    if master.runner:
        clients = master.runner.client_count()


    return render_template("index.html",
        version=dvidbench.__version__,
        clients=clients
    )

def start(options):
    print "Server started and listening at http://{0}:{1}/".format(options.console_host or "*", options.console_port)
    wsgi.WSGIServer((options.console_host, options.console_port), app, log=None).serve_forever()
