#!/usr/bin/python

import atexit
import cmd
import os
import re
import readline
import sys

class NotesShell(cmd.Cmd):
    curdir = '/'
    root_entries = [
        'by_titles',
        'by_tags',
        'by_due_on',
        'by_priority',
        ]

    def __init__(self, notes_manager):
        cmd.Cmd.__init__(self)
        self._notes_manager = notes_manager
        self._update_curdir('/')
        self._setup_path_handlers()
        self._setup_readline()

    def run(self):
        self.cmdloop("")

    def do_ls(self, *args):
        path = self.curdir
        if args[0] != '':
            path = args[0]

        path = self._abspath(path)
        for path_regex, handler in self._ls_handlers.iteritems():
            match = re.match(path_regex, path)
            if match:
                handler(*match.groups())
                return

        sys.stdout.write("Bad path: %s\n" % (path))

    def do_cd(self, *args):
        self._update_curdir(args[0])

    def do_cat(self, *args):
        print args[0]

    def do_pwd(self, *args):
        sys.stdout.write("%s\n" % (self.curdir))

    def do_EOF(self, *args):
        self._exit(True)

    def do_quit(self, *args):
        self._exit(False)

    def do_exit(self, *args):
        self._exit(False)

    def _update_curdir(self, dirpath):
        if dirpath == '..':
            if self.curdir == '/':
                dirpath = '/'
            else:
                dirpath = os.path.dirname(self.curdir)
        elif not dirpath.startswith('/'):
            prefix = self.curdir
            if prefix != '/':
                prefix += '/'
            dirpath = prefix + dirpath

        self.curdir = dirpath
        self.prompt = "%s > " % (dirpath)

    def _exit(self, newline=True):
        if newline:
            sys.stdout.write('\n')
        sys.exit(0)

    def _setup_path_handlers(self):
        self._ls_handlers = {
            '^\/$': self._list_root,
            '^\/by_titles\/?$': self._list_titles,
            '^\/by_tags\/?$': self._list_tags,
            '^\/by_tags/(\w+)\/?$': self._list_notes_for_tag,
            '^\/by_due_on\/?$': self._list_due_on,
            '^\/by_due_on/(\w+ \d+ \d+ \d+:\d+:\d+)\/?$': self._list_for_due_on,
            '^\/by_priority\/?$': self._list_priorities,
            '^\/by_priority/(\w+)\/?$': self._list_notes_for_priority,
            }

    def _list_notes_for_priority(self, priority):
        self._notes_manager.search(needle='priority:%s' % (priority))

    def _list_notes_for_tag(self, tag):
        self._notes_manager.search(needle='tags:%s' % (tag))

    def _list_for_due_on(self, due_on):
        self._notes_manager.search(needle='due_on:<=%s' % (due_on))

    def _list_root(self, *params):
        self._show_entries(self.root_entries)

    def _list_titles(self, *params):
        self._show_entries(self._notes_manager.get('titles'))

    def _list_tags(self, *params):
        self._show_entries(self._notes_manager.get('tags'))

    def _list_due_on(self, *params):
        self._show_entries(self._notes_manager.get('due_on'))

    def _list_priorities(self, *params):
        self._show_entries(self._notes_manager.get('priority'))

    def _show_entries(self, entries):
        for e in entries:
            sys.stdout.write("%s\n" % (e))

    def _abspath(self, path):
        if path.startswith('/'):
            return path
        else:
            return "%s/%s" % (self.curdir, path)

    def _setup_readline(self):
        histfile = os.path.join(os.environ['HOME'], '.notes_history')
        try:
            readline.read_history_file(histfile)
        except IOError:
            pass
        atexit.register(readline.write_history_file, histfile)

if __name__ == '__main__':
    from notes_manager import NotesMananger
    NotesShell(NotesManager("json", True)).run()
