# this test script shows that you don't have to run .join() on a greenlet
# group for it to be running along side the others when .join() is called
# on at least one group. In this example the greenlets group gets the join()
# method called on it, but the others group still executes in parallel.

# tldr; only have to call .join() once to get all greenlets to execute in parallel.

import gevent
from gevent import GreenletExit
from gevent.pool import Group

def active_message():
    while True:
        print "test message"
        gevent.sleep(2)
    return

def sleepy_message():
    while True:
        print "I'm tired"
        gevent.sleep(3)
    return

greenlets = Group()
greenlets.spawn(sleepy_message)

others = Group()
others.spawn(active_message)

greenlets.join()
