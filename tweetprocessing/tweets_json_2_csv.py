#!/usr/bin/env python

import argparse
import codecs
import json
import re

"""
Script to extract information from a json tweet file and write to csv format
"""
parser = argparse.ArgumentParser(description = "Script to extract information from a json tweet file and write to csv format")
parser.add_argument('-i', action = 'store', required = True, help = "the input file")  
parser.add_argument('-o', action = 'store', required = True, help = "the output file")  
args = parser.parse_args() 

infile = codecs.open(args.i,"r","utf-8")
try:
    outfilein = codecs.open(args.o,"r","utf-8")
    new = False
    outfilein.close()
except:
    new = True
outfile = codecs.open(args.o,"a","utf-8")

if new:
    outfile.write("#user_id\t#tweet_id\t#date\t#time\t#reply_to_tweet_id\t#replied_tweet_url\t#retweet_to_tweet_id\t#retweeted_tweet_url\t#user_name\t#user_follower_count\t#user_location\t#tweet_location\t#hashtags\t#tweet\n")

month = {"Jan":"01", "Feb":"02", "Mar":"03", "Apr":"04", "May":"05", "Jun":"06", "Jul":"07", "Aug":"08", "Sep":"09", "Oct":"10", "Nov":"11", "Dec":"12"}
date_time = re.compile(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d+) (\d{2}:\d{2}:\d{2}) \+\d+ (\d{4})")

for line in infile.readlines():
    decoded = json.loads(line)
    if "twinl_lang" in decoded and decoded["twinl_lang"] != "dutch":
        continue
    fields = [decoded["user"]["id"],decoded["id"]]
    dtsearch = date_time.search(decoded["created_at"]).groups()
    fields.extend([dtsearch[1] + "-" + month[dtsearch[0]] + "-" + dtsearch[3],dtsearch[2]])
    if decoded["in_reply_to_status_id"]:
        tid = decoded["in_reply_to_status_id_str"]
        if len(decoded["entities"]["user_mentions"]) > 0:
            user = decoded["entities"]["user_mentions"][0]["screen_name"]
            fields.extend([tid,"https://twitter.com/" + user + "/status/" + tid])
        else:
            fields.extend([tid,"null"])
    else:
        fields.extend(["null","null"])
    if "retweeted_status" in decoded:
        #print decoded["retweeted_status"]
        #print decoded["retweeted_status"]["id"]
        tid = decoded["retweeted_status"]["id_str"]
        user = decoded["retweeted_status"]["user"]["screen_name"]
        fields.extend([tid,"https://twitter.com/" + user + "/status/" + tid])
        #print fields
    else:
        fields.extend(["null","null"])
    userfields = decoded["user"]
    fields.extend([userfields["screen_name"],userfields["followers_count"],userfields["location"]])
    if fields[-1] != None:
        fields[-1] = re.sub("\n","",fields[-1])
    if decoded["place"]:
        fields.append(decoded["place"]["name"])
    else:
        fields.append("null")
    fields.append(",".join(["#" + x["text"] for x in decoded["entities"]["hashtags"]]))
    fields.append(decoded["text"].replace("\n"," "))
    fields_write = "\t".join([unicode(x).replace("\n"," ") for x in fields]) + "\n"
    outfile.write(fields_write)

infile.close()
outfile.close() 
