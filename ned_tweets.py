#!/usr/bin/env python

import argparse
import multiprocessing
import frog_functions
import gen_functions

"""
Script to process a file containing tweets with Frog, and output it with highlighted named entities in a file.
"""
parser = argparse.ArgumentParser(description = "Script to process a file containing tweets with Frog, and output it with highlighted named entities in a file.")
parser.add_argument('-i', action = 'store', required = True, help = "the input file")  
parser.add_argument('-o', action = 'store', required = True, help = "the output file")
parser.add_argument('-d', action = 'store', default = "\t", help = "the delimiter, given that the lines contain fields (default is \'\\t\')")
parser.add_argument('--header', action = 'store_true', default = "False", help = "choose to ignore the first line of the input-file")
parser.add_argument('--text', action = 'store', type=int, required = False, help = "give the field on a line that contains the text (starting with 0 (the third column would be given by '2'). If the lines only contain text, give '0'.")
parser.add_argument('--parralel', action = 'store_true', default = False, help = "choose if the file should be processed in parralel (recommended for big files).")

args = parser.parse_args()

outfile = open(args.o,"w",encoding = "utf-8")

infile = open(args.i,encoding = "utf-8")
lines = infile.readlines()
if args.header:
    lines.pop(0)
pre_tweets = [line.strip().split(args.d) for line in lines]
infile.close()
tweets = []
for tweet in pre_tweets:
    if tweet != "":
        tweets.append(tweet)
      
#Function to tokenize the inputfile
def frogger(t,o,i):
    Fr = frog_functions.Frogger(8)
    for tweet in t:
#        print(tweet)
        entities = Fr.return_entities(tweet[args.text])
        if len(entities) == 0:
            entities = [("x","x")] 
        new_string = args.d.join(tweet + [" | ".join([x[0] for x in entities])]) + "\n"
        print(new_string)
        o.put(new_string)
    print("Chunk " + str(i) + " done.")

print("Processing tweets.")
q = multiprocessing.Queue()
frogged_tweets = []
if args.parralel:
    tweets_chunks = gen_functions.make_chunks(tweets)
else:
    tweets_chunks = [tweets]

for i in range(len(tweets_chunks)):
    p = multiprocessing.Process(target=frogger,args=[tweets_chunks[i],q,i])
    p.start()

while True:
    l = q.get()
    frogged_tweets.append(l)
    outfile.write(l)
    print(len(frogged_tweets))
    if len(frogged_tweets) == len(tweets):
        break

outfile.close()
