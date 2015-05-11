#!/usr/bin/env 

import sys
import json
import twitter_devs3
import twython

passwordfile = open(sys.argv[1],encoding="utf-8")
outfile = sys.argv[2]
infiles = sys.argv[3:]

passwords = passwordfile.read().split("\n")
passwordfile.close()
print(passwords)
api = twython.Twython(passwords[0],passwords[1],passwords[2],passwords[3])
out = open(outfile,"a",encoding="utf-8")

for infile in infiles:
    print(infile)
    idfile = open(infile,encoding="utf-8")
    jt = json.load(idfile)
    idfile.close()
    print(jt['tweetID'])
#    try:
    tweet = twitter_devs3.return_tweet(api,jt['tweetID'])
    out.write("\t".join(tweet[:2] + [str(tweet[2].date())] + [str(tweet[2].time())] + [tweet[3]]) + "\n")
 #   except:
 #       continue
out.close()
