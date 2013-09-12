#! /usr/bin/env python

import time_functions
import argparse
import codecs
import datetime
from collections import defaultdict
import re

parser = argparse.ArgumentParser(description = "")

parser.add_argument('-i', action='store', required = True, help = 'File with tweets')
parser.add_argument('-g', action='store', default = 12, help = 'Time granularity in hours (default = 12 hours)')
parser.add_argument('--rt', action='store_true', help = 'choose to remove retweets')
# parser.add_argument('-u', action='store', default = 'day', choices = ['day','hour','minute'], help = 'The unit of time by which the difference will be measured (one of \'day\', \'hour\' or \'minute\'')
# parser.add_argument('--begin', action='store', type = int, required = True, help = 'The first unit of time of tweets related to an event to be counted (for example \'-7\' for 7 units before')
# parser.add_argument('--end', action='store', type = int, required = True, help = 'The last unit of time of tweets related to an event to be counted (for example \'5\' for 5 units after')
# parser.add_argument('--weekdays', action='store', nargs='+', default = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"], help = 'Restriction in the days of the week on which an event is held (default = all days)')
# parser.add_argument('--timewindow', action='store', type = int, nargs=2, default = [0,24], help = 'Restriction in the window of time (in hours) within which an event may start on a day (default = all hours)')

args = parser.parse_args() 

datetimes = []
segment_tweets = defaultdict(int)

infile = codecs.open(args.i,"r","utf-8")
for line in infile.readlines()[1:]:
    tokens = line.split("\t")
    date = tokens[2]
    time = tokens[3]
    if args.rt:
        text = tokens[7]
        if re.search(' rt ',text,re.IGNORECASE):
            continue
    dt = time_functions.return_datetime(date,time,"vs")
    datetimes.append(dt)

sorted_datetimes = sorted(datetimes)
start = datetime.datetime(2013,9,9,0,0,0)
end = start + datetime.timedelta(hours=12)
for obj in sorted_datetimes:
    if obj > end:
        start = end
        end = start+datetime.timedelta(hours=12)
    segment_tweets[start] += 1

for time in sorted(segment_tweets.keys()):
    print time.date(),time.time(),segment_tweets[time]



