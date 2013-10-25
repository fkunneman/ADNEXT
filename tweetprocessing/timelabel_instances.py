#!/usr/bin/env python

import argparse
import codecs
import time_functions
from collections import defaultdict
import datetime

"""
Script to put metadata in the right order for tweets_2_features.
Presumes file for 1 event
"""
parser = argparse.ArgumentParser(description = "Script to put metadata in the right order for tweets_2_features.")
parser.add_argument('-i', action = 'store', required = True, help = "the input file")  
parser.add_argument('-o', action = 'store', required = True, help = "the output file")
parser.add_argument('-d', action = 'store', type=int, required = True, help = "field with the tweet date")
parser.add_argument('-t', action = 'store', type=int, required = True, help = "field with the tweet time")
parser.add_argument('-e', action = 'store', required = True, help = "file with event-time information")
parser.add_argument('-n', action = 'store', required = True, help = "event name")
parser.add_argument('-u', action = 'store', choices = ["day","hour","minute"], default='day', help = "specify the unit of time for the timelabel")
parser.add_argument('-b', action = 'store', type=int, required = False, help = "for the inclusion of an early" + 
    "class, specify before which anount of time units this label is given")
args = parser.parse_args() 

tweetfile = codecs.open(args.i,"utf-8","r")
outfile = codecs.open(args.o,"utf-8","r")

eventhash = time_functions.generate_event_time_hash(args.e)
event_time = eventhash[args.n]
for tweet in tweetfile.readlines():
    tokens = tweet.split("\t")
    time = time_functions.return_datetime(tokens[args.d],tokens[args.t],"vs")
    #Extract the time difference between the tweet and the event 
    if tweet_datetime < event_datetime_begin:
        tweet_event_time=time_functions.timerel(event_datetime_begin,tweet_datetime,timeunit) * -1
        if args.b and tweet_event_time < args.b:
            label="early"
        else:
            label=str(tweet_event_time)
    else:
        if tweet_datetime < event_datetime_end:
            label="during"
        else:
            label="after"
    tokens = label + tokens
    outfile.write("\t".join(tokens))