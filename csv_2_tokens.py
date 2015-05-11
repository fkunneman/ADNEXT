#!/usr/bin/env 

import csv
import sys
import frog

fo = frog.FrogOptions(threads=20)
frogger = frog.Frog(fo,"/vol/customopt/uvt-ru/etc/frog/frog-twitter.cfg")
csv.field_size_limit(sys.maxsize)

filename = sys.argv[1][:-4]

lines = []
metalist = []
tokenslist = []
stemslist = []
poslist = []

print("reading in file")
with open(sys.argv[1], 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        lines.append(row)

print("frogging")
l = len(lines)
for i,line in enumerate(lines):
    print("line",i,"of",l)   
    tokens = []
    stems = []
    pos = []
    metalist.append(line[:-1])
    data = frogger.process(line[-1])
    for token in data:
        tokens.append(token["text"])
        pos.append(token["pos"])
        stems.append(token["lemma"])
    tokenslist.append(tokens)
    poslist.append(tokens)
    stemslist.append(tokens)

with open(filename + "_tokenized.csv", 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for i,tokens in enumerate(tokenslist):
        writer.writerow(metalist[i] + [" ".join(tokens)])

with open(filename + "_postags.csv", 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for i,tokens in enumerate(poslist):
        writer.writerow(metalist[i] + [" ".join(tokens)])

with open(filename + "_stems.csv", 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for i,tokens in enumerate(stemslist):
        writer.writerow(metalist[i] + [" ".join(tokens)])

#     t.add_stem(stems)
#     t.add_pos(poss)
#     t.text = " ".join(tokens)




# infile = open(sys.argv[1],encoding="utf-8")







