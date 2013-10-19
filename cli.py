#!/usr/bin/python

import sys

from util.cmdline_parser import CmdlineParser
from util import priority
from notes.notes_manager import NotesManager
from notes.notes_shell import NotesShell

if __name__ == '__main__':
    sub_cmds = {
        'add':
            [('title', {}),
             ('body', {'default': '', 'nargs': '?'}),
             ('priority', {'default': 'low', 'nargs': '?', 'choices': priority.VALID_PRIORITIES}),
             ('due_on', {'default': '1 week', 'nargs': '?'}),
             ('tags', {'default': [], 'nargs': '*'})],
        'add_voice': [],
        'delete':
            [('needle', {})],
        'voice_delete': [],
        'search':
            [('needle',
              {'help': 'the term to search for or alternatively use attrib:needle notation where ' \
                   'attrib is one of title, body or tag'})],
        'voice_search': [],
        'update':
            [('needle',
              {'help': 'the term to search for or alternatively use attrib:needle notation where ' \
                   'attrib is one of title, body or tag'})],
        'list':
            [('what', {'default': 'notes', 'nargs': '?', 'choices': ['notes', 'tags']})],
        'shell': [],
        }

    global_opts = {
        '--debug': {'action': 'store_true', 'default': False},
        '--match-threshold': {'default': 0.0, 'type': float},
        '--backend': {},
        '--non-interactive': {'action': 'store_true', 'default': False},
        }

    cparser = CmdlineParser()
    parsed_opts = cparser.build_and_parse(sub_cmds,
                                          None,
                                          global_opts)
    kwargs = parsed_opts.__dict__
    cmd = kwargs.pop('cmd')

    try:
        nm = NotesManager(kwargs['backend'],
                          not kwargs['non_interactive'])
        if kwargs['match_threshold'] > 0.0:
            nm.match_threshold = kwargs['match_threshold']
        nm.debug = kwargs['debug']
        if cmd == 'shell':
            NotesShell(nm).run()
        else:
            getattr(nm, cmd)(**kwargs)
    except KeyboardInterrupt:
        # TODO(rgs): each cmd should handle this individually
        pass
