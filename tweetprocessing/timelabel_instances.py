#!/usr/bin/env python

import argparse
import codecs
import time_functions
from collections import defaultdict
import datetime

"""
Presumes file for 1 event
"""
parser = argparse.ArgumentParser(description = "")
parser.add_argument('-i', action = 'store', required = True, help = "the input file")  
parser.add_argument('-o', action = 'store', required = True, help = "the output file")
parser.add_argument('-d', action = 'store', type=int, required = True, help = "field with the tweet date")
parser.add_argument('-t', action = 'store', type=int, required = True, help = "field with the tweet time")
parser.add_argument('-e', action = 'store', required = True, help = "file with event-time information")
parser.add_argument('-n', action = 'store', required = True, help = "event name")
parser.add_argument('-u', action = 'store', choices = ["day","hour","minute"], default='day', help = "specify the unit of time for the timelabel")
parser.add_argument('-b', action = 'store', type=int, required = False, help = "for the inclusion of an early" + 
    "class, specify before which amount of time units this label is given")
args = parser.parse_args() 

tweetfile = codecs.open(args.i,"r","utf-8")
outfile = codecs.open(args.o,"w","utf-8")

eventhash = time_functions.generate_event_time_hash(args.e)
event_time = eventhash[args.n]
for tweet in tweetfile.readlines():
    tokens = tweet.split("\t")
    tweet_datetime = time_functions.return_datetime(tokens[args.d],tokens[args.t],setting="vs")
    #Extract the time difference between the tweet and the event 
    if tweet_datetime < event_time[0]:
        tweet_event_time=time_functions.timerel(event_time[0],tweet_datetime,args.u) * -1
        if args.b and tweet_event_time < args.b:
            label="early"
        else:
            label=str(tweet_event_time)
    else:
        if tweet_datetime < event_time[1]:
            label="during"
        else:
            label="after"
    tokens = [label] + tokens
    outfile.write("\t".join(tokens))
