#! /usr/bin/env python

import argparse
from evalset import Evalset
from collections import defaultdict
import re
import time_functions
import datetime
from dateutil.relativedelta import relativedelta

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
date = re.compile(r"\d{4}-\d{2}-\d{2}(T.+)$")
date_time = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
period = re.compile(r"P(\d+|X)(WE|W|M|Y|D|H)")
dateweek = re.compile(r"\d{4}-w\d+")
for window in sorted(window_timetags.keys())[:10]:
    weights = defaultdict(float)
    timetags = window_timetags[window]
    for timetag in timetags:
        tweetdate = time_functions.return_datetime(timetag[2],setting="vs")
        windowdate = time_functions.return_datetime(timetag[1],setting="vs")
        #print timetag
        estimation = timetag[-1]
        #print estimation
        if date.match(estimation):
            estimation_date = time_functions.return_datetime(estimation,setting="vs")
            score = 1
        elif date_time.match(estimation):
            estimation_date = time_functions.return_datetime(estimation.split(" ")[0],setting="vs")
            score = 0.5
        elif period.match(estimation):
            cats = period.search(estimation)
            unit = cats.group(2)
            length = cats.group(1)
            if length == "X":
                length = 1
            else:
                length = int(length)
            if unit == "H":
                estimation_date = time_functions.return_datetime(timetag[1],setting="vs")
            elif unit == "D":
                estimation_date = tweetdate + datetime.timedelta(days=length)
            elif unit == "WE":
                tweet_weekday = tweetdate.weekday()
                if tweet_weekday < 5:
                    dif = 5 - tweet_weekday
                else:
                    dif = 5 + (7-tweet_weekday)
                estimation_date = tweetdate + datetime.timedelta(days=dif)
            elif unit == "W":
                estimation_date = tweetdate + datetime.timedelta(days=7)
            elif unit == "M":
                estimation_date = tweetdate + relativedelta(months=length)
            elif unit == "Y":
                estimation_date = tweetdate + relativedelta(years=length)
            score = 0.1
        elif dateweek.match(estimation):
            continue
        tte = time_functions.timerel(windowdate,estimation_date,unit="day")
#        print str(windowdate),str(estimation_date),tte
        print window,timetag,tte,score
        weights[tte] += score
    window_weight[window] = weights
for window in sorted(window_weight.keys()):
    print window,window_timetags[window][0][0],"\t",window_weight[window]

