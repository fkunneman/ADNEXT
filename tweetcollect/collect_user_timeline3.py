#! /usr/bin/env python

import twython
import twitter_devs3
import sys
import re
import time

userfile = open(sys.argv[1],"r",encoding = "utf-8")
passwordfile = open(sys.argv[2],"r",encoding = "utf-8")
outdir = sys.argv[3]

passwords = passwordfile.read().split("\n")
passwordfile.close()
api = twython.Twython(passwords[0],passwords[1],passwords[2],passwords[3])

users = [x.strip() for x in userfile.read().split("\n")]
userfile.close()

for user in users:
    print(user)
    outfile = open(outdir + user + ".txt","w",encoding = "utf-8")
    # Collect tweets
    tweets = twitter_devs3.collect_usertweets(api,user)
    while not tweets[0]:
        time.sleep(1800)
        api = twython.Twython(passwords[0],passwords[1],passwords[2],passwords[3])
        tweets = twitter_devs3.collect_usertweets(api,user)
    outfile.write("\n".join(tweets))
    outfile.close()
