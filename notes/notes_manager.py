#!/usr/bin/python
#
#

import os
import re
import readline
import sys
from pygsr import Pygsr
from Levenshtein import ratio

from backend.storage import get_backend
from note import Note
from util import colors
from util import priority
from util import state
from util.date import human_to_timestamp, timestamp_to_human

DEFAULT_MATCH_THRESHOLD = 0.70
DEFAULT_BACKEND = "json"

class NotesManager():
    def __init__(self, backend, interactive, lang='en_US', duration=3):
        self.duration = duration
        self.lang = lang
        self.debug = False
        self.match_threshold = DEFAULT_MATCH_THRESHOLD
        self.interactive = interactive
        self.backend = \
            get_backend(DEFAULT_BACKEND if backend is None else backend)
        self.backend.load()

    def add(self, **kwargs):
        self._do_add(kwargs['title'],
                     kwargs['body'],
                     kwargs['priority'],
                     kwargs['due_on'],
                     kwargs['tags'])

    def add_voice(self, **kwargs):
        title = self._voice_input(self.duration)
        self._do_add(title)

    def get(self, what):
        if what == 'titles':
            return map(lambda n: n.title, self.backend.list())
        elif what == 'tags':
            return self.get_tags()
        elif what == 'due_on':
            return self.get_due_on_dates()
        elif what == 'priority':
            return priority.VALID_PRIORITIES
        else:
            raise ValueError(what)

    def get_due_on_dates(self):
        tstamps = list(set(map(lambda n: n.due_on, self.backend.list())))
        tstamps.sort()
        return map(lambda tstamp: timestamp_to_human(tstamp), tstamps)

    def get_tags(self):
        tags = set()
        for note in self.backend.list():
            tags |= set(note.tags)
        tags = list(tags)
        tags.sort()
        return tags

    def list(self, **kwargs):
        if kwargs['what'] == 'notes':
            for note in self.backend.list():
                sys.stdout.write(str(note) + '\n')
        elif kwargs['what'] == 'tags':
            gen = colors.gen_color()
            for tag in self.get_tags():
                sys.stdout.write(gen.next() % (tag) + '\n')

    def voice_delete(self, **kwargs):
        needle = self._voice_input(self.duration)
        self._delete(needle)

    def delete(self, **kwargs):
        self._delete(kwargs['needle'])

    def update(self, **kwargs):
        attrib='title'
        needle = kwargs['needle']
        if ':' in needle:
            attrib, needle = needle.split(':')

        for note in self._do_search(needle, attrib):
            sys.stdout.write("%s\n" % (str(note)))
            if self._confirm("Edit?"):
                # title
                modified = self._rlinput("title> ", note.title)
                if modified != note.title:
                    note.title = modified

                # body
                new_body = []
                modified = self._rlinput("body> ", note.body)
                new_body.append(modified)
                while True:
                    modified = self._rlinput("", "")
                    if modified == '':
                        break

                    new_body.append(modified)

                modified = '\n'.join(new_body)
                if modified != note.body:
                    note.body = modified

                # edit priority
                self._edit(note, 'priority', priority.VALID_PRIORITIES)

                # edit state
                self._edit(note, 'state', state.VALID_STATES)

                # edit due date
                cur_due_on = timestamp_to_human(note.due_on)
                modified = self._rlinput('due on> ', cur_due_on)
                modified = human_to_timestamp(modified)
                if modified != note.due_on:
                    note.due_on = modified

                # edit existing tags
                new_tags = []
                for t in note.tags:
                    modified = self._rlinput("tag> ", t)

                    if modified == '':
                        continue

                    new_tags.append(modified)

                # add new tags
                while True:
                    t = self._rlinput("tag> ", "")
                    if t == '':
                        break
                    new_tags.append(t)

                note.tags = new_tags

                if self._confirm("Save?"):
                    self.backend.sync()

    def search(self, **kwargs):
        attrib='title'
        needle = kwargs['needle']
        if ':' in needle:
            attrib, needle = needle.split(':', 1)

        if attrib == 'due_on':
            # extract operator and value
            m = re.match("(<|<=|==|>|>=)\s*(.+)", needle)
            if m:
                operator = m.group(1)
                needle = m.group(2)
            else:
                operator = '=='

            needle = human_to_timestamp(needle)
            self._search_by_date(operator, needle, attrib)
        else:
            self._search_needle(needle, attrib)

    def voice_search(self, **kwargs):
        needle = self._voice_input(self.duration)
        self._search_needle(needle)

    def _search_needle(self, needle, attrib='title'):
        for note in self._do_search(needle, attrib):
            sys.stdout.write("%s\n" % (str(note)))

    def _edit(self, note, attrib, valid_values):
        invalid_msg = 'Invalid %s\n' % (attrib)
        cur_value = getattr(note, attrib)

        while True:
            modified = self._rlinput('%s> ' % (attrib), cur_value)

            if modified == cur_value:
                break

            if modified in valid_values:
                setattr(note, attrib, modified)
                break

            sys.stdout.write(invalid_msg)

    def _do_add(self, title, body='', priority='low', due_on='1 week', tags=[]):
        note = Note(title=title,
                    body=body,
                    priority=priority,
                    due_on=due_on,
                    tags=tags)

        sys.stdout.write(str(note))
        if not self.interactive or self._confirm("Save?"):
            self.backend.add(note)
            self.backend.sync()

    def _delete(self, needle):
        deleted = False
        attrib='title'
        if ':' in needle:
            attrib, needle = needle.split(':')

        for note in self._do_search(needle, attrib):
            sys.stdout.write("%s\n" % (str(note)))
            if self._confirm("Delete?"):
                self._delete_note(note)
                deleted = True

        if deleted:
            self.backend.sync()
        else:
            sys.stdout.write('No matches found\n')

        return deleted

    def _voice_input(self, duration):
        speech = Pygsr()
        speech.record(duration)
        phrase, complete_response = speech.speech_to_text(self.lang)
        return phrase

    def _confirm(self, msg, colors=True):
        if colors:
            msg = "\033[91m%s\033[0m (y|n):" % (msg)

        return raw_input("%s " % (msg)) == "y"

    def _delete_note(self, note):
        self.backend.delete(note)

    def _search_by_date(self, operator, needle, attrib):
        for note in self.backend.list():
            expr = "%f %s %f" % (getattr(note, attrib), operator, needle)

            if self.debug:
                print "_search_by_date: %s" % (expr)

            if eval(expr) is True:
                sys.stdout.write("%s\n" % (str(note)))

    def _do_search(self, needle, by_attrib='title'):
        matches = []

        if self.debug:
            print "Starting search with threshold: %f" % \
                (self.match_threshold)

        for note in self.backend.list():
            if self._match(needle, getattr(note, by_attrib)):
                matches.append(note)

        return matches

    def _match(self, needle, attrib_value):
        if type(attrib_value) == type([]):
            for sub_v in attrib_value:
                ret = self._do_match(needle, sub_v)
                if ret:
                    return True
        else:
            return self._do_match(needle, attrib_value)

        return False

    def _do_match(self, needle, note_attrib_value):
        for token_note in note_attrib_value.split():
            for token_needle in needle.split():
                result = ratio(unicode(token_note), unicode(token_needle))
                if self.debug:
                    print "Searching match for %s against %s got: %f" % \
                        (token_needle, token_note, result)
                if result >= self.match_threshold:
                    return True
        return False

    def _rlinput(self, prompt, prefill):
        readline.set_startup_hook(lambda: readline.insert_text(prefill))
        try:
            return raw_input(prompt)
        finally:
            readline.set_startup_hook()
        return prefill
