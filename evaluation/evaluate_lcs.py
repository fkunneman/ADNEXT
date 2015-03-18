#!/usr/bin/env python

import argparse
import re
import codecs
from collections import defaultdict

from evalset import Evalset
import gen_functions

parser = argparse.ArgumentParser(description = "Program to read lcs output and evaluate the \
    performance")

parser.add_argument('-t', action = 'store', nargs='+',required=True, help = "the target files")
parser.add_argument('-c', action='store', nargs='+',required=True, 
    help = "the classification files")
parser.add_argument('-w', action='store', required=True, help = "file to write results to")
parser.add_argument('-f', action='store', required=False, 
    help = "give the filesdirectory to write an intermediate output with instance " +
        "text and classification")
parser.add_argument('-n', action='store', type = int, required=False, 
    help = "give the number of tweets to choose to rank classifications by score and write " + 
    "the top n tweets to a file")

args = parser.parse_args()

#collect target-observation pairs
instances = []
name_instance = {}
filename_instance = {}
filename_scores = defaultdict(lambda : {})
for t in args.t:
    targets = open(t)
    for line in targets.readlines():
        tokens = line.strip().split(" ")
        name_instance[tokens[0]] = tokens[1]
    targets.close()
for c in args.c:
    observations = open(c)
    for line in observations.readlines():
        tokens = line.strip().split("  ")
        filename = tokens[0].strip()
        scores = tokens[1]
        classification_scores = tokens[1].split(" ")
        classification_score = classification_scores[0].split(":")
        non_classification_score = classification_scores[1].split(":")
        filename_scores[filename][re.sub(r"\?","",classification_score[0])] = classification_score[1]
        filename_scores[filename][re.sub(r"\?","",non_classification_score[0])] = \
            non_classification_score[1]
        classification = re.sub("\?","",classification_score[0])
        score = classification_score[1]  
        instance = (name_instance[filename],classification,score)
        instances.append(instance)
        filename_instance[filename] = instance

#generate outcomes
evaluation = Evalset()
evaluation.add_instances(instances)
evaluation.calculate_general()

#write results
outfile = open(args.w,"w")
evaluation.calculate_general()
for label in evaluation.calculate_outcome():
    outfile.write("\t".join([str(x) for x in label]) + "\n")
outfile.close()

if args.f:
    outfile = codecs.open("/".join(args.w.split("/")[:-1]) + "/stand_output.txt","w","utf-8")
    for filename in sorted(filename_instance.keys()):
        instance = filename_instance[filename]
        fileopen = codecs.open(args.f+filename,"r","utf-8")
        text = " ".join([x for x in fileopen.read().split("\n") if not re.search("_",x)])
        label = instance[0]
        classification = instance[1]
        labels = sorted(filename_scores[filename].keys())
        outfile.write(text + "\t" + label + " " + classification + " " + "\t".join([" ".join([x,filename_scores[filename][x]]) for x in labels]) + "\n")
    outfile.close()

if args.n:
    #make filename - meta dict:
    print "making meta-dict"
    metafile = codecs.open("/".join(args.c[0].split("/")[:-1]) + "/meta.txt","r","utf-8")
    file_meta = defaultdict(list)
    for line in metafile.readlines():
        tokens = line.strip().split("\t")
        file_meta[tokens[0]] = tokens[1:]
    metafile.close()
    print "writing ranked file"
    #write tweets
    rankfile = codecs.open("/".join(args.w.split("/")[:-1]) + "/ranked_tweets.txt" ,"w","utf-8")
    for tweet in sorted(instances,key=lambda x: x[2],reverse = True)[:args.n]:
        # fileopen = codecs.open(args.f + tweet[3],"r","utf-8")
        # feats =  fileopen.read().split("\n")
        meta = file_meta[tweet[3]]
        feats = meta[-1].split(" ")
#        print feats
        i = 0
        while not re.search(r"<s>",feats[i]):
    #        print feats[i],i
            i += 1
        #print "len",i,len(feats),feats[:i]
        rankfile.write("\t".join([str(tweet[2]),meta[0],meta[2],meta[3],meta[4],
            " ".join(feats[:i])]) + "\n")
    rankfile.close()
