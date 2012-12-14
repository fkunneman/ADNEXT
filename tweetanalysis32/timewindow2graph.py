#! /usr/bin/env python

import sys
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(description = "Make an accumulated tweetfrequency-graph out of coordinatesfiles")

parser.add_argument('-c', action='store', nargs='+', required = True, help = 'Files with graph coordinates')
parser.add_argument('-o', action='store', required = True, help = 'The file to write the graph to')
parser.add_argument('-l', action='store', nargs='+', help = 'Legenda entries for the different files (same amount as coordinatefiles required (default = numbering)')
parser.add_argument('-x', action='store', required = True, help = 'Label for the x-axis')
parser.add_argument('-y', action='store', required = True, help = 'Label for the y-axis)')
parser.add_argument('-t', action='store', required = True, help = 'The title of the graph')

args = parser.parse_args() 

graphfiles = args.c
outfile = args.o
legend = tuple(args.l)
xl = args.x
yl = args.y
title = args.t

xaxes = []
yaxes = []
for graphfile in graphfiles:
	coordinates = open(graphfile,"r")
	xaxis = []
	yaxis = []
	for coordinate in coordinates:
		x_and_y = coordinate.split("\t")
		xaxis.append(x_and_y[0])
		yaxis.append(x_and_y[1])
	plt.plot(xaxis,yaxis)

plt.legend(legend,'upper left')
plt.ylabel(yl)
plt.xlabel(xl)
plt.title(title)
plt.savefig(outfile)
