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

ordered_tweets = []
windows = [] 
#generate ordered list of timetagged tweets

#extract tweets from datefile and make a date-tweets dict
date_tweets = defaultdict(list)

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
    print date
    tagged = date_tweets[date]
    metatweets_in = codecs.open(args.i + date + ".txt","r","utf-8")
    metatweets = metatweets_in.readlines()
    metatweets_in.close()
    metatweets_filt = []
    for t in metatweets:
        tokens = t.split("\t")
        if not re.search("RT",tokens[-1]):
            metatweets_filt.append(t)
    for i,tweet in enumerate(metatweets_filt):
            tokens = tweet.strip().split("\t")
            try:
                ordered_tweets.append({"label":tokens[0],"meta":tokens,"text":tagged[i]})
            except:
                print date,i,len(tagged)

i=0
while i+args.window < len(ordered_tweets):
    window = {"label":str(i+args.window) + " " + ordered_tweets[i+args.window]["label"], "meta":ordered_tweets[i+args.window]["meta"],"features":[]}
    for t in ordered_tweets[i:i+args.window]:
        if re.search("<TIMEX3",t["text"]):
            tt = {}
            time_extract = re.search('<TIMEX3 (.+)</TIMEX3>', t["text"])
            time_info = time_extract.group(1)
            meta_word = time_info.split(">")
            tt["target"] = meta_word[1]
            if re.search("</TIMEX3",meta_word[1]):
                print t["text"],time_info,meta_word
            meta = meta_word[0].split(" ")
            for m in meta:
                kv = m.split("=")
#                print meta_word,meta,m,kv
                tt[kv[0]] = re.sub("\"","",kv[1])
            window["features"].append(tt)
#     windows.extend([{"features":t["text"],"label":str(i+args.window) + " " + window["label"],"meta":window["meta"]} for t in ordered_tweets[i:i+args.window]])
    i+=args.step
    windows.append(window)

#for w in windows[:50]:
#    for f in w["features"]:
	# print w["label"],w["meta"][3],f




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
