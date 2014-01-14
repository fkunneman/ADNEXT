#! /usr/bin/env python

import argparse
import gzip
import codecs

parser = argparse.ArgumentParser(description = "Program to sample Dutch tweets from an extended \
    period")

parser.add_argument('-i', action = 'store', nargs = '+', required = True, 
    help = "the input files")
parser.add_argument('-n', action = 'store', type = int, required = True, 
    help = "the number of tweets to sample")
parser.add_argument('-t', action = 'store_true', required = True, 
    help = "choose to smooth sample over time")

args = parser.parse_args()

tweets = []
#open files
for i in args.i:
    if i[-2:] == "gz":
        infile = gzip.open(i,"rb")
    else:
        infile = codecs.open(i,"r","utf-8")
    tweets.extend(infile.readlines())
    infile.close
    print len(tweets)

#count tweets



#if smooth: 
#   make time dict of day-hours
#   sample 1/24 from each hour


# else:
# sample randomly from all