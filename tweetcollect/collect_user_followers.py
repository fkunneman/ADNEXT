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
    followers = []
    outfile = open(outdir + user + "_followers.txt","w",encoding = "utf-8")
    # Collect followers
    next_cursor=-1
    c = 0
    while(next_cursor):
        try:
            newfollowers = api.get_followers_list(screen_name=user,count=200,cursor=next_cursor)
            followers.extend([x["screen_name"] for x in newfollowers["users"]])
            c += len(followers)
            outfile.write("\n".join(followers) + "\n")
            followers = []            
            next_cursor = newfollowers["next_cursor"]
            time.sleep(45)
            print(c,next_cursor)
        except:
            print("limit exceeded")
            time.sleep(3600)
            api = twython.Twython(passwords[0],passwords[1],passwords[2],passwords[3])   
    outfile.close()
