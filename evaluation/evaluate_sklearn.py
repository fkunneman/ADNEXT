#!/usr/bin/env python

from __future__ import division
import argparse
import re
import codecs
from collections import defaultdict
from matplotlib import pyplot as plt
from scipy import stats
from evalset import Evalset

parser = argparse.ArgumentParser(description = "Program to read svm output and evaluate the \
    performance")

parser.add_argument('-t', action = 'store', nargs='+',required=True, help = "the target files")
parser.add_argument('-w', action='store', required=True, help = "dir to write results to")
parser.add_argument('--header', action="store_true", help = "specify if the first 7 lines are not to be evaluated")
parser.add_argument('--id', action='store_true', 
    help = "specify whether id's of the instances are included")
parser.add_argument('--text', action='store_true', 
    help = "specify whether the text of the instances is included")
parser.add_argument('-f', action='store', type = int, required=False, 
    help = "[OPTIONAL] give the number of instances to choose to rank classifications by score and write " + 
    "the top n instances to a file (presumes a text or id to be included with instances)")
parser.add_argument('-p', action='store_true', help = "[OPTIONAL] choose to plot a precision-at curve)")

args = parser.parse_args()

start = 0
if args.header:
    start = 7

#collect target-observation pairs
instances = []
for t in args.t:
    targets = open(t)
    for line in targets.readlines()[start:]:
        tokens = line.strip().split("\t")
        if len(tokens) >= 3:
            tokens2 = tokens[1].split()
            tokens3 = tokens[2].split()
        else:
            tokens2 = tokens[0].split()
            tokens3 = tokens[1].split()
        label = tokens2[0]
        classification = tokens2[1]
        if len(tokens3) == 2:
            score = tokens3[1]
        else:
            score = tokens3[0]
        instance = [label,classification,score]
        if args.text:
            if len(tokens) == 3:
                instance.append(tokens[0])
            else:
                instance.append("-")
        if args.id:
            instance.append(tokens[0])
        instances.append(instance)

#insert instances
evaluation = Evalset()
evaluation.add_instances(instances,score=True,text=args.text,tid=args.id)
evaluation.calculate_general()

#write results
results = open(args.w + "results.txt","w")
outcomes = evaluation.calculate_outcome()
for label in outcomes:
    results.write("\t".join([str(x) for x in label]) + "\n")
results.close()

if args.id:
    idfile = open(args.w + "share.txt","w")
    for instance in evaluation.instances:
        idfile.write(instance.id + " " + instance.label + " " + instance.classification + "\n")
    idfile.close()

if args.f:
    #write tweets
    rankfile = open("/".join(args.w.split("/")[:-1]) + "/ranked_tweets.txt" ,"w")
    for instance in evaluation.return_ranked_score(args.f):
        rankfile.write("\t".join(instance) + "\n")
    fpfile = open("/".join(args.w.split("/")[:-1]) + "/ranked_fps.txt" ,"w")
    for instance in evaluation.return_rankedfp(args.f,"1.0"):
        fpfile.write("\t".join(instance) + "\n")
    rankfile.close()
    fpfile.close()

if args.p:
    plotfile = "/".join(args.w.split("/")[:-1]) + "/prat_curve.png"
    x = []
    y = []
    # plotfile = open(re.sub(".png",".txt",args.plot),"w")
    instances = evaluation.return_ranked_score(500)
    for i in range(1,500):
#        print instances[:i]
        tp = len([p for p in instances[:i] if p[2] == p[3]])
#        print tp,len(instances[:i])
        #print [p.classification for p in evaluation.instances[:i]]
        #print tp
        precision = tp / i
        #plotfile.write(str(i) + " " + str(precision) + "\n")
        x.append(i)
        y.append(precision)
        #plotfile.write(str(i) + " " + str(precision) + "\n")
    #plotfile.close()

    plt.plot(x,y,linewidth=3)
    plt.ylabel('Precision')
    plt.xlabel('Rank by classifier confidence')
    plt.savefig(plotfile,bbox_inches="tight")
