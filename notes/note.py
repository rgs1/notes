#!/usr/bin/python

import time

from util import colors
from util import priority
from util.date import human_to_timestamp, timestamp_to_human

class Note(object):
    def __init__(self, title,
                 body='',
                 tags=[],
                 priority='low',
                 state='pending',
                 due_on='1 week',
                 created_on=time.time()):
        self.title = title
        self.body = body
        self.tags = tags
        self.priority = priority
        self.state = state

        if type(due_on) == str:
            due_on = human_to_timestamp(due_on)

        self.due_on = due_on
        self.created_on = created_on
    
    def __str__(self, colors_on=True, show_date=True):
        if colors_on:
            title = colors.GREEN_STR % ('title:')
            tags = colors.RED_STR % ('tags:')
            created_on = colors.YELLOW_STR % ('created on:')
            state = colors.PURPLE_STR % ('state:')
            prio = colors.BLUE_STR % ('priority:')
            due_on = colors.CYAN_STR % ('due on:')
        else:
            title = 'title:'
            tags = 'tags:'
            created_on = 'created on:'
            state = 'state:'
            prio = 'priority:'
            due_on = 'due on:'

        s = ""
        if self.title and self.title != "":
            s += "%s: %s\n" % (title, self.title)

        if self.body and self.body != "":
            s += "%s\n" % (self.body)

        if self.tags and len(self.tags) > 0:
            s += "%s: %s\n" % (tags, self.tags_as_str())

        s += "%s: %s\n" % (state, self.state)

        s += "%s: %s\n" % (prio, self.priority)

        s += "%s: %s\n" % (due_on, timestamp_to_human(self.due_on))

        if show_date:
            s += "%s: %s\n" % (created_on, timestamp_to_human(self.created_on))

        return s

    @property
    def __dict__(self):
        return {
            'title': self.title,
            'body': self.body,
            'state': self.state,
            'priority': self.priority,
            'tags': self.tags,
            'due_on': self.due_on,
            'created_on': self.created_on,
            }

    def tags_as_str(self):
        return ','.join(self.tags)
