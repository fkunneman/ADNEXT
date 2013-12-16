#! /usr/bin/env python

import argparse
import codecs
from collections import defaultdict

parser = argparse.ArgumentParser(description = "Program that can be used to change or make additions to any file with (possibly column-based) lines with a consistent format")
parser.add_argument('-i', action = 'store', required = True, help = "The input file.")  
parser.add_argument('-o', action = 'store', required = True, help = "The output directory.")
parser.add_argument('-h', action = 'store', required = True, help = "The heideltime directory.")
parser.add_argument('-d', action = 'store', type = int, required = True, help = "Specify the column with a date.")
# parser.add_argument('-a', action = 'store', required = False, choices = ["add","replace","delete","delete_filematch","extract","add_time","add_id","filter"], help = "Choose the action to perform.")
# parser.add_argument('-s', action = 'store', required = False, help = "give a string as argument for add, replace, delete or filter")
# parser.add_argument('-c', action = 'store', required = False, type=int, help = "give the column as argument for add, replace or delete (add is done before the column, no column means behind the last one, no column for replace means every column will be matches).")
# parser.add_argument('--extract', action = 'store', required = False, nargs='+', help = "[EXTRACT] specify the number of lines to extract")
# parser.add_argument('--replace', action = 'store', required = False, nargs='+', help = "[REPLACE] specify the strings to match for replacement.")
# parser.add_argument('--filematch', action = 'store', required = False, nargs='+', help = "[DELETE_FILEMATCH] give respectively the file and the column within the file to match")
# parser.add_argument('--excel', action = 'store_true', help = "Output lines in excel format")

args = parser.parse_args()

infile = codecs.open(args.i,"r","utf-8")
date_tweets = defaultdict(list)
date_tweetfiles = {}
outdir_date = args.o + "dates/"
#make a date - tweet dictionary
for line in infile.readlines():
    tokens = line.strip().split("\t")
    date_tweets[tokens[args.d]].append(line)

for date in date_tweets.keys():
    dateout = open(outdir_date + date,"w")
    date_file[date] = dateout
    for tweet in date_tweets[date]
        dateout.write(tweet)
    dateout.close()

outdir_tags = args.o + "dates_tagged/"
os.chdir(args.h)
for date in date_file.keys():
    tagged_out = outdir_tags + date)
    os.system("java -jar de.unihd.dbs.heideltime.standalone.jar " + date_file[date] + " -l DUTCH -t NEWS -dct " + date + " > " + tagged_out)

