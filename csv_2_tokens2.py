#!/usr/bin/env python

import pynlpl.clients.frogclient
import sys
import csv
#import codecs
import re
import multiprocessing
import gen_functions
import utils
      
#Function to tokenize the inputfile
def frogger(ls,o,i):
    fc = pynlpl.clients.frogclient.FrogClient('localhost',sys.argv[2])    
    
    for l in ls:
        ts = fc.process(l)
        lemma
        print(output)
        #words.append(word)    
        #outstring = outstring + "\n"
        #o.put(outstring)
    
    print("Chunk ",i," done.")

csv.field_size_limit(sys.maxsize)
filename = sys.argv[1][:-4]

lines = []
metalist = []
tokenslist = []
stemslist = []
poslist = []

print("reading in file")
#dataset = utils.load_data(filename=sys[1], random_state=None, max_n=None)

with open(sys.argv[1], 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        lines.append(row)

#texts = dataset["texts"]
texts = [i[-1] for i in lines]
indices = range(len(texts))

print("Frogging")
fc = pynlpl.clients.frogclient.FrogClient('localhost',sys.argv[2])    

ts = texts[:2]
lemmas = []
tokens = []
for t in ts:
    frs = fc.process(t)
    for t in frs:
        if t[0]:
            lemmas.append(t[1])
            tokens.append(t[0])
#print(t[0] for t in tokens)
    #print(t[1] for t in tokens)
    #print(t[3] for t in tokens)
# for t in texts[:20]:    
#     for output in fc.process(t):
#         print(output)
print(zip(tokens,lemmas))
quit()

print("Processing lines.")
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
