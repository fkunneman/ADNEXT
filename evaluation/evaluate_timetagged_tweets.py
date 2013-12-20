#!/usr/bin/env python

import argparse
from evalset import Evalset
from collections import defaultdict

parser = argparse.ArgumentParser(description = "Program to evaluate the time-to-event of timetagged tweets")

parser.add_argument('-i', action = 'store', required = True, nargs='+', help = "the timetagged files")
parser.add_argument('-e', action='store', required = True, help = "the file with scores and estimations")
parser.add_argument('-o', action='store', required = True, help = "the results file")
parser.add_argument('-t', action='store', type=float, default = 1.0, help = "The threshold parameter")

args = parser.parse_args()

for eventfile in args.i:
    window_timetags = defaultdict(list)
    eventopen = open(args.i)
    for line in eventopen.readlines():
        tokens = line.strip().split("\t")
        window_timetags[int(tokens[0])].append(tokens[1:])

for window in sorted(window_timetags.keys()):
    print window


