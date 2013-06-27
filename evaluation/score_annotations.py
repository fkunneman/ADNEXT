#!/usr/bin/env python

import argparse
from evalset import Evalset

parser = argparse.ArgumentParser(description = "Program to process a file containing tweets with Frog en write output")

parser.add_argument('-i', action = 'store', required = True, help = "the input file")
parser.add_argument('-o', action = 'store', required = True, help = "the output file (for the positive precision score and cohens kappa")
parser.add_argument('-p', action='store', help = "[OPTIONAL] specify an output file for a precision at curve")
parser.add_argument('-d', action='store_true', help = "choose for a prudent scoring (annotations with doubt are not taken as positive)")

args = parser.parse_args()
infile = args.i
outfile = open(args.o,"w")
precision_at = args.p

evaluation = Evalset()
evaluation.set_instances_annotation(infile)
iaa = evaluation.calculate_interannotator_agreement()
scores = evaluation.return_precisions_annotations(doubt = args.d,plot = precision_at)
outfile.write("\nCohen's Kappa: " + str(iaa) + "\n\n")
for score in scores:
    outfile.write("Precision for " + str(score[0]) + " positive: " + str(score[1]) + "\n")
    
