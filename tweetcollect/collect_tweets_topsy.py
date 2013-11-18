#! /usr/bin/env python

import sys
import codecs
import twitter_devs
import otter
import re

searchterm = sys.argv[1]

if len(tweetlist) == 0:
    userfile = codecs.open(sys.argv[1],"w","utf-8")
    for u in users[completed-1:]:
        userfile.write(u + "\n")
break
else:   
    outfile = codecs.open(userdirectory + user + ".txt","w","utf-8")
    for tweet in tweetlist:
        tweetstring = "\t".join(tweet)
        outfile.write(tweetstring + "\n")
    completed += 1  
