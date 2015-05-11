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
    print(len(ls))
    fc = pynlpl.clients.frogclient.FrogClient('localhost',sys.argv[2])    

    out = []
    for l in ls:
        lemmas = []
        tokens = []
        poss = []
        frs = fc.process(l[1])
        for t in frs:
            if t[0]:
                tokens.append(t[0])
                lemmas.append(t[1])
                poss.append(t[3])
        o.put([l[0]," ".join(tokens)," ".join(lemmas)," ".join(poss)])

    print("chunk",i,"done")

csv.field_size_limit(sys.maxsize)
filename = sys.argv[1][:-4]

lines = []

print("reading in file")
#dataset = utils.load_data(filename=sys[1], random_state=None, max_n=None)

with open(sys.argv[1], 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        lines.append(row)

#texts = dataset["texts"]
texts = [i[-1] for i in lines][:20]
indices = range(len(texts))

print("Processing lines.")
q = multiprocessing.Queue()
frogged = []
chunks = gen_functions.make_chunks(zip(indices,texts))
print(len(chunks))

for i in range(len(chunks)):
    p = multiprocessing.Process(target=frogger,args=[chunks[i],q,i])
    p.start()

total = len(lines)
while True:
    l = q.get()
    frogged.append(l)
    print(len(frogged),"of",total)
    if len(frogged) == len(indices):
        break

print("writing to files")
frogged_sorted = sorted(frogged,key = lambda k : k[0])
meta = []
for index in [i[0] for i in frogged_sorted]:
    meta.append([dataset['user_id'][index],dataset['age'][index],dataset['gender'][index],
        dataset['loc_country'][index],dataset['loc_region'][index],dataset['loc_city'][index],
        dataset['education'][index],dataset['pers_big5'][index],dataset['pers_mbti'][index]])

with open(filename + "_tokenized.csv", 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for i,tokens in enumerate(frogged_sorted):
        writer.writerow(meta[i] + [tokens[1]])

with open(filename + "_lemmatized.csv", 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for i,tokens in enumerate(frogged_sorted):
        writer.writerow(meta[i] + [tokens[2]])

with open(filename + "_postags.csv", 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for i,tokens in enumerate(frogged_sorted):
        writer.writerow(meta[i] + [tokens[3]])
