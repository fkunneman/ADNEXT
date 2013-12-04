#!/usr/bin/env python

import codecs
import argparse
import gen_functions

"""
Program to put tweet metadata in the right order for tweets_2_features.py
"""
parser = argparse.ArgumentParser(description = "Program to put tweet metadata in the right order for \'tweets_2_features.py\'")
parser.add_argument('-i', action = 'store', required = True, help = "the input file")  
parser.add_argument('-o', action = 'store', required = True, help = "the output file")
parser.add_argument('--header', action = 'store_true', default = "False", help = "choose to ignore the first line of the input-file")
parser.add_argument('--text', action = 'store', type=int, required = True, help = "give the field on a line that contains the text (starting with 0 (the third column would be given by '2'). If the lines only contain text, give '0'.")
parser.add_argument('--user', action = 'store', type=int, required = False, help = "if one of the fields contain a username, specify its column.")
parser.add_argument('--date', action = 'store', type=int, required = False, help = "if one of the fields contain a date, specify its column.")
parser.add_argument('--time', action = 'store', type=int, required = False, help = "if one of the fields contain a time, specify its column.")
parser.add_argument('--id', action = 'store', type=int, required = False, help = "if one of the fields contain a tweetid, specify its column.")
parser.add_argument('--label', action = 'store', type=int, required = False, help = "if one of the fields contain a label / score of the tweet, specify its column.")
parser.add_argument('--man', action = 'store', required = False, help = "specify a label that applies to all tweets")

args = parser.parse_args() 
infile = codecs.open(args.i,"r","utf-8")
outfile = codecs.open(args.o,"w","utf-8")
column_sequence = [args.label,args.id,args.user,args.date,args.time,args.text]

if args.i[-3:] == "xls": 
    tweets = gen_functions.excel2lines(args.i,[0],date=args.date)[0]
else:
    tweets = infile.readlines()
#print tweets

if args.header:
    tweets.pop(0)
for line in tweets:
    if not args.i[-3:] == "xls":
	tokens = line.strip().split("\t")
    else:
        tokens = line
    outfields = []
    if args.man:
        outfields.append(args.man)
        column_sequence = column_sequence[1:]
    for column in column_sequence:
        if column != None:
            if tokens[column] == "":
                tokens[column] = "-"
            outfields.append(tokens[column])
        else:
            outfields.append("-")
    outfile.write("\t".join(outfields) + "\n")

infile.close()
outfile.close()
