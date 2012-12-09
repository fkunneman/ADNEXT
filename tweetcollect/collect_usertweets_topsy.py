#! /usr/bin/env python

import sys
import codecs
import twitter_devs
import otter
import re

userfile = codecs.open(sys.argv[1],"r","utf-8")
userdirectory = sys.argv[2]

users = []
kw = otter.loadrc()

for user in userfile:
        user = re.sub("\n","",user)
        users.append(user)

content = 0
for user in users:
        print user
        tweetlist = twitter_devs.collect_user_topsy(user,kw)
	print len(tweetlist)
        if len(tweetlist) == 0:
                continue
                userfile = codecs.open(sys.argv[1],"w","utf-8")
                for u in users[completed:]:
                        userfile.write(u + "\n")
        else:   
                outfile = codecs.open(userdirectory + user + ".txt","w","utf-8")
                for tweet in tweetlist:
                        tweetstring = "\t".join(tweet)
                        outfile.write(tweetstring + "\n")
                completed += 1  

