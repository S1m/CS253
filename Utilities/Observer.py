#!/usr/bin/env python
#
# Created by: Simon Brunet 2013-06-20
#
# Abstract:
#   Python Observer Design Pattern Class
#
###############################################################################

class Observer(object):
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        if not observer in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    # Notify a specific viewer
    def notify(self, viewer, *args, **kwargs):
        for observer in self._observers:
            if viewer == type(observer):
                observer.update(*args, **kwargs)
                
    # Notify all viewers (Can't take arguments to be generic)
    def notifyAll(self):
        for observer in self._observers:
            observer.update()

