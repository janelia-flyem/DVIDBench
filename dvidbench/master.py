import gevent
import json
import events
import logging
import time
import os
from gevent import GreenletExit
from gevent.pool import Group
import rpc
from rpc import Message
from stats import global_stats
from config import Configurable

runner = None # singleton so that we only have one master runner.

class Master(Configurable):

    def __init__(self, options):
        self.clients = {}
        self.master_host = options.master_host
        self.master_port = options.master_port

        self.config = self.load_config_data(options)

        self.server = rpc.Server('*', self.master_port)
        self.greenlet = Group()
        self.greenlet.spawn(self.listener)

        self.stats = global_stats

        def on_manager_report(client_id, data):
            self.clients[client_id]['workers'] = data['workers']

            return
        events.manager_report += on_manager_report

        if self.config.log_stats_dir:
            log_dir = os.path.expanduser(self.config.log_stats_dir)
            try:
                os.makedirs(log_dir)
            except OSError:
                if not os.path.isdir(log_dir):
                    print "Couldn't create dir {0}: 1{}".format(log_dir, e)
                    exit(1)

            # create logger
            timestr = time.strftime("%Y%m%d-%H%M%S")
            log_file = os.path.join(log_dir, '{0}-data.log'.format(timestr))

            log_format ='%(message)s'
            logging.basicConfig(format=log_format, filename=log_file, level=logging.DEBUG )

            def log_on_manager_report(client_id, data):
                for stat in data['stats']:
                    logging.info( "%(start_time)s\t%(name)s\t%(max_response_time)s\t%(min_response_time)s\t%(total_content_length)s", stat)
                return
            events.manager_report += log_on_manager_report


        return

    def client_count(self):
        return len(self.clients)

    def worker_count(self):
        count = 0
        for client in self.clients.itervalues():
            count += client['workers']
        return count

    def listener(self):
        while True:
            msg = self.server.recv()
            if msg.type == "client-started":
                # add the client to the list of registered clients
                print msg
                print "Received contact from client {}".format(msg.node_id)
                self.clients[msg.node_id] = {'workers': 0}
                print "currently serving {} clients".format(len(self.clients))

            elif msg.type == "client-ready":
                # set clients status as ready
                print "received: {}".format(msg.data)

            elif msg.type == "client-quit":
                if msg.node_id in self.clients:
                  print self.stats.aggregated_stats(name="total", full_request_history=True).num_requests
                  del self.clients[msg.node_id]


            elif msg.type == "client-stats":
                events.manager_report.fire(client_id=msg.node_id, data=msg.data)

    def quit(self):
        for client in self.clients:
            self.server.send(Message("quit",None,None))

    def start_workers(self, count):
        # divide the count among the workers
        per_client = count / self.client_count()

        # is this the first worker
        seen_first = False

        # contact each one in kind and tell them to start x workers
        for client in self.clients.iterkeys():
            workers = per_client

            # is there going to be a remainder, shove it on the first worker?
            if not seen_first and (count % self.client_count() == 1):
                workers += 1

            self.server.send(Message('start', workers, client))
            seen_first = True
            print "started {} workers on client {}".format(workers, client)

        return

    def stop_workers(self):
        for client in self.clients.iterkeys():
            self.server.send(Message('stop', {}, client))
        return




