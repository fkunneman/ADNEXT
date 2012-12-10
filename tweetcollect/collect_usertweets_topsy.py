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

completed = 0
content = 0
for user in users:
        print user
        tweetlist = twitter_devs.collect_user_topsy(user,kw)
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

