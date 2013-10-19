#!/usr/bin/python

import argparse

class CmdlineParser:
    def build_and_parse(self, sub_cmds, args=None, global_opts={}):
        """
        sub_cmds is a dictionary of:
          {
            cmd_name_1: {
                          'arg1': {'nargs': '?'},
                        },
            cmd_name_2: {
                          'arg1': {'choices': ['c1', 'c2']},
                        },
            ...
          }

        If args is None, it'll go for sys.argv
        global_opts contains options that affect all sub cmds.
        """
        parser = argparse.ArgumentParser()
        for opt_flag, opt_params in global_opts.iteritems():
            parser.add_argument(opt_flag, **opt_params)

        cmds_parsers = parser.add_subparsers(dest='cmd')
        for cmd, cmd_args in sub_cmds.iteritems():
            self._cmd_basic_sub_parser(cmds_parsers, cmd, cmd_args)

        if args is None:
            return parser.parse_args()
        else:
            return parser.parse_args(args)

    def _cmd_basic_sub_parser(self, cmds_parsers, name, args):
        add_parser = cmds_parsers.add_parser(name)

        for arg_name, arg_opts in args:
            add_parser.add_argument(arg_name, **arg_opts)

# tests
def test_01():
    sub_cmds = {
        'add':
            [('file', {}),
             ('title', {'nargs': '?', 'default': ''})],
        'delete':
            [('file', {}),
             ('title', {})],
        'list': [],
        }

    expected_options = {
        'cmd': 'add',
        'file': 'something.txt',
        'title': '',
        }

    args = ['add', 'something.txt']
    cparser = CmdlineParser()
    parsed_opts = cparser.build_and_parse(sub_cmds, args)
    print parsed_opts.__dict__
    print expected_options
    assert(parsed_opts.__dict__ == expected_options)

def test_02():
    sub_cmds = {
        'list': [],
        }

    expected_options = {
        'cmd': 'list',
        }

    args = ['list']
    cparser = CmdlineParser()
    parsed_opts = cparser.build_and_parse(sub_cmds, args)
    assert(parsed_opts.__dict__ == expected_options)

if __name__ == '__main__':
    import tests_util

    tests = [eval(m) for m in dir() if m.startswith('test_')]
    tests_util.run_tests(tests)
