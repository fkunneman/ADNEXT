#!/usr/bin/env python

import argparse
from evalset import Evalset
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description = "Program to plot a learning curve based on classifications with upschaled training data")

parser.add_argument('-l', action = 'store', required = True, nargs='+', help = "the label / label+classification files (required)")
parser.add_argument('-c', action='store', required=False, nargs='+', help = "the classification files (if separated)")
parser.add_argument('-t', action='store', required=True, nargs='+', help = "trainingfiles for each classification")
parser.add_argument('-m', action='store', required=False, nargs='+', help = "the files with meta-information")
parser.add_argument('-o', action='store', required=True, help = "name of the plotfile")
parser.add_argument('-i', action = 'store', choices = ["lcs","meta","knn"], help="specify the input type of label (and classification) files")

args = parser.parse_args()
xaxis = []
yaxis = []

for i,f in enumerate(args.l):
    evaluation = Evalset()
    if args.i == "lcs":
        evaluation.set_instances_lcs(args.c[i],labelfile=f)
        results = evaluation.return_results()
        yaxis.append(results[-1][-7])
        training_file = args.t[i]
        trainingopen = open(training_file)
        xaxis.append(len(trainingopen.readlines()))
        trainingopen.close()

plt.plot(xaxis,yaxis)
plt.xscale('log')
plt.ylabel("Micro-F1")
plt.xlabel("Size trainingdata")
plt.savefig(args.o)
