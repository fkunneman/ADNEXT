#!/usr/bin/env python

import argparse
from evalset import Evalset
from collections import defaultdict
import re
import time_functions

parser = argparse.ArgumentParser(description = "Program to evaluate the time-to-event of timetagged tweets")

parser.add_argument('-i', action = 'store', required = True, nargs='+', help = "the timetagged files")
parser.add_argument('-e', action='store', required = True, help = "the file with scores and estimations")
parser.add_argument('-o', action='store', required = True, help = "the results file")
parser.add_argument('-t', action='store', type=float, default = 1.0, help = "The threshold parameter")

args = parser.parse_args()

for eventfile in args.i:
    window_timetags = defaultdict(list)
    eventopen = open(eventfile)
    for line in eventopen.readlines():
        tokens = line.strip().split("\t")
        spl = tokens[0].split(" ")
        vals = [spl[1]] + tokens[1:]
        window_timetags[int(spl[0])].append(vals)

window_weight = defaultdict(lambda: defaultdict(list))
date = re.compile(r"\d{4}-\d{2}-\d{2}")
date_time = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
period = re.compile(r"P(\d+|X)(WE|W|M|Y|D|H)")
dateweek = re.compile(r"\d{4}-w\d+")
for window in sorted(window_timetags.keys())[:10]:
    weights = defaultdict(list)
    timetags = window_timetags[window]
    for timetag in timetags:
        estimation = timetag[-1]
        if date.match(estimation):
            estimation_date = time_functions.return_datetime(estimation,setting="vs")
            multiplyer = 1
        elif date_time.match(estimation):
            estimation_date = time_functions.return_datetime(estimation.split(" ")[0],setting="vs")
            multiplyer = 0.5
        elif period.match(estimation):
            print timetag[-2],estimation
        elif dateweek.match(estimation):
            print estimation

        #tte =  - time_functions.return_datetime(timetag[1],setting="vs")



    #print window,window_timetags[window]


