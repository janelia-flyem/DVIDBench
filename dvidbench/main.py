import argparse
import dvidbench
import os
import web
import gevent
import rpc
import json
from rpc import Message

def parse_command_arguments():
    parser = argparse.ArgumentParser(description='Benchmark a DVID server')
    parser.add_argument('-v', '--version', action="version", version=dvidbench.__version__ )
    parser.add_argument('-d', '--debug',  help='print extra debugging information', action='store_true')

    parser.add_argument('config_file', help='location of the configuration file', nargs='?', default=os.path.expanduser('~/.dvidbenchrc'))

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--slave',  help='set this process to run as a slave worker', action='store_true')
    group.add_argument('--master',  help='set this process to run as the aggregating master', action='store_true')

    parser.add_argument('--master-host',  help='specify the address of the master this slave should report to', action='store', dest='master_host', default='127.0.0.1')
    parser.add_argument('--master-port',  help='specify the port of the master this slave should report to', action='store', dest='master_port', default=5050)
    parser.add_argument('--console-host',  help='specify the ip address the master console should be attached to', action='store', dest='console_host', default='')
    parser.add_argument('--console-port',  help='specify the port the master console should be attached to', action='store', dest='console_port', default=8889)

    return parser.parse_args()

def main():
    # parse command line arguments
    args = parse_command_arguments()
    if args.slave:
        greenlet = slave(args)
    else:
        greenlet = master(args)

    try:
        greenlet.join()
    except KeyboardInterrupt as e:
        # shutdown if requested
        exit(0)


    return

def master_listener(server, args, clients):
    while True:
        msg = server.recv()
        if msg.type == "client-started":
            # add the client to the list of registered clients
            print "received: {}".format(msg.data)
            clients.append(msg.node_id)
            print "currently serving {} clients".format(len(clients))
            for client in clients:
                server.send(Message('config', args.config, client))

        elif msg.type == "client-ready":
            # set clients status as ready
            print "received: {}".format(msg.data)

def load_config_data(args):
    if args.debug:
        sys.stderr.write("looking for settings in %s\n" % args.config_file)

    try:
        config_json = open(args.config_file)
        config = json.load(config_json)
    except IOError:
        print "unable to find the config file: %s\n" % args.config_file
    except ValueError:
        print "There was a problem reading the config. Is it valid JSON?\n"

    # merge the command line args with the ones loaded from the config file.
    # command line always wins.

    args.config = config
    return args


def master(args):
    clients = []

    # load configuration file
    args = load_config_data(args)

    # start up web gui thread
    main_greenlet = gevent.spawn(web.start, args)

    # start up rpc server
    server = rpc.Server(args.master_host, args.master_port)

    # wait for commands from web interface
    gevent.spawn(master_listener, server, args, clients)


    # send commands forward to clients

    # need to use events for the following
        # send configuration to clients
            # on client start
            # on config update
        # log stats reported from clients
    return main_greenlet

def client_listener(client):
    while True:
        msg = client.recv()
        if msg.type == 'config':
            print "got configuration from master"
            print msg.data.get('urls')
        elif msg.type == 'quit':
            print msg.data


def slave(args):
    print "running as slave"
    # start up rpc client
    client = rpc.Client(args.master_host, args.master_port)
    # signal ready state to master
    print "sent message to {0}:{1}".format(args.master_host, args.master_port)
    client.send(Message('client-started','greetings master','my uuid'))
    # receive configuration and store
    # wait for run command
    main_greenlet = gevent.spawn(client_listener, client)
    # run requests until receive stop command
    # report stats
    # shutdown if requested
    return main_greenlet


if __name__ == '__main__':
    main()
