#!/usr/bin/env 

import csv
import sys
import frog

fo = frog.FrogOptions(threads=20)
frogger = frog.Frog(fo,"/vol/customopt/uvt-ru/etc/frog/frog-twitter.cfg")
csv.field_size_limit(sys.maxsize)

filename = sys.argv[1][:-4]

metalist = []
tokenslist = []
stemslist = []
poslist = []

with open(sys.argv[1], 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader[:20]:
        tokens = []
        stems = []
        pos = []
        metalist.append(row[:-1])
        data = frogger.process(row[-1])
        for token in data:
                tokens.append(token["text"])
                pos.append(token["pos"])
                stems.append(token["lemma"])
        tokenslist.append(tokens)
        poslist.append(tokens)
        stemslist.append(tokens)

with open(filename + "tokenized.csv", 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for i,tokens in enumerate(tokenslist):
        writer.writerow(metalist[i] + [" ".join(tokens)])

with open(filename + "postags.csv", 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for i,tokens in enumerate(poslist):
        writer.writerow(metalist[i] + [" ".join(tokens)])

with open(filename + "stems.csv", 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for i,tokens in enumerate(stemslist):
        writer.writerow(metalist[i] + [" ".join(tokens)])

#     t.add_stem(stems)
#     t.add_pos(poss)
#     t.text = " ".join(tokens)




# infile = open(sys.argv[1],encoding="utf-8")







