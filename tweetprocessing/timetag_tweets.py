#! /usr/bin/env python

import argparse
import codecs
from collections import defaultdict
import os

parser = argparse.ArgumentParser(description = "Program that can be used to change or make additions to any file with (possibly column-based) lines with a consistent format")
parser.add_argument('-i', action = 'store', nargs = '+', required = True, help = "The input files.")  
parser.add_argument('-o', action = 'store', required = True, help = "The output directory.")
parser.add_argument('-w', action = 'store', required = True, help = "The heideltime directory.")
parser.add_argument('-d', action = 'store', type = int, required = True, help = "Specify the column with a date.")
parser.add_argument('--depth', action = 'store', type = int, default = 2, help = "Specify the depth of file characterizations; [DEFAULT] = 2)")
parser.add_argument('--header', action = 'store', default = 2, help = "Specify if the infiles contain a header")

args = parser.parse_args()

date_tweets = defaultdict(list)
date_file = {}
outdir_date = args.o + "dates/"
outdir_meta = args.o + "dates_meta/"
if not os.path.exists(outdir_date):
    d = args.depth * -1
    while d <= -1: 
        if not os.path.exists("/".join(outdir_date.split("/")[:d])):
            os.system("mkdir " + "/".join(outdir_date.split("/")[:d]))
        d+=1
    os.system("mkdir " + outdir_meta)
for i in args.i:
    infile = codecs.open(i,"r","utf-8")
    #make a date - tweet dictionary
    if args.header:
        lines = infile.readlines()[1:]
    else:
        lines = infile.readlines()
    for line in lines:
        try:
            tokens = line.strip().split("\t")
            date_tweets[tokens[args.d]].append(line)
        except IndexError:
            continue

for date in date_tweets.keys():
    dateout_string = outdir_date + date + ".txt"
    metaout_string = outdir_meta + date + ".txt"
    dateout = codecs.open(dateout_string,"w","utf-8")
    metaout = codecs.open(metaout_string,"w","utf-8")
    date_file[date] = dateout_string
    for tweet in date_tweets[date]:
        tokens = tweet.split("\t")
        dateout.write(tokens[-1])
        metaout.write(tweet)
    dateout.close()
    metaout.close()

outdir_tags = args.o + "dates_tagged/"
os.system("mkdir " + outdir_tags)
os.chdir(args.w)
for date in date_file.keys():
    print date
    tagged_out = outdir_tags + date + ".txt"
    os.system("java -jar de.unihd.dbs.heideltime.standalone.jar " + date_file[date] + " -l DUTCH -t NEWS -dct " + date + " > " + tagged_out)

