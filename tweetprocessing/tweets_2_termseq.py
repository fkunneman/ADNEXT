#!/usr/bin/env python

import argparse
import datetime
from collections import defaultdict
import codecs
import time_functions
import re

parser = argparse.ArgumentParser(description = "Program to sort tweets in time and make sequences of words")

parser.add_argument('-i', action = 'store', required = True, nargs='+', help = "the infiles")
parser.add_argument('-o', action='store', required=True, help = "the outfile")
parser.add_argument('-u', action = 'store', default = "day", choices = ["day","hour","minute"], help="specify the time unit to divide tweets by")
parser.add_argument('-d', action='store', default = 2, type = int, help = "the date column in the tweet")
parser.add_argument('-t', action='store', default = 3, type = int, help = "the time column in the tweet")
args = parser.parse_args()

outfile = codecs.open(args.o,"w","utf-8")
word_timewindow = defaultdict(list)

#make time-tweet dict and word vocabulary
time_tweet = defaultdict(list)
words = defaultdict(int)
for f in args.i:
    tweetfile = codecs.open(f,"r","utf-8")
    for tweet in tweetfile.readlines():
        tokens = tweet.strip().split("\t")
        date = tokens[args.d]
        time = tokens[args.t]
        tweet_datetime = time_functions.return_datetime(date,time = time,setting="vs")
        time_tweet[tweet_datetime].extend(tokens[-1].split(" "))
        for word in tokens[-1].split(" "):
            words[word.lower()] += 1
vocabulary = [x for x in words.keys() if words[x] > 1 and not re.search("@",x) and not re.search("http",x)]

#sort tweets in time
sorted_time = sorted(time_tweet.keys())

#for each timepoint
starttime = sorted_time[0]
endtime = sorted_time[-1]
if args.u == "day":
    heap = datetime.timedelta(days=1)
elif args.u == "hour":
    heap = datetime.timedelta(hours=1)
elif args.u == "minute":
    heap = datetime.timedelta(minutes=1)
print "heap",heap
print sorted_time
#count word and add to sequence
windowtime = starttime + heap
time = starttime
i = 0
while i < len(sorted_time):
    wordcount = defaultdict(int)
    time = sorted_time[i]
    words = time_tweet[time]
    for word in words:
        wordcount[word] += 1
    for word in vocabulary: 
        try:
            word_timewindow[word].append(wordcount[word])
        except:
            word_timewindow[word].append(0)
    i += heap

#write to file
for word in vocabulary:
    outfile.write(word + "\t" + "|".join([str(x) for x in word_timewindow[word]]) + "\n")
outfile.close()
