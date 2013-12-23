#! /usr/bin/env python

import argparse
from collections import defaultdict
import os
import re
import codecs
import datetime
import time_functions

parser=argparse.ArgumentParser(description="Program to perform a classification experiment with time-tagged event tweets in a sliding window fashion")
parser.add_argument('-t', action='store', required=True, help="the directory with time-tagged tweets")
parser.add_argument('-i', action='store', help="the directory with meta-tagged tweets")
parser.add_argument('-o', action='store', help="the outputfile")
parser.add_argument('--step', action='store', default=1, type=int, help="specify the stepsize of instance windows; [DEFAULT] = 1")
parser.add_argument('--window', action='store', default=100, type=int, help="specify the size of instance windows; [DEFAULT] = 100")

args = parser.parse_args()

print args.o

ordered_tweets = []
windows = [] 
#generate ordered list of timetagged tweets

#extract tweets from datefile and make a date-tweets dict
date_tweets = defaultdict(list)

for f in os.listdir(args.t):
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

weekday = re.compile(r"(maandag|dinsdag|woensdag|donderdag|vrijdag|zaterdag|zondag)$",re.IGNORECASE)
weekdays=["maandag","dinsdag","woensdag","donderdag","vrijdag","zaterdag","zondag"]
i=0
while i+args.window < len(ordered_tweets):
    window = {"label":str(i+args.window) + " " + ordered_tweets[i+args.window]["label"], "meta":ordered_tweets[i+args.window]["meta"],"features":[]}
    for t in ordered_tweets[i:i+args.window]:
        if re.search("<TIMEX3",t["text"]):
            time_extracts = re.findall('<TIMEX3 (.+?)</TIMEX3>', t["text"])
            for e in time_extracts:
                tt = [window["meta"][3],t["meta"][3]]
                meta_word = e.split(">")
                tt.append(meta_word[1])
                meta = meta_word[0].split(" ")
                for m in meta:
                    kv = m.split("=")
    #                print meta_word,meta,m,kv
                    if kv[0] == "value":
                        if weekday.match(tt[2]):
                            date = time_functions.return_datetime(tt[1],setting="vs")
                            ref_weekday = weekdays.index(tt[2].lower())
                            tweet_weekday = date.weekday()
                            if tweet_weekday < ref_weekday:
                                dif=ref_weekday - tweet_weekday
                            else:
                                dif=ref_weekday + (7-tweet_weekday)
                            ref_date = date + datetime.timedelta(days=dif) 
                            tt.append(str(ref_date))
                        else:
                            tt.append(re.sub("\"","",kv[1]))
                window["features"].append(tt)
#     windows.extend([{"features":t["text"],"label":str(i+args.window) + " " + window["label"],"meta":window["meta"]} for t in ordered_tweets[i:i+args.window]])
    
    i+=args.step
    windows.append(window)

if not os.path.exists("/".join(args.o.split("/")[:-1])):
    os.system("mkdir " + "/".join(args.o.split("/")[:-1]))
outfile = codecs.open(args.o + "_" + str(args.window) + "_" + str(args.step) + ".txt","w","utf-8")
P = re.compile(r"P(\d+|X)(WE|W|M|Y|D|H)")
d = re.compile(r"\d{4}-\d{2}(-\d{2})?(TEV)?")
dw = re.compile(r"\d{4}-w\d+")
for w in windows:
    for f in w["features"]:
        if P.search(f[3]) or d.search(f[3]):
            outfile.write(w["label"] + "\t" + "\t".join(f) + "\n")
