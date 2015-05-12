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
tokenslist = []
stemslist = []
poslist = []

print("reading in file")
with open(sys.argv[1], 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        lines.append(row)

lines = lines[:50]
l = len(lines)
for i,line in enumerate(lines):
    print("line",i,"of",l)   
    tokenizer.process(lines)
    for token in tokenizer:
        print(token.text,token.role,token.type())
