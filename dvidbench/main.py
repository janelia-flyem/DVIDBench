import argparse
import dvidbench
import os
import web
import gevent
import rpc
from rpc import Message

def parse_command_arguments():
    parser = argparse.ArgumentParser(description='Benchmark a DVID server')
    parser.add_argument('-v', '--version', action="version", version=dvidbench.__version__ )
    parser.add_argument('-d', '--debug',  help='print extra debugging information', action='store_true')

    parser.add_argument('config', help='location of the configuration file', nargs='?', default=os.path.expanduser('~/.dvidbenchrc'))

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

def master_listener(server):
    while True:
        msg = server.recv()
        if msg:
            print "received: {}".format(msg.data)


def master(args):
    # start up web gui thread
    main_greenlet = gevent.spawn(web.start, args)
    # start up rpc server
    server = rpc.Server(args.master_host, args.master_port)
    # wait for commands from web interface
    gevent.spawn(master_listener, server)
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
        if msg:
            print msg

def slave(args):
    print "running as slave"
    # start up rpc client
    client = rpc.Client(args.master_host, args.master_port)
    # signal ready state to master
    print "sent message to {0}:{1}".format(args.master_host, args.master_port)
    client.send(Message('client-start','greetings master','my uuid'))
    # receive configuration and store
    # wait for run command
    main_greenlet = gevent.spawn(client_listener, client)
    # run requests until receive stop command
    # report stats
    # shutdown if requested
    return main_greenlet


if __name__ == '__main__':
    main()
