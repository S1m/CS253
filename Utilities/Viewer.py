#!/usr/bin/env python
#
# Created by: Simon Brunet 2013-06-22
#
# Abstract:
#   Viewers to go with the Observer
#
###############################################################################

import datetime

GLOBAL_KEY = 'GLOBAL'

# Viewer that will take a timestamp upon notification
class TimestampViewer(object):
    def __init__(self):
        self._timestamp = {}

    def GetTimeStamp(self, key=GLOBAL_KEY):
        if key in self._timestamp:
            return self._timestamp[key]
        return datetime.datetime.min
    
    def GetAll(self):
        return self._timestamp
    
    # If no key is specified, the global key holds the last notification tStamp
    def update(self, key=GLOBAL_KEY):
        self._timestamp[key] = datetime.datetime.now()
            
# Viewer that will take increment a counter upon notification
class IncrementalCounterViewer(object):
    def __init__(self):
        self._counter = {}

    def GetCount(self, key=GLOBAL_KEY):
        if key in self._counter:
            return self._counter[key]
        return 0

    def update(self, key=GLOBAL_KEY):
        if not key in self._counter:
            self._counter[key] = 0
        else:
            self._counter[key] += 1
