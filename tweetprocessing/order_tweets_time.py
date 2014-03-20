#!/usr/bin/env python

import argparse
import codecs
import time_functions
from collections import defaultdict

"""
Script to sort tweets by time.
"""
parser = argparse.ArgumentParser(description = "Script to sort tweets by time.")
parser.add_argument('-i', action = 'store', required = True, help = "the input file")  
parser.add_argument('-o', action = 'store', required = True, help = "the output file")
parser.add_argument('-d', action = 'store', type=int, required = True, help = "field with the tweet date")
parser.add_argument('-t', action = 'store', type=int, required = True, help = "field with the tweet time")

args = parser.parse_args()

tweetdict = defaultdict(list)
fileread = codecs.open(args.i,"r","utf-8")
for line in fileread.readlines():
    tokens = line.strip().split("\t")
    tweet_datetime = time_functions.return_datetime(tokens[args.d],time=tokens[args.t],setting="vs")
    tweetdict[tweet_datetime].append(line)
fileread.close()

outfile = codecs.open(args.o,"w","utf-8")
for dt in sorted(tweetdict):
    for tweet in tweetdict[dt]:
        outfile.write(tweet)
outfile.close()
