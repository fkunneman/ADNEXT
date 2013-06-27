#! /usr/bin/env python

import sys
from collections import defaultdict
import re
from matplotlib import pyplot as pplt
import argparse

parser = argparse.ArgumentParser(description = "Generate LCS-files and parts and an additional metafile based on files with tweets.")
parser.add_argument('-p', action='store', required = True, help = 'Outfile for the plot')  
parser.add_argument('-c', action='store', nargs = "+", required = True, help = 'Files with coordinates')
parser.add_argument('-l', action='store', nargs = "+", required = True, help = 'legend entries for each file (in the same order)')

args = parser.parse_args() 
outplot = args.p
coordinate_files = args.c
legend_entries = args.l

linestyles = ["-","--","-.",":"]
i = 0
legend = []

for x,coordinate_file in enumerate(coordinate_files):
	coordinates = open(coordinate_file)
	xaxis = []
	yaxis = []
	for line in coordinates:
		tokens = line.strip().split(" ")
		actual_time = float(tokens[0])
		absolute_error = float(tokens[1])
		xaxis.append(actual_time * -1)
		yaxis.append(absolute_error)
	pplt.plot(xaxis,yaxis,linestyle = linestyles[i])
	if i == 3: 
		i = 0	
	else:	
		i += 1

pplt.ylim((0,200))
pplt.legend(legend_entries,loc = "upper right",ncol = 1)
pplt.ylabel("absolute prediction error (per hour)")
pplt.xlabel("time before the event (in hours)")
pplt.savefig(outplot)

