#! /usr/bin/env python

import argparse
from collections import defaultdict
from os import listdir

parser=argparse.ArgumentParser(description="Program to perform a classification experiment with time-tagged event tweets in a sliding window fashion")
parser.add_argument('-t', action='store', required=True, help="the directory with time-tagged tweets")
parser.add_argument('-i', action='store', help="the file with ordered tweets in time")
parser.add_argument('--step', action='store', default=1, type=int, help="specify the stepsize of instance windows; [DEFAULT] = 1")
parser.add_argument('--window', action='store', default=100, type=int, help="specify the size of instance windows; [DEFAULT] = 100")
args = parser.parse_args()

#generate ordered list of timetagged tweets

#extract tweets from datefile and make a date-tweets dict
date_tweets = defaultdict(list)
for f in listdir(args.t):
    print f



#generate windows from the list




#print info in window
