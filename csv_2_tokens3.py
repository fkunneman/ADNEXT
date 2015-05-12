#!/usr/bin/env 

import csv
import sys
import frog
import ucto

fo = frog.FrogOptions(threads=25)
frogger = frog.Frog(fo,"/home/fkunneman/netlogconf/frog-netlog.cfg")
csv.field_size_limit(sys.maxsize)

#ucto_settingsfile = "/home/fkunneman/netlogconf/tokconfig-nl-netlog"
#tokenizer = ucto.Tokenizer(ucto_settingsfile)

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
lines = lines[:30]
l = len(lines)
for i,line in enumerate(lines):
    print("line",i,"of",l)
    #tokenizer = ucto.Tokenizer(ucto_settingsfile)
    #tokenizer.process(line[-1])
    #print(line)
    #for x in tokenizer:
    #    print(x.text,x.role,x.type())   
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
    poslist.append(pos)
    stemslist.append(stems)

with open(filename + "_tokenized.csv", 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for i,tokens in enumerate(tokenslist):
        writer.writerow(metalist[i] + [" ".join(tokens)])

with open(filename + "_postags.csv", 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for i,pos in enumerate(poslist):
        writer.writerow(metalist[i] + [" ".join(pos)])

with open(filename + "_lemmatized.csv", 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for i,stems in enumerate(stemslist):
        writer.writerow(metalist[i] + [" ".join(stems)])

#     t.add_stem(stems)
#     t.add_pos(poss)
#     t.text = " ".join(tokens)




# infile = open(sys.argv[1],encoding="utf-8")







