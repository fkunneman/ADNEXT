#!/usr/bin/env python

import pynlpl.clients.frogclient
import sys
import csv
import codecs
import re
import argparse
import multiprocessing
import gzip
import gen_functions
import utils

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
      
#Function to tokenize the inputfile
def frogger(t,o,i):
    fc = pynlpl.clients.frogclient.FrogClient('localhost',args.p,returnall = True)    
        
    for output in fc.process(t):
        print(output)
        #words.append(word)    
        #outstring = outstring + "\n"
        #o.put(outstring)
    
    print "Chunk " + str(i) + " done."

filename = sys.argv[1][:-4]

lines = []
metalist = []
tokenslist = []
stemslist = []
poslist = []

print("reading in file")
dataset = load_data(filename=sys[1], random_state=None, max_n=None)

texts = dataset["texts"]
indices = range(len(texts))

fc = pynlpl.clients.frogclient.FrogClient('localhost','15243',returnall = True)    
    
for output in fc.process(texts[:10]):
    print(output)
quit()

print "Processing lines."
q = multiprocessing.Queue()
frogged = []
chunks = gen_functions.make_chunks(zip(indices,texts))

for i in range(len(tweets_chunks)):
    p = multiprocessing.Process(target=frogger,args=[tweets_chunks[i],q,i])
    p.start()

while True:
    l = q.get()
    frogged.append(l)
    print(len(frogged))
    if len(frogged) == len(indices):
        break

frogged_sorted = sorted(frogged,key = lambda k : k[0])
meta = []
for index in [i[0] for i in frogged_sorted]:
    meta.append([dataset['user_id'][index],dataset['age'][index],dataset['gender'][index],
        dataset['loc_country'][index],dataset['loc_region'][index],dataset['loc_city'][index],
        dataset['education'][index],dataset['pers_big5'][index],dataset['pers_mbti'][index]])

with open(filename + "_tokenized.csv", 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for i,tokens in enumerate(frogged_sorted):
        writer.writerow(meta[i] + [" ".join(tokens[1])])

with open(filename + "_lemmatized.csv", 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for i,tokens in enumerate(frogged_sorted):
        writer.writerow(meta[i] + [" ".join(tokens[2])])

with open(filename + "_postags.csv", 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for i,tokens in enumerate(frogged_sorted):
        writer.writerow(meta[i] + [" ".join(tokens[3])])
