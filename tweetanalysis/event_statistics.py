#!/usr/bin/env python

import argparse
import gen_functions
import tweetsfeatures

"""
Describe the statistics of an event set.
"""
parser = argparse.ArgumentParser(description = "Describe the statistics of an event set.")
parser.add_argument('-i', action = 'store', required = True, nargs="+", help = "the input files")  
parser.add_argument('-o', action = 'store', required = True, help = "the output file")
parser.add_argument('-s', action = 'store', required = True, help = "the name of the event set")
parser.add_argument('-f', action = 'store', type=int, help = "the size of the tweet frame")

args = parser.parse_args()

#generate list of tweet counts and list of tte at frame
counts = []
tte_at_frame = []
for f in args.i:
    tweets = tweetsfeatures.Tweetsfeatures(f)
    tweets.set_wordsequences()
    tweets.filter_tweets(["rt"])
    counts.append(len(tweets.instances))
    tte_at_frame.append(int(tweets.instances[args.f].label))

#calculate mean and median and write to file
print counts
print tte_at_frame

fileout = open(args.o,"a")
fileout.write("\nStatistics of " + args.s + "\n")
cmean = sum(counts) / len(counts)
cmedian = sorted(counts)[int(len(counts)/2)]
cstdev = gen_functions.return_standard_deviation(counts)
tmean = sum(tte_at_frame) / len(tte_at_frame)
tmedian = sorted(tte_at_frame)[int(len(tte_at_frame)/2)]
tstdev = gen_functions.return_standard_deviation(tte_at_frame)
fileout.write("count statistics: mean - " + str(cmean) + " standard deviation - " + str(cstdev) + " median " + str(cmedian) + "\ntte statistics: mean - " + str(tmean) + " standard deviation " + str(tstdev) + " median " + str(tmedian) + "\n")
