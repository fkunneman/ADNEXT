#!/usr/bin/env python

import sys
from collections import defaultdict
import gen_functions

infile = open(sys.argv[1])
outfile = open(sys.argv[2],"w")
headers = sys.argv[3:]

cols = defaultdict(list)
for line in infile.readlines():
    tokens = line.strip().split(" ")
    for i,token in enumerate(tokens):
        cols[i].append(token)

aggregates = []
for i in range(len(cols.keys())):
    col = cols[i]
    mean = sum(col) / len(col)
    stdev = gen_functions.return_standard_deviation(col)
    aggregates.append(mean + " (" + stdev + ")")

outfile.write("\t".join(headers) + "\n" + "\t".join(aggregates))