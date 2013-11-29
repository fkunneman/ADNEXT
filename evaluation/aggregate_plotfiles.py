#!/usr/bin/env python

import sys
from collections import defaultdict

outplot = open(sys.argv[1],"w")
plotfiles = sys.argv[2:]

plotdict = defaultdict(list)

plotreads = [open(x).readlines() for x in plotfiles]
for plot in plotreads:
    for line in plot:
        tokens = line.strip().split("\t")
        plotdict[int(tokens[0])].append(int(tokens[1]))

for tte in sorted(plotdict.keys()):
    mean = sum(plotdict[tte]) / len(plotdict[tte])
    outplot.write(str(tte) + "\t" + str(mean) + "\n")

