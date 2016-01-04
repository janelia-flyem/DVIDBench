#!/usr/bin/env python

__version__=0.1

import time
import os
import gevent
from gevent import GreenletExit, monkey
from gevent.pool import Group
import argparse

monkey.patch_all()

import sys



if sys.version_info[0] == 3:
    from urllib.request import urlopen
else:
    from urllib2 import urlopen

total_time = 0
total_requests = 0
max_request = 0
min_request = 100000000000000000000
requests_start = 0

def parse_command_arguments():
    parser = argparse.ArgumentParser(description='Benchmark a DVID server')
    parser.add_argument('config', help='location of the configuration file', nargs='?', default=os.path.expanduser('~/.dvidbenchrc'))

    parser.add_argument('-v', '--version', action="version", version=__version__ )
    parser.add_argument('-d', '--debug',  help='print extra debugging information', action='store_true')
    parser.add_argument('-R', '--random',  help='randomly request urls from the url list', action='store_true')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--slave',  help='set this process to run as a slave worker', action='store_true')
    group.add_argument('--master',  help='set this process to run as the aggregating master', action='store_true')

    parser.add_argument('--master-host',  help='specify the address of the master to report to', action='store')

    return vars(parser.parse_args())

def print_head(url):
    while True:
        #print('Starting %s' % url)
        start = time.time()
        try:
            data = urlopen(url).read()
        except Exception as e:
            print "unable to open {0}: {1}".format(url, e)

        end = time.time() - start
        #print('%s: %s bytes: %r time: %s ms' % (url, len(data), data[:50], end * 1000))
        global total_time
        total_time += end
        global total_requests
        total_requests += 1

        global max_request
        global min_request

        if end > max_request:
            max_request = end
        if end < min_request:
            min_request = end
        gevent.sleep(1)


def print_stats():
        global total_requests
        global total_time
        global max_request
        global min_request
        global requests_start
        while True:
            try:
                sys.stdout.write('reqs: {3}, RPS: {4},  AVG: {0}, Min: {1}, Max:{2}\r'.format((total_time / total_requests) * 1000, min_request * 1000, max_request * 1000, total_requests, total_requests / (time.time() - requests_start) ))
                sys.stdout.flush()
            except Exception as e:
                print "Gathering stats"
            gevent.sleep(1)

def command_input(greenlet, workers):
    while True:
        print "waiting for command input:"
        gevent.socket.wait_read(sys.stdin.fileno())
        cmd = sys.stdin.readline().strip()
        url = 'http://localhost/'
        if cmd == 'a':
            workers.append(greenlet.spawn(print_head, url))
            print "{} concurrent requests running".format(len(workers))
        elif cmd == 'k':
            g = workers.pop()
            greenlet.killone(g)
            print "{} concurrent requests running".format(len(workers))

        else:
            import pdb; pdb.set_trace()
            print "I don't know what you want me to do"

def sig_term_handler():
    logger.info("Got SIGTERM signal")
    gevent.signal(signal.SIGTERM, sig_term_handler)

def main ():
    args = parse_command_arguments()
    print args

    urls = ['http://localhost/']

    greenlet = Group()

    # spawn a bunch of threads to run requests
    workers = [greenlet.spawn(print_head, url) for url in urls]

    print workers

    # start up a command thread
    greenlet.spawn(command_input, greenlet, workers)

    # start up a thread to print out stats to the screen.
    greenlet.spawn(print_stats)

    tstart = time.time()
    global requests_start
    requests_start = tstart
    try:
        greenlet.join()
    except KeyboardInterrupt as e:
        total = time.time() - tstart
        greenlet.kill(block=True)
        print "{}s".format(total)
        global total_requests
        global total_time
        global max_request
        global min_request
        print('AVG: {0} Min: {1}, Max:{2}'.format((total_time / total_requests) * 1000, min_request * 1000, max_request * 1000))

if __name__ == "__main__":
    main()
