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
outfile = codecs.open(args.o,"a","utf-8")

outfile.write("#user_id\t#tweet_id\t#created\t#reply_to_tweet_id\t#retweet_to_tweet_id\t#user_name\t#user_follower_count\t#user_location\t#tweet_location\t#hashtags\t#tweet\n")

for line in infile.readlines():
    decoded = json.loads(line)
    fields = [decoded["user"]["id"],decoded["id"],decoded["created_at"]]
    if decoded["in_reply_to_status_id"]:
        fields.append(decoded["in_reply_to_status_id"])
    else:
        fields.append("null")
    if "retweet_status" in decoded:
        fields.append(decoded["retweet_status"]["id"])
    else:
        fields.append("null")
    userfields = decoded["user"]
    fields.extend([userfields["screen_name"],userfields["followers_count"],userfields["location"]])
    if decoded["place"]:
        fields.append(decoded["place"]["name"])
    else:
        fields.append("null")
    fields.append(",".join(["#" + x["text"] for x in decoded["entities"]["hashtags"]]))
    fields.append(decoded["text"])
    outfile.write("\t".join([unicode(x) for x in fields]) + "\n")

infile.close()
outfile.close() 
