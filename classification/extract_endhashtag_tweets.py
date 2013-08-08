#! /usr/bin/env python

import argparse
import codecs
import re

parser = argparse.ArgumentParser(description = "")
parser.add_argument('-i', action = 'store', required = True, help = "the input file")  
parser.add_argument('-c', action = 'store', required = True, help = "the column in the input file with the tweet text")
parser.add_argument('-h', action = 'store', required = True, nargs='+', help = "the hashtags for which tweets are checked")
parser.add_argument('-o', action = 'store', required = True, help = "the output file")

infile = codecs.open(args.i,"r","utf-8")
inlines = infile.readlines()
infile.close()
outfile = codecs.open(args.o,"w","utf-8")

def has_endhashtag(sequence):
    sequence = text.split(" ")
    for h in args.h:
        if sequence[-1] == ".":
            return False
        try:
            if re.match(sequence[-1],h,re.IGNORECASE):
                return True
        except:
            return False             
    if re.search("http://",sequence[-1]) or re.search("#",sequence[-1]):
        has_endhashtag(sequence[:-1])
    else:
        return False

for line in inlines:
    tokens = line.split("\t")
    text = tokens[args.c]
    for hashtag in args.h:
        if re.search(hashtag,text):
            wordsequence = text.split(" ")
            if has_endhashtag(wordsequence):
                outfile.write(line)
                continue
 
outfile.close()