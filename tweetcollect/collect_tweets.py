#! /usr/bin/env python

import twython
import twitter_devs
import sys
import re
import codecs

eventfile = codecs.open(sys.argv[1],"r","utf-8")
passwordfile = codecs.open(sys.argv[2],"r","utf-8")
idfile = open(sys.argv[3],"r")
outfile = codecs.open(sys.argv[4],"a","utf-8")
language = sys.argv[5]

passwords = passwordfile.read().split("\t")
passwordfile.close()
api = twython.Twython(passwords[0],passwords[1],passwords[2],passwords[3])

events = []
ids = []
tweets = []

for eventinfo in eventfile.readlines():
    tokens = eventinfo.strip().split("|")
    event = tokens[0].strip()
    events.append(event)    
eventfile.close()

for tweetid in idfile:
    ids.append(int(tweetid.strip()))    
idfile.close()

# Collect tweets
for event in events:
    tweets += twitter_devs.extract_tweets(event,api,language)

# Process tweets
for tweetinfo in tweets:
    tweetid = tweetinfo[0]
    if not tweetid in ids:
        ids.append(tweetid)
        tweet = tweetinfo[1]
        outfile.write(tweet)

id_outfile = open(sys.argv[2],"w")
for tweetid in ids:
    id_outfile.write(str(tweetid) + "\n")
    
