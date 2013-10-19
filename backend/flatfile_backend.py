#!/usr/bin/python

import os
import shutil

from abstract_backend import AbstractBackend
from notes.note import Note

DEFAULT_PATH = os.path.expanduser('~/notes')

class NoteNotFound(Exception):
    pass

class FlatFileBackend(AbstractBackend):
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
        with open(self.notes_path, 'r') as fh:
            for l in fh.readlines():
                self._notes.append(Note(text=l.strip()))

    def sync(self):
        """ load() should have happened first """
        shutil.copyfile(self.notes_path, self.notes_backup)
        with open(self.notes_path, 'w') as fh:
            for note in self._notes:
                fh.write(note.text.encode('utf8') + '\n')

    def list(self):
        """ should have been loaded first """
        return self._notes

    @property
    def notes_backup(self):
        return "%s.bak" % (self.notes_path)

def get():
    return FlatFileBackend()
