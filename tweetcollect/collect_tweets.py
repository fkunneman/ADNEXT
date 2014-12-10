#! /usr/bin/env python

import twython
import twitter_devs
import sys
import re
import codecs

eventfile = codecs.open(sys.argv[1],"r","utf-8")
idfile = open(sys.argv[2],"r")
outfile = codecs.open(sys.argv[3],"a","utf-8")
language = sys.argv[4]

api = twython.Twython("UgWAr6AsfnpnkNz6Lsvgjg","jxEvISOAPlhlWmCWXDrF2jL3ZNo62IDu5FMyYrM","101817731-dF9m4wpJVUjh41nE85Qv7lWQcOBgqgw8lFB9ZK60","PR8dR3IXBDA7YagdTIudDuPXZvDBC1xC0tRNlbYTFfs")

events = []
ids = []
tweets = []

for eventinfo in eventfile:
    tokens = eventinfo.split("|")
    event = tokens[0].strip()
    events.append(event)    

for tweetid in idfile:
    ids.append(int(tweetid.strip()))    

# Collect tweets
print "event",event,"api",api,"lang",language
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
    
