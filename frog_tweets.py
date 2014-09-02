#!/usr/bin/env python

import pynlpl.clients.frogclient
import codecs
import re
import argparse
import multiprocessing
import gzip
import gen_functions

"""
Script to process a file containing tweets with Frog en output it in a file.
It relies on Frog set up on a server beforehand.
"""
parser = argparse.ArgumentParser(description = "Program to process a file containing tweets with Frog en write output to a file. It relies on Frog being set up on a server beforehand.")
parser.add_argument('-i', action = 'store', required = True, help = "the input file")  
parser.add_argument('-p', action = 'store', type=int, required = True, help = "specify the port of the Frog server")
parser.add_argument('-w', action = 'store', required = True, help = "the output file")
parser.add_argument('-d', action = 'store', default = "\t", help = "the delimiter, given that the lines contain fields (default is \'\\t\')")
parser.add_argument('-v', action = 'store_true', help = "set the print output to verbose")
parser.add_argument('--header', action = 'store_true', help = "choose to ignore the first line of the input-file")
parser.add_argument('--text', action = 'store', type=int, required = False, help = "give the field on a line that contains the text (starting with 0 (the third column would be given by '2'). If the lines only contain text, give '0'.")
parser.add_argument('--user', action = 'store', type=int, required = False, help = "if one of the fields contain a username, specify its column.")
parser.add_argument('--date', action = 'store', type=int, required = False, help = "if one of the fields contain a date, specify its column.")
parser.add_argument('--time', action = 'store', type=int, required = False, help = "if one of the fields contain a time, specify its column.")
parser.add_argument('--id', action = 'store', type=int, required = False, help = "if one of the fields contain a tweetid, specify its column.")
parser.add_argument('--label', action = 'store', type=int, required = False, help = "if one of the fields contain a label / score of the tweet, specify its column.")
parser.add_argument('--punct', action = 'store_true', default = False, help = "choose if punctuation should be removed from the output")
parser.add_argument('--parallel', action = 'store_true', default = False, help = "choose if the file should be processed in parallel (recommended for big files).")
parser.add_argument('--events', action = 'store', required = False, help = "if the event of a tweet should be given as a label, give a file containing the events")
parser.add_argument('--man', action = 'store', required = False, help = "specify a label that applies to all tweets")
parser.add_argument('--txtdelim', action = 'store_true', help = "specify if the spaces between words in the tweet text are the same as the basic delimiter")
parser.add_argument('--ne', action = 'store_true', help = "choose to highlight named entities")
parser.add_argument('--pos', action = 'store_true', help = "choose to append a word sequence in pos-tags")

args = parser.parse_args() 
print args.i
outfile = codecs.open(args.w,"w","utf-8")
if args.i[-2:] == "gz":
    infile = gzip.open(args.i,"rb")
    reader = codecs.getreader("utf-8")
    lines = reader( infile )
else:
    infile = codecs.open(args.i,"r","utf-8")

if args.i[-3:] == "xls": 
    pre_tweets = gen_functions.excel2lines(args.i,[0],args.header,date=datecolumn)[0]
else:
    if not args.i[-2:] == "gz":
        lines = infile.readlines()
    if args.header:
        lines.pop(0)
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
      
#Function to tokenize the inputfile
def frogger(t,o,i):
    fc = pynlpl.clients.frogclient.FrogClient('localhost',args.p,returnall = True)
    for tokens in t:
        if args.txtdelim:
            tokens[column_sequence[-1]] = " ".join(tokens[column_sequence[-1]:])
            tokens = tokens[:column_sequence[-1]+1]
        if args.text == 0:
            outfields = [tokens]
        else:
            outfields = []
            for column in column_sequence:
                if column or column == 0:
                    try:
                        outfields.append(tokens[column])
                    except IndexError:
                        continue

        try:
            text = outfields[-1]
        except IndexError:
            continue
        if args.man:
            outstring = args.man
        else:
            outstring = ""
        words = []        
        
        for output in fc.process(text):
            if output[0] == None or (args.punct and output[3] == "LET()"):
                continue
            else:    
                if args.events:
                    for hashtag in events:
                        if re.search(output[0],hashtag):
                            outstring = output[0]
                            break
                if args.ne and output[4] != "O":
                    cat = re.search(r"B-([^_]+)",output[4])
                    word = "[" + cat.groups()[0] + " " + output[0] + "]"
                elif args.pos:
                    word = output[0] + "__" + output[3] 
                else:
                    word = output[0]
                words.append(word)    
    
        outfields[-1] = " ".join(words)
        for field in outfields:
            if outstring == "":
                outstring = field
            else:
                try:
                    outstring = outstring + "\t" + field
                except UnicodeDecodeError:
                    outstring = outstring + "\t" + field.decode("utf-8")

        outstring = outstring + "\n"
        o.put(outstring)
    if args.v:
        print "Chunk " + str(i) + " done."

print "Processing tweets."
q = multiprocessing.Queue()
frogged_tweets = []
if args.parallel:
    tweets_chunks = gen_functions.make_chunks(tweets)
else:
    tweets_chunks = tweets

for i in range(len(tweets_chunks)):
    p = multiprocessing.Process(target=frogger,args=[tweets_chunks[i],q,i])
    p.start()

while True:
    l = q.get()
    frogged_tweets.append(l)
    outfile.write(l)
    if args.v:
        print len(frogged_tweets)
    if len(frogged_tweets) == len(tweets):
        break

outfile.close()
