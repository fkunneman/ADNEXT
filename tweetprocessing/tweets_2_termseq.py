#!/usr/bin/env python

import argparse
import datetime
from collections import defaultdict
import codecs
import time_functions
import re
import ucto
import multiprocessing

parser = argparse.ArgumentParser(description = "Program to sort tweets in time and make sequences of words")

parser.add_argument('-i', action = 'store', required = True, nargs='+', help = "the infiles")
parser.add_argument('-o', action='store', required=True, help = "the outfile")
parser.add_argument('-u', action = 'store', default = "day", choices = ["day","hour","minute"], help="specify the time unit to divide tweets by")
parser.add_argument('-d', action='store', default = 2, type = int, help = "the date column in the tweet")
parser.add_argument('-t', action='store', default = 3, type = int, help = "the time column in the tweet")
args = parser.parse_args()

outfile = codecs.open(args.o,"w","utf-8")
ucto_settingsfile = "/vol/customopt/uvt-ru/etc/ucto/tokconfig-nl-twitter"

#make time-tweet dict and word vocabulary
time_words = defaultdict(list)
words = defaultdict(int)
for f in args.i:
    tokenizer = ucto.Tokenizer(ucto_settingsfile)
    tweetfile = codecs.open(f,"r","utf-8")
    for tweet in tweetfile.readlines():
        tokens = tweet.strip().split("\t")
        date = tokens[args.d]
        time = tokens[args.t]
        tweet_datetime = time_functions.return_datetime(date,time = time,setting="vs")
        time_words[tweet_datetime].extend(tokens[-1].split(" "))
        tokenizer.process(tokens[-1])
        for word in [x.text.lower() for x in tokenizer]:
            words[word] += 1
vocabulary = [x for x in words.keys() if words[x] > 1 and not re.search("@",x) and not re.search("http",x)]

#sort tweets in time
sorted_time = sorted(time_words.keys())

#for each timepoint
starttime = sorted_time[0]
endtime = sorted_time[-1]
if args.u == "day":
    heap = datetime.timedelta(days=1)
elif args.u == "hour":
    heap = datetime.timedelta(hours=1)
elif args.u == "minute":
    heap = datetime.timedelta(minutes=1)
#print "heap",heap
#print sorted_time
#count word and add to sequence
#windowtime = starttime + heap
endtime = starttime.date() + heap

timewindows = []
timewindow = []
for t in sorted_time:
    if t.date() < endtime:
        timewindow.append(t)
    else:
        timewindows.append(timewindow)
        timewindow = [t]
        endtime += heap

print "timewindow length",len(timewindows)

word_timewindow = defaultdict(list)
for tw in timewindows:
    wordcount = defaultdict(int)
    for time in tw:
        words = time_words[time]
        for word in words:
            wordcount[word] += 1
    for word in vocabulary: 
        try:
            word_timewindow[word].append(wordcount[word])
        except:
            word_timewindow[word].append(0)

print "wordseq lengths",[len(word_timewindow[word]) for word in vocabulary[:100]]

#write to file
for word in vocabulary:
    outfile.write(word + "\t" + "|".join([str(x) for x in word_timewindow[word]]) + "\n")
outfile.close()
