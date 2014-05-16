#!/usr/bin/env python

import argparse
import re
import codecs

from evalset import Evalset
import gen_functions

parser = argparse.ArgumentParser(description = "Program to read lcs output and evaluate the \
    performance")

parser.add_argument('-t', action = 'store', required = True, help = "the target file")
parser.add_argument('-c', action='store', required=True, help = "the classification file")
parser.add_argument('-w', action='store', required=True, help = "file to write results to")
parser.add_argument('-f', action='store', required=False, help = "give the filedir choose to rank classifications by score and write the tweets to a file")

args = parser.parse_args()

#collect target-observation pairs
instances = []
name_instance = {}
targets = open(args.t)
for line in targets.readlines():
    tokens = line.strip().split(" ")
    name_instance[tokens[0]] = tokens[1]
targets.close()
observations = open(args.c)
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
    #write tweets
    rankfile = codecs.open("/".join(args.w.split("/")[:-1]) + "ranked_tweets.txt" ,"w","utf-8")
    print "rankfile", "/".join(args.w.split("/")[:-1]) + "/ranked_tweets.txt"
    for tweet in sorted(instances,key=lambda x: x[2],reverse = True)[:10000]:
        fileopen = codecs.open(args.f + tweet[3],"r","utf-8")
        feats = fileopen.read().split("\n")
#        print feats
        i = 0
        while not re.search("_",feats[i]):
            i += 1
        rankfile.write(str(tweet[2]) + "\t" + " ".join(feats[:i]) + "\n")
        fileopen.close()
    rankfile.close()
