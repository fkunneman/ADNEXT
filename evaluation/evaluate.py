#!/usr/bin/env python

from __future__ import division
import argparse
from evalset import Evalset
from collections import defaultdict
import codecs
import re
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description = "Program to process a file containing tweets with Frog en write output")

parser.add_argument('-l', action = 'store', required = True, nargs='+', help = "the label / label+classification files (required)")
parser.add_argument('-c', action='store', required=False, nargs='+', help = "the classification files (if separated)")
parser.add_argument('-m', action='store', required=False, nargs='+', help = "the files with meta-information")
parser.add_argument('-o', action='store', required=True, help = "file to write the results to (required)")
parser.add_argument('-i', action = 'store', choices = ["lcs","meta","knn","simple"], help="specify the input type of label (and classification) files")
parser.add_argument('-fp', action='store', required = False, nargs = '+', help = "to extract a ranked list of the most confident false positive instances, specify a file name, the class to which the false positives apply, the number of instances and the directory with tweet files")
parser.add_argument('-v', action='store', required = False, help = "[KNN] give a vocabulary file to link indexes to features")
parser.add_argument('--plot', action='store', required=False, help = "choose to plot data")

args = parser.parse_args()
evaluation = Evalset()

if args.v:
    evaluation.set_vocabulary(args.v)
   
if args.i == "lcs":
    labelfiles = args.l
    observationfiles = args.c
    for i,l in enumerate(labelfiles):
        evaluation.set_instances_lcs(observationfiles[i],labelfile=l)

elif args.i == "simple":
    for lf in args.l:
    #     evaluation.set_instances_simple(lf)
        lines = codecs.open(lf,"r","utf-8").readlines()
        evaluation.add_instances([l.split("\t") for l in lines],score=True)

elif args.i == "meta":
    metafiles = args.l
    for m in metafiles:
        evaluation.set_instances_meta(m,args.w)
    
elif args.i == "knn":
    exit()

if args.plot:
    #precision_at = [1,5,10,25,50,100,250,500,1000]
#plotfile = open(sys.argv[1],"w")
    x = []
    y = []
    plotfile = open(re.sub(".png",".txt",args.plot),"w")
    for i,instance in enumerate(evaluation.instances):
        if i > 0:
            tp = len([p for p in evaluation.instances[:i] if p.classification == '1.0'])
            #print [p.classification for p in evaluation.instances[:i]]
            print tp
            precision = tp / i
            #plotfile.write(str(i) + " " + str(precision) + "\n")
            x.append(i)
            y.append(precision)
            plotfile.write(str(i) + " " + str(precision) + "\n")
    plotfile.close()

    plt.plot(x,y,linewidth=3)
    plt.ylabel('Precision')
    plt.xlabel('Rang op basis van de classifier confidence')
    plt.savefig(args.plot,bbox_inches="tight")
    #plotfile.close()

#results = evaluation.return_results()
#outfile = open(args.o,"w")
#for row in results:
#    line = "\t".join([str(e) for e in row]) + "\n"
#    outfile.write(line)
#outfile.close()
#if args.fp:
#    evaluation.extract_top(args.fp[0],args.fp[1],int(args.fp[2]),args.fp[3])
