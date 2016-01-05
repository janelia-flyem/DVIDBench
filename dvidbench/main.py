import argparse
import dvidbench
import os
import web
import gevent
import rpc
import json
import sys
import events
import master
import slave

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
        greenlet = as_slave(args)
    else:
        greenlet = as_master(args)

    try:
        greenlet.join()
    except KeyboardInterrupt as e:
        # shutdown if requested
        events.quitting.fire()
        exit(0)


    return


def as_master(args):
    clients = []

    # start up web gui thread
    main_greenlet = gevent.spawn(web.start, args)

    # start up rpc server
    master.runner = master.Master(args)

    # wait for commands from web interface

    # send commands forward to clients

    # need to use events for the following
        # send configuration to clients
            # on client start
            # on config update
        # log stats reported from clients
        # shutting down

    def on_quit():
        print "sending all clients the quit signal"
        print "closing down"
        master.runner.quit()
    events.quitting += on_quit
    return main_greenlet



def as_slave(args):
    print "running as slave"
    # start up rpc client
    slave.runner = slave.Slave(args)

    # signal ready state to master
    # receive configuration and store
    # wait for run command
    main_greenlet = gevent.spawn(slave.runner.listener)
    # run requests until receive stop command
    # report stats
    # shutdown if requested
    def on_quit():
        print "terminating client"
        slave.runner.quit()
    events.quitting += on_quit
    return main_greenlet


if __name__ == '__main__':
    main()
