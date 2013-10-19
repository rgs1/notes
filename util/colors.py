#!/usr/bin/python

GREEN_STR = '\033[92m%s\033[0m'
RED_STR = '\033[91m%s\033[0m'
YELLOW_STR = '\033[93m%s\033[0m'
BLUE_STR = '\033[94m%s\033[0m'
PURPLE_STR = '\033[95m%s\033[0m'
CYAN_STR = '\033[96m%s\033[0m'

ALL_COLORS = [
    GREEN_STR,
    RED_STR,
    YELLOW_STR,
    BLUE_STR,
    PURPLE_STR,
    CYAN_STR,
]

def gen_color():
    i = 0
    total_colors = len(ALL_COLORS)
    while True:
        yield ALL_COLORS[i]
        i += 1
        if i == total_colors:
            i = 0
