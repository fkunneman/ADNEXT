#! /usr/bin/env python

import argparse
from collections import defaultdict
from os import listdir
import re
import codecs

parser=argparse.ArgumentParser(description="Program to perform a classification experiment with time-tagged event tweets in a sliding window fashion")
parser.add_argument('-t', action='store', required=True, help="the directory with time-tagged tweets")
parser.add_argument('-i', action='store', help="the directory with meta-tagged tweets")
# parser.add_argument('-d', action='store', type=int, help="the date-column in the ordered tweetfile")
parser.add_argument('--step', action='store', default=1, type=int, help="specify the stepsize of instance windows; [DEFAULT] = 1")
parser.add_argument('--window', action='store', default=100, type=int, help="specify the size of instance windows; [DEFAULT] = 100")

args = parser.parse_args()

#generate ordered list of timetagged tweets

#extract tweets from datefile and make a date-tweets dict
date_tweets = defaultdict(list)
ordered_tweets = []
for f in listdir(args.t):
    date = re.sub(".txt","",f)
    datefile = codecs.open(args.t + f,"r","utf-8")
    within = False
    for line in datefile.readlines():
        if within:
            if not re.search("</TimeML>",line):
                if not re.search("RT",line) and not re.match("\n",line):
                    date_tweets[date].append(line)
        else:
            if re.search("<TimeML>",line):
                within = True
    datefile.close()

for date in sorted(date_tweets.keys()):
    tagged = date_tweets[date]
    metatweets = codecs.open(args.i + date + ".txt","r","utf-8")
    for i,tweet in enumerate(metatweets.readlines()):
        tokens = tweet.split("\t")
        if not re.search("RT",tokens[-1]):
            try:
                ordered_tweets.append({"label":tokens[0],"meta":tokens[:-1],"text":tagged[i]})
            except:
                print i,tagged
                

print ordered_tweets

# exit()

# ordered_tweets_timex = []
# for line in ordered_tweets.readlines():
#     instance = {}
#     tokens = line.strip().split("\t")
#     date = tokens[args.d]
#     tweet = tokens[-1]
#     if not re.search("RT",tweet):
#         tagged_tweet = date_tweets[date].pop(0)
#         print tagged_tweet







#generate windows from the list




#print info in window
