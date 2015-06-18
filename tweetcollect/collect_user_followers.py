#! /usr/bin/env python

import twython
import twitter_devs3
import sys
import re
import time

userfile = open(sys.argv[1],"r",encoding = "utf-8")
passwordfile = open(sys.argv[2],"r",encoding = "utf-8")
outdir = sys.argv[3]
nc = sys.argv[4]

passwords = passwordfile.read().split("\n")
passwordfile.close()
api = twython.Twython(passwords[0],passwords[1],passwords[2],passwords[3])

users = [x.strip() for x in userfile.read().split("\n")]
userfile.close()

for i,user in enumerate(users):
    if len(user.strip()) > 0:
        print(user)
        followers = []
        # Collect followers
        if nc != '-' and i == 0:
            next_cursor = nc
            outfile = open(outdir + user + "_followers.txt","a",encoding = "utf-8")
        else:
            next_cursor = '-1'
            outfile = open(outdir + user + "_followers.txt","w",encoding = "utf-8")
        c = 0
        while(next_cursor):
            try:
                newfollowers = api.get_followers_ids(screen_name=user,count=5000,cursor=next_cursor)
                followers.extend(newfollowers["ids"])
                c += len(followers)
                outfile.write("\n".join([str(x) for x in followers]) + "\n")
                outfile.close()
                followers = []            
                next_cursor = newfollowers["next_cursor"]
                print(c,next_cursor)
                time.sleep(45)
                outfile = open(outdir + user + "_followers.txt","a",encoding = "utf-8")
            except:
                print("limit exceeded")
                time.sleep(1800)
                api = twython.Twython(passwords[0],passwords[1],passwords[2],passwords[3])   
        outfile.close()
