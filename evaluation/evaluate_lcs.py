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
parser.add_argument('-c', action='store', nargs='+',required=True, help = "the classification files")
parser.add_argument('-w', action='store', required=True, help = "file to write results to")
parser.add_argument('-f', action='store', type = int, required=False, help = "give the number of tweets to choose to rank classifications by score and write the top n tweets to a file")

args = parser.parse_args()

#collect target-observation pairs
instances = []
name_instance = {}
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
        classification_score = tokens[1].split(" ")[0].split(":")
        classification = re.sub("\?","",classification_score[0])
        score = classification_score[1]  
        instances.append((name_instance[filename],classification,score,filename))

#generate outcomes
evaluation = Evalset()
evaluation.add_instances(instances)
outcomes = evaluation.calculate_general()

#write results
outfile = open(args.w,"w")
for label in outcomes:
    #columns = gen_functions.format_list(label,'20')
    #outfile.write("".join(columns) + "\n")
    outfile.write("\t".join([str(x) for x in label]) + "\n")
outfile.close()

if args.f:
    #make filename - meta dict:
    print "making meta-dict"
    metafile = codecs.open("/".join(args.c.split("/")[:-1]) + "/meta.txt","r","utf-8")
    file_meta = defaultdict(list)
    for line in metafile.readlines():
        tokens = line.strip().split("\t")
        file_meta[tokens[0]] = tokens[1:]
    metafile.close()
    print "writing ranked file"
    #write tweets
    rankfile = codecs.open("/".join(args.w.split("/")[:-1]) + "/ranked_tweets.txt" ,"w","utf-8")
    for tweet in sorted(instances,key=lambda x: x[2],reverse = True)[:args.f]:
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
        rankfile.write("\t".join([str(tweet[2]),meta[0],meta[2],meta[3],meta[4]," ".join(feats[:i])]) + "\n")
    rankfile.close()
