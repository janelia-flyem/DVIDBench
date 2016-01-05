import gevent
import json
import sys
from gevent import GreenletExit
from gevent.pool import Group
import rpc
from rpc import Message

class Master():

    def __init__(self, options):
        self.clients = []
        self.master_host = options.master_host
        self.master_port = options.master_port

        self.load_config_data(options)

        self.server = rpc.Server(self.master_host, self.master_port)
        self.greenlet = Group()
        self.greenlet.spawn(self.listener)
        return

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
