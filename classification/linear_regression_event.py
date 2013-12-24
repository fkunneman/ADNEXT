#!/usr/bin/env python

import argparse
from collections import defaultdict
from itertools import chain
import numpy

"""
Script to perform simple linear regression adapted to tweet distributions for an event
"""
parser=argparse.ArgumentParser(description="Script to perform simple linear regression adapted to tweet distributions for an event")
parser.add_argument('-i', action='store', nargs = '+', required=True, help="files with event tweets")
parser.add_argument('-l', action='store', type = int, default = 0, help="specify the column with the time-to-event label" )
parser.add_argument('-n', action='store', type = int, default=10, help="specify n for n-fold")
parser.add_argument('-d', action='store', help = "the output directory")

args=parser.parse_args() 

#make train_test sets
event_buckets = defaultdict(list)
for ef in args.i:
    instance_file = open(ef)
    instances_raw=instance_file.readlines()
    instance_file.close()
    event_txt = "/".join(ef.split("/")[depth:])
    event = re.sub(".txt","",event_txt)
    tte_tweets = defaultdict(int)
    for tweet in instances_raw:
        values = tweet.strip().split("\t")
        tte = values[args.d]
        tte_tweets[tte] += 1
    #make pairs of the time_to_event and the (logged) number of tweets in this period 
    buckets = [(tte,math.log(tte_tweets[tte],2)) for tte in tte_tweets.keys()]
    event_buckets[event] = buckets       

#for each train-test
events = event_buckets.keys()
testlen = int(len(events)/10)
for i in range(0,len(events),testlen):
    try:
        train_events = events[:i] + events[i+testlen:]
        test_events = [events[j] for j in range(i,i+testlen)]
    except IndexError:
        train_events = events[:i]
        test_events = [events[j] for j in range(i,len(events))]
    train = sum([event_instances[x] for x in train_events],[])
    test = []
    for event in test_events:
        testdict = {}
        eventout = args.d + event + ".txt"
        testdict["out"] = eventout
        testdict["instances"] = event_buckets[event]
        test.append(testdict)
    #make model
    trainbuckets = list(chain([event_buckets[e] for e in train_events]))
    targetvect = [t[0] for t in trainbuckets]
    valuevect = [t[1]] for t in trainbuckets]
    print trainbuckets
    print targetvect
    print valuevect
    print len(targetvect),len(valuevect)



#predict tte







