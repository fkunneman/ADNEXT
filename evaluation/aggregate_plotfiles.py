#!/usr/bin/env python

import sys
from collections import defaultdict

outplot = sys.argv[1]
plotfiles = sys.argv[2:]

plotdict = defaultdict(list)

plotreads = [open(x).readlines() for x in plotfiles]
for plot in plotreads:
    for line.strip() in plot:
        tokens = line.split("\t")
        plotdict[tokens[0]].append(int(tokens[1]))

print sorted(plotdict.keys())

