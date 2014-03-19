#! /usr/bin/env python

import twython
import twitter_devs
import sys
import re
import codecs

user = sys.argv[1]
outfile = codecs.open(sys.argv[2],"a","utf-8")

api = twython.Twython("UgWAr6AsfnpnkNz6Lsvgjg","jxEvISOAPlhlWmCWXDrF2jL3ZNo62IDu5FMyYrM","101817731-dF9m4wpJVUjh41nE85Qv7lWQcOBgqgw8lFB9ZK60","PR8dR3IXBDA7YagdTIudDuPXZvDBC1xC0tRNlbYTFfs")

tweets = []

# Collect tweets
tweets = twitter_devs.collect_usertweets(api,user)

quit()
# Process tweets
# for tweetinfo in tweets:
#     tweetid = tweetinfo[0]
#     if not tweetid in ids:
#         ids.append(tweetid)
#         tweet = tweetinfo[1]
#         outfile.write(tweet)

# id_outfile = open(sys.argv[2],"w")
# for tweetid in ids:
#     id_outfile.write(str(tweetid) + "\n")
    
