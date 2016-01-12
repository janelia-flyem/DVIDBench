import gevent
import json
import sys
import events
from gevent import GreenletExit
from gevent.pool import Group
import rpc
from rpc import Message
from stats import global_stats

runner = None # singleton so that we only have one master runner.

class Master():

    def __init__(self, options):
        self.clients = {}
        self.master_host = options.master_host
        self.master_port = options.master_port

        self.load_config_data(options)

        self.server = rpc.Server(self.master_host, self.master_port)
        self.greenlet = Group()
        self.greenlet.spawn(self.listener)

        self.stats = global_stats

        def on_slave_report(client_id, data):
            self.clients[client_id]['workers'] = data['workers']
            return
        events.slave_report += on_slave_report

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
                for client in self.clients.iterkeys():
                    self.server.send(Message('config', self.config, client))

            elif msg.type == "client-ready":
                # set clients status as ready
                print "received: {}".format(msg.data)

            elif msg.type == "client-quit":
                if msg.node_id in self.clients:
                  del self.clients[msg.node_id]

            elif msg.type == "client-stats":
                events.slave_report.fire(client_id=msg.node_id, data=msg.data)

    def quit(self):
        for client in self.clients:
            self.server.send(Message("quit",None,None))

    def load_config_data(self, args):
        if args.debug:
            sys.stderr.write("looking for settings in %s\n" % args.config_file)

        self.config_file = args.config_file

        try:
            config_json = open(args.config_file)
            config = json.load(config_json)
        except IOError:
            print "unable to find the config file: %s\n" % args.config_file
        except ValueError:
            print "There was a problem reading the config. Is it valid JSON?\n"

        # merge the command line args with the ones loaded from the config file.
        # command line always wins.

        self.config = config
        return

    def start_workers(self, count):
        # divide the count among the workers
        per_client = count / self.client_count()
        # contact each one in kind and tell them to start x workers
        for client in self.clients:
            self.server.send(Message('start', per_client, client))

        print "started {} workers".format(count)

