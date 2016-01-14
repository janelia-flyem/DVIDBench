from gevent import wsgi
from flask import Flask, make_response, request, render_template, abort, redirect, url_for
from itertools import chain
import dvidbench
import os
import master
import json

app = Flask(__name__)
app.debug = True
app.root_path = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    clients = 0
    workers = 0
    if master.runner:
        clients = master.runner.client_count()
        workers = master.runner.worker_count()

    try:
        stats=master.runner.stats.aggregated_stats(name="total", full_request_history=True)
    except Exception:
        stats = {}


    return render_template("index.html",
        version=dvidbench.__version__,
        clients=clients,
        workers=workers,
        stats=stats,
        timings=master.runner.stats.timings,
    )

@app.route('/start', methods=['POST'])
def start_workers():
    count = int(request.form['count'])
    if count > 0 and master.runner.client_count() > 0:
        master.runner.start_workers(count)

    return redirect(url_for('index'))

@app.route('/stop')
def stop_workers():
    master.runner.stop_workers()
    return(redirect(url_for('index')))

@app.route('/stats/timings')
def get_timings():
    data = {}
    timings = master.runner.stats.timings
    for t in timings.iterkeys():
        data[t] = timings[t].current_max
    return json.dumps(data)

@app.route('/stats/update')
def get_stats():
    data = {
      'clients': master.runner.client_count(),
      'workers': master.runner.worker_count(),
    }

    stats = []
    for s in chain(_sort_stats(master.runner.stats.entries), [master.runner.stats.aggregated_stats(name="total", full_request_history=True)]):
        stats.append({
            "method": 'GET',
            "name": s.name,
            "num_requests": s.num_requests,
            "num_failures": s.num_failures,
            "avg_response_time": s.avg_response_time,
            "min_response_time": s.min_response_time or 0,
            "max_response_time": s.max_response_time,
            "current_rps": s.current_rps,
            "median_response_time": s.median_response_time,
            "avg_content_length": s.avg_content_length,
        })
    data['stats'] = stats
    return json.dumps(data)


@app.route("/stats/reset")
def reset_stats():
    master.runner.stats.reset_all()
    return "ok"


def _sort_stats(stats):
    return [stats[key] for key in sorted(stats.iterkeys())]


def start(options):
    print "Server started and listening at http://{0}:{1}/".format(options.console_host or "*", options.console_port)
    wsgi.WSGIServer((options.console_host, options.console_port), app, log=None).serve_forever()
