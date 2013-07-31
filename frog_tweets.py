#!/usr/bin/env python

import pynlpl.clients.frogclient
import codecs
import sys
import re
import argparse
import multiprocessing
import os
from random import randint
import gen_functions

"""
Script to process a file containing tweets with Frog en output it in a file.
It relies on Frog set up on a server beforehand.
"""
parser = argparse.ArgumentParser(description = "Program to process a file containing tweets with Frog en write output to a file. It relies on Frog being set up on a server beforehand.")
parser.add_argument('-i', action = 'store', required = True, help = "the input file")  
parser.add_argument('-p', action = 'store', required = True, help = "specify the port of the Frog server")
parser.add_argument('-w', action = 'store', required = True, help = "the output file")
parser.add_argument('-d', action = 'store', default = "\t", help = "the delimiter, given that the lines contain fields (default is \'\\t\')") 
parser.add_argument('--header', action = 'store_true', default = "False", help = "choose to ignore the first line of the input-file")
parser.add_argument('--text', action = 'store', required = False, help = "give the field on a line that contains the text (starting with 0 (the third column would be given by '2'). If the lines only contain text, give '0'.")
parser.add_argument('--user', action = 'store', required = False, help = "if one of the fields contain a username, specify its column.")
parser.add_argument('--date', action = 'store', required = False, help = "if one of the fields contain a date, specify its column.")
parser.add_argument('--time', action = 'store', required = False, help = "if one of the fields contain a time, specify its column.")
parser.add_argument('--id', action = 'store', required = False, help = "if one of the fields contain a tweetid, specify its column.")
parser.add_argument('--label', action = 'store', required = False, help = "if one of the fields contain a label / score of the tweet, specify its column.")
parser.add_argument('--punct', action = 'store_true', default = False, help = "choose if punctuation should be removed from the output")
parser.add_argument('--parralel', action = 'store_true', default = False, help = "choose if the file should be processed in parralel (recommended for big files).")
parser.add_argument('--events', action = 'store', required = False, help = "if the event of a tweet should be given as a label, give a file containing the events")
parser.add_argument('--man', action = 'store', required = False, help = "specify a label that applies to all tweets")

args = parser.parse_args() 
infile = codecs.open(args.i,"r","utf-8")
outfile = codecs.open(args.w,"w","utf-8")
port = int(args.p)
delimiter = args.d
textcolumn = args.text
usercolumn = args.user
datecolumn = args.date
timecolumn = args.time
idcolumn = args.id
labelcolumn = args.label
parralel = args.parralel
eventlist = args.events
punct = args.punct
man_class = args.man
 
if args.header:
    pre_tweets = infile.readlines()[1:]
else:
    pre_tweets = infile.readlines()
infile.close()
tweets = []
for tweet in pre_tweets:
    if tweet != "":
        tweets.append(tweet.strip())

column_sequence = [labelcolumn,idcolumn,usercolumn,datecolumn,timecolumn,textcolumn]

#if needed, generate a list of event hashtags
if eventlist:
    eventfile = codecs.open(args.eventlist,"r","utf-8")
    events = []
    for line in eventfile:
        tokens = line.split("\t")
        events.append(tokens[0])
    eventfile.close()
      
#Function to tokenize the inputfile
def frogger(t,o,i):
    fc = pynlpl.clients.frogclient.FrogClient('localhost',port)
    for tweet in t:
        tokens = tweet.split(delimiter)
        outfields = []
        for column in column_sequence:
            if column:
                outfields.append(tokens[int(column)])    

        text = outfields[-1]
        if man_class:
            outstring = man_class
        else:
            outstring = ""
        words = []        

        for word,lemma,morph,pos in fc.process(text):
            if word == None or (punct and pos == "LET()"):
                continue
            else:    
                if eventlist:
                    for hashtag in events:
                        if re.search(word,hashtag):
                            outstring = word
                            break
                words.append(word)    
    
        outfields[-1] = " ".join(words)
        for field in outfields:
            if outstring == "":
                outstring = field
            else:
                outstring = outstring + "\t" + field

        outstring = outstring + "\n"
        o.put(outstring)
    
    print "Chunk " + str(i) + " done."

print "Processing tweets."
q = multiprocessing.Queue()
frogged_tweets = []
if parralel:
    chunk_size = int(len(tweets) / 16)
    tweets_chunks = gen_functions.make_chunks(tweets,chunk_size)
else:
    tweets_chunks = [tweets]
    
for i in range(len(tweets_chunks)):
    p = multiprocessing.Process(target=frogger,args=[tweets_chunks[i],q,i])
    p.start()
while len(frogged_tweets) < len(tweets):
    l = q.get()
    frogged_tweets.append(l)
    outfile.write(l)
    print len(tweets)
    print len(frogged_tweets)

outfile.close()

