# copied from http://locust.io event object under MIT license

class EventHook(object):
    """
    Here's how to use the EventHook class::

        my_event = EventHook()
        def on_my_event(a, b, **kw):
            print "Event was fired with arguments: %s, %s" % (a, b)
        my_event += on_my_event
        my_event.fire(a="foo", b="bar")
    """

    def __init__(self):
        self._handlers = []

    def __iadd__(self, handler):
        self._handlers.append(handler)
        return self

    def __isub__(self, handler):
        self._handlers.remove(handler)
        return self

    def fire(self, **kwargs):
        for handler in self._handlers:
            handler(**kwargs)

client_report = EventHook()
# indicates that a client has reported some statistics.


client_ready = EventHook()
# run when the client has parsed the configuration and is ready to start running
# jobs.


