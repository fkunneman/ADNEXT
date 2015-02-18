#! /usr/bin/env python

import twython
import twitter_devs
import sys
import re
import codecs

userfile = codecs.open(sys.argv[1],"r","utf-8")
passwordfile = codecs.open(sys.argv[2],"r","utf-8")
outdir = sys.argv[3]

passwords = passwordfile.read().split("\t")
passwordfile.close()
api = twython.Twython(passwords[0],passwords[1],passwords[2],passwords[3])

users = [x.strip() for x in userfile.read().split("\n")]
userfile.close()

for user in users:
    outfile = codecs.open(outdir + user + ".txt","w","utf-8")
    # Collect tweets
    tweets = twitter_devs.collect_usertweets(api,user)
    outfile.write("\n".join(tweets))
    outfile.close()
