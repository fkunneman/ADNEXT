#!/usr/bin/env 

import sys
import json
import twitter_devs3
import twython

outfile = sys.argv[3]
passwords = sys.argv[2]
infiles = sys.argv[4:]

out = open(outfile,"w",encoding="utf-8")

for infile in infiles:
    idfile = open(infile,encoding="utf-8")
    jt = json.load(idfile)
    idfile.close()
    tweet = twitter_devs3.return_tweet(jt['tweetID'])
    out.write("\t".join(tweet[:2] + [tweet[2].date()] + [tweet[2].time()] + [tweet[3]) + "\n")
out.close()