#!/usr/bin/python

class AbstractBackend:
    """
    Basic interface for storage backend
    """
    def name(self, note):
        raise NotImplementedError()

    def add(self, note):
        raise NotImplementedError()

    def delete(self, note):
        raise NotImplementedError()

    def load(self):
        raise NotImplementedError()

    def sync(self):
        raise NotImplementedError()

    def list(self):
        raise NotImplementedError()

