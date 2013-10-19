#!/usr/bin/python

import time

import parsedatetime.parsedatetime as pdt


def human_to_timestamp(date_str):
    cal = pdt.Calendar()
    t = cal.parse(date_str)[0]
    return time.mktime(t)

def timestamp_to_human(tstamp):
    return time.strftime("%b %d %Y %H:%M:%S",
                         time.gmtime(tstamp))
