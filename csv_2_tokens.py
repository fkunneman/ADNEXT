#!/usr/bin/env 

import csv
import sys
import frog
import codecs

fo = frog.FrogOptions(threads=25,parser=False)
frogger = frog.Frog(fo,"/vol/customopt/uvt-ru/etc/frog/frog-twitter.cfg")
csv.field_size_limit(sys.maxsize)

filename = sys.argv[1][:-4]

lines = []
metalist = []
tokenslist = []
stemslist = []
poslist = []

x = 0
print("reading in file")
data_initial = open(sys.argv[1],'r')
#with open(sys.argv[1], 'r') as csvfile:
reader = csv.reader((line.replace('\0','') for line in data_initial),delimiter=',')
    #reader = csv.reader(csvfile)
for row in reader:
        #print(x)
        #x+=1
    lines.append(row)

print("frogging")
lines = lines
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







