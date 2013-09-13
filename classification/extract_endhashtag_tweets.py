#! /usr/bin/env python

import argparse
import codecs
import re

parser = argparse.ArgumentParser(description = "")
parser.add_argument('-i', action = 'store', required = True, help = "the input file")  
parser.add_argument('-c', action = 'store', required = True, help = "the column in the input file with the tweet text")
parser.add_argument('-ht', action = 'store', required = True, nargs='+', help = "the hashtags for which tweets are checked")
parser.add_argument('-o', action = 'store', required = True, help = "the output file")
args = parser.parse_args()

infile = codecs.open(args.i,"r","utf-8")
inlines = infile.readlines()
infile.close()
outfile = codecs.open(args.o,"w","utf-8")

def has_endhashtag(sequence,hashtags):
#    print sequence
    if len(sequence) == 0:
       return False
    if sequence[-1] == ".":
#        print "dot-false"
        return False
    for h in hashtags:
        try:
            #print sequence[-1],h,len(sequence[-1].strip()),len(h.strip())
            if re.match(sequence[-1],h,re.IGNORECASE):
#                print "true"
                return True
        except:
#            print "charfalse"
            return False             
    if re.search("URL",sequence[-1]) or re.search("#",sequence[-1]):
#        print "markerproceed"
        has_endhashtag(sequence[:-1])
    else:
#        print "empty stop"
        return False

for line in inlines:
    tokens = line.split("\t")
    text = tokens[int(args.c)]
    for hashtag in args.ht:
        if re.search(hashtag,text):
#            print text
            wordsequence = text.strip().split(" ")
#            print has_endhashtag(wordsequence)
            if has_endhashtag(wordsequence,args.ht):
#                print "yes"
                outfile.write(line)
                continue
 
outfile.close()
