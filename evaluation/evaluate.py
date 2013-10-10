#!/usr/bin/env python

import argparse
from evalset import Evalset
from collections import defaultdict

parser = argparse.ArgumentParser(description = "Program to process a file containing tweets with Frog en write output")

parser.add_argument('-l', action = 'store', required = True, nargs='+', help = "the label / label+classification files (required)")
parser.add_argument('-c', action='store', required=False, nargs='+', help = "the classification files (if separated)")
parser.add_argument('-m', action='store', required=False, nargs='+', help = "the files with meta-information")
parser.add_argument('-o', action='store', required=True, help = "file to write the results to (required)")
parser.add_argument('-i', action = 'store', choices = ["lcs","meta","knn"], help="specify the input type of label (and classification) files")
parser.add_argument('-fp', action='store', required = False, nargs = '+', help = "to extract a ranked list of the most confident false positive instances, specify a file name, the class to which the false positives apply, the number of instances and the directory with tweet files")
parser.add_argument('-v', action='store', required = False, help = "[KNN] give a vocabulary file to link indexes to features")
parser.add_argument('--plot', action='store_true', help = "choose to plot data")

args = parser.parse_args()
evaluation = Evalset()

if args.v:
    evaluation.set_vocabulary(args.v)
   
if args.i == "lcs":
    labelfiles = args.l
    observationfiles = args.c
    for i,l in enumerate(labelfiles):
        evaluation.set_instances_lcs(l,observationfiles[i],"normal")
    results = evaluation.return_results()
    outfile = open(args.o,"w")
    for row in results:
        line = "\t".join(row)
        outfile.write(line)
    outfile.close()
    if args.fp:
        evaluation.extract_top(args.fp[0],args.fp[1],int(args.fp[2]),args.fp[3])
    #if args.tp:
    #    evaluation.extract_top()
    #if args.fn:
    #    evaluation.extract_top()

elif args.i == "meta":
    metafiles = args.l
    for m in metafiles:
        evaluation.set_instances_meta(m,args.w)
    
elif args.i == "knn":
    exit()


