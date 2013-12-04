#!/usr/bin/env python

import argparse
import codecs
import time_functions
from collections import defaultdict
import datetime

"""
Script to put metadata in the right order for tweets_2_features.
Presumes file for 1 event
"""
parser = argparse.ArgumentParser(description = "Script to put metadata in the right order for tweets_2_features.")
parser.add_argument('-i', action = 'store', required = True, help = "the input file")  
parser.add_argument('-o', action = 'store', required = True, help = "the output file")
parser.add_argument('-d', action = 'store', default = "\t", help = "the delimiter, given that the lines contain fields (default is \'\\t\')") 
parser.add_argument('--header', action = 'store_true', default = "False", help = "choose to ignore the first line of the input-file")
parser.add_argument('--text', action = 'store', type=int, required = False, help = "give the field on a line that contains the text (starting with 0 (the third column would be given by '2'). If the lines only contain text, give '0'.")
parser.add_argument('--user', action = 'store', type=int, required = False, help = "if one of the fields contain a username, specify its column.")
parser.add_argument('--date', action = 'store', type=int, required = False, help = "if one of the fields contain a date, specify its column.")
parser.add_argument('--time', action = 'store', type=int, required = False, help = "if one of the fields contain a time, specify its column.")
parser.add_argument('--id', action = 'store', type=int, required = False, help = "if one of the fields contain a tweetid, specify its column.")
parser.add_argument('--label', action = 'store', type=int, required = False, help = "if one of the fields contain a label / score of the tweet, specify its column.")
parser.add_argument('--events', action = 'store', required = False, help = "if the event of a tweet should be given as a label, give a file containing the events")
parser.add_argument('--man', action = 'store', required = False, help = "specify a label that applies to all tweets")
parser.add_argument('--txtdelim', action = 'store_true', help = "specify if the spaces between words in the tweet text are the same as the basic delimiter")

args = parser.parse_args() 

infile = codecs.open(args.i,"utf-8","r")
outfile = codecs.open(args.o,"utf-8","r")

if args.i[-3:] == "xls": 
    pre_tweets = gen_functions.excel2lines(args.i,[0],args.header,date=datecolumn)[0]
else:
    lines = infile.readlines()
    if args.header():
        lines.pop()
    pre_tweets = [line.strip().split(args.d) for line in lines]
    infile.close()
tweets = []
for tweet in pre_tweets:
    if tweet != "":
        tweets.append(tweet)

column_sequence = [args.label,args.id,args.user,args.date,args.time,args.text]

#if needed, generate a list of event hashtags
if args.events:
    eventfile = codecs.open(args.events,"r","utf-8")
    events = []
    for line in eventfile:
        tokens = line.split("\t")
        events.append(tokens[0])
    eventfile.close()

for tweet in tweets:
    tokens = tweet.strip().split(args.delimiter)
    if args.txtdelim:
        tokens[column_sequence[-1]] = " ".join(tokens[column_sequence[-1]:])
        tokens = tokens[:column_sequence[-1]+1]
    outfields = []
    for column in column_sequence:
        if column:
            try:
                outfields.append(tokens[column])
            except IndexError:
                continue
    outstring = args.delimiter.join(outfields) + "\n"
    outfile.write(outstring)

outfile.close()
