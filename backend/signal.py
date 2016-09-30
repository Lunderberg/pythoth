#!/usr/bin/env python3

class Signal:
    def __init__(self):
        self.callbacks = []

    def connect(self, func):
        self.callbacks.append(func)

    def disconnect(self, func):
        self.callbacks.remove(func)

    def disconnect_all(self):
        del self.callbacks[:]

    def emit(self, *args, **kwargs):
        for callback in self.callbacks:
            callback(*args, **kwargs)
