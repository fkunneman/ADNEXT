#!/usr/bin/env 

import csv
import sys
import ucto

csv.field_size_limit(sys.maxsize)
ucto_settingsfile = "/vol/customopt/uvt-ru/etc/ucto/tokconfig-nl-twitter"
tokenizer = ucto.Tokenizer(ucto_settingsfile)

filename = sys.argv[1][:-4]

lines = []
metalist = []

print("reading in file")
with open(sys.argv[1], 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        lines.append(row)

#lines = lines[:50]
indices = []
l = len(lines)
for i,line in enumerate(lines):
    print("line",i,"of",l)   
    tokenizer.process(line[-1])
    metalist.append(line[:-1])
    ind = []
    x = 0
    for token in tokenizer:
        x+=1
        #print(token.text,token.role,token.type(),token.isendofsentence())
        if token.isendofsentence():
            ind.append(str(x))
            x = 0
    indices.append(" ".join(ind))

with open(filename + "_sentences.csv", 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for i,tokens in enumerate(metalist):
        writer.writerow(tokens + [indices[i]])

