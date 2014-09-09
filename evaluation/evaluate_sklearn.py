#!/usr/bin/env python

import argparse
import re
import codecs
from collections import defaultdict

from evalset import Evalset

parser = argparse.ArgumentParser(description = "Program to read svm output and evaluate the \
    performance")

parser.add_argument('-t', action = 'store', nargs='+',required=True, help = "the target files")
parser.add_argument('-w', action='store', required=True, help = "dir to write results to")
parser.add_argument('--id', action='store_true', 
    help = "specify whether id's of the instances are included")
parser.add_argument('--text', action='store_true', 
    help = "specify whether the text of the instances is included")
parser.add_argument('-f', action='store', type = int, required=False, 
    help = "[OPTIONAL] give the number of instances to choose to rank classifications by score and write " + 
    "the top n instances to a file (presumes a text or id to be included with instances)")

args = parser.parse_args()

#collect target-observation pairs
instances = []
for t in args.t:
    targets = open(t)
    for line in targets.readlines()[7:]:
        tokens = line.strip().split("\t")
        if len(tokens) == 3:
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
