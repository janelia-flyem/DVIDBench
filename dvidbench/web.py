from gevent import wsgi
from flask import Flask, make_response, request, render_template, abort, redirect, url_for
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
        clients=clients,
        stats=master.runner.stats
    )

@app.route('/start', methods=['POST'])
def start_workers():
    count = int(request.form['count'])
    if count > 0 and master.runner.client_count() > 0:
        master.runner.start_workers(count)

    return redirect(url_for('index'))

def start(options):
    print "Server started and listening at http://{0}:{1}/".format(options.console_host or "*", options.console_port)
    wsgi.WSGIServer((options.console_host, options.console_port), app, log=None).serve_forever()
