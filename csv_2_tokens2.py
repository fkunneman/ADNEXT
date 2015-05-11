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
