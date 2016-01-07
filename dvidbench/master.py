import gevent
import json
import sys
from gevent import GreenletExit
from gevent.pool import Group
import rpc
from rpc import Message
from stats import Stats

runner = None # singleton so that we only have one master runner.

class Master():

    def __init__(self, options):
        self.clients = []
        self.master_host = options.master_host
        self.master_port = options.master_port

        self.load_config_data(options)

        self.server = rpc.Server(self.master_host, self.master_port)
        self.greenlet = Group()
        self.greenlet.spawn(self.listener)

        self.stats = Stats()
        return

    def client_count(self):
        return len(self.clients)

    def listener(self):
        while True:
            msg = self.server.recv()
            if msg.type == "client-started":
                # add the client to the list of registered clients
                print msg
                print "Received contact from client {}".format(msg.node_id)
                self.clients.append(msg.node_id)
                print "currently serving {} clients".format(len(self.clients))
                for client in self.clients:
                    self.server.send(Message('config', self.config, client))

            elif msg.type == "client-ready":
                # set clients status as ready
                print "received: {}".format(msg.data)

            elif msg.type == "client-quit":
                self.clients.remove(msg.node_id)

            elif msg.type == "request-stats":
                self.stats.add(msg.data)

            elif msg.type == "client-stats":
                print "stats: {}".format(msg.data)

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
