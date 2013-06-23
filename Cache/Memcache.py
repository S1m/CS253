#!/usr/bin/env python
#
# Created by: Simon Brunet 2013-06-20
#
# Abstract:
#   Memcache abstraction
#
###############################################################################

from google.appengine.api import memcache
import logging
import Observer
import Viewer

class Memcache(Observer.Observer):
    def __init__(self):
        super(Memcache, self).__init__()
  
    # Get an element in memcache, if not, execute the query functor specified
    #   Note: Watch out with Query.run() as it's returning an iterable not data
    def Get(self, key, query, update = False, *args, **kwargs):
        data = memcache.get(key)
        if data is None or update:
            logging.error("Database Hit")
            data = query(*args, **kwargs)
            self.notify(Viewer.TimestampViewer, key)
            self.notify(Viewer.IncrementalCounterViewer, key)
            logging.error(data)
            logging.error("memcache is setting key: " + key)
            memcache.set(key, data)
        return data

    def Flush(self):
        memcache.flush_all()
