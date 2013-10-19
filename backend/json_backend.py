#!/usr/bin/python

import json
import os
import shutil

from abstract_backend import AbstractBackend
from notes.note import Note

DEFAULT_PATH = os.path.expanduser('~/notes.json')

class NoteNotFound(Exception):
    pass

class JsonBackend(AbstractBackend):
    notes_path = DEFAULT_PATH

    def __init__(self):
        self._notes = []

    def add(self, note):
        """ should we check if repeated? """
        self._notes.append(note)

    def delete(self, note):
        """ returns true if note was deleted, false otherwise """
        if note in self._notes:
            self._notes.remove(note)
            return True

        return False

    def load(self):
        """ shouldn't be called twice... """
        if os.path.exists(self.notes_path) is False:
            return

        with open(self.notes_path, 'r') as fh:
            try:
                notes_list = json.load(fh)
                for n_dict in notes_list:
                    note = Note(**n_dict)
                    self._notes.append(note)
            except ValueError as ex:
                print "Couldn't load notes: %s" % (str(ex))

    def sync(self):
        """ load() should have happened first """
        try:
            shutil.copyfile(self.notes_path, self.notes_backup)
        except IOError:
            pass

        with open(self.notes_path, 'w') as fh:
            json.dump(map(lambda n: n.__dict__, self._notes),
                      fh,
                      indent=4)

    def list(self):
        """ should have been loaded first """
        return self._notes

    @property
    def notes_backup(self):
        return "%s.bak" % (self.notes_path)

def get():
    return JsonBackend()
