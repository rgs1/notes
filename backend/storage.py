#!/usr/bin/python

import os
import sys

def get_backend(name):
    this_dir = os.path.dirname(__file__)
    if this_dir not in sys.path:
        sys.path.append(this_dir)

    for file_name in os.listdir(this_dir):
        if file_name.endswith('_backend.py'):
            if name == file_name[:-11]:
                backend = __import__(file_name[:-3])
                return backend.get()
