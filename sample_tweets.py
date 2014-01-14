#! /usr/bin/env python

from __future__ import division
import argparse
import gzip
import codecs
import random
from collections import defaultdict

import time_functions

parser = argparse.ArgumentParser(description = "Program to sample Dutch tweets from an extended \
    period")

parser.add_argument('-i', action = 'store', nargs = '+', required = True, 
    help = "the input files")
parser.add_argument('-o', action = 'store', required = True,
    help = "the output file")
parser.add_argument('-n', action = 'store', type = int, required = True, 
    help = "the number of tweets to sample")
parser.add_argument('-t', action = 'store_true', help = "choose to smooth sample over time")
parser.add_argument('-d', action = 'store', type = int, required = False,
    help = "the column with date information (for time smoothing)")
parser.add_argument('-m', action = 'store', type = int, required = False,
    help = "the column with time information (for time smoothing)")

args = parser.parse_args()

tweets = []
#open files
print "reading in files..."
for i in args.i:
    print i
    if i[-2:] == "gz":
        infile = gzip.open(i,"rb")
        tweets.extend([x.decode('utf-8') for x in infile.readlines()])
	infile.close()
    else:
        infile = codecs.open(i,"r","utf-8")
    	tweets.extend(infile.readlines())
    	infile.close

outfile = codecs.open(args.o,"w","utf-8")
#if smooth: 
if args.t:
    #make time dict of day-hours
    print "dividing data in hours..."
    hour_tweets = defaultdict(list)
    for tweet in tweets:
        tokens = tweet.split(" ")
        if tokens[0] == "dutch":
            try:
                dt = time_functions.return_datetime(date = tokens[args.d],time=tokens[args.m],setting="vs")
                hour_tweets[dt.hour].append(tweet)
            except:
                print tokens

    print "extracting samples and writing to file..."
    percent = args.n / len(tweets)
    sampled = []
    for i,hour in enumerate(hour_tweets.keys()):
        print hour
        htweets = hour_tweets[hour]
        if i == 23:
            extract = args.n - len(sampled)
        else:
            extract = int(round(len(htweets)/len(tweets),0))      
        sampled.extend(random.sample(htweets, extract))
        print extract,len(htweets),len(sampled)
    for line in sampled:
        outfile.write(line)

# else sample randomly from all
else:
    print "extracting sample and writing to file..."
    sample = random.sample(tweets,args.n)
    for line in sample:
        outfile.write(line)

outfile.close()
