#!/usr/bin/env python

import argparse
from collections import defaultdict
import re

parser = argparse.ArgumentParser(description = "Program to read lcs output and evaluate the \
    performance")

parser.add_argument('-t', action = 'store', nargs = '+', required = True, help = "the label dirs") #train tweets
parser.add_argument('-f', action='store', required=True, help = "good id file") #test tweets
# parser.add_argument('-c', action='store', nargs = '+', required=True, help = "the classification files") #test tweets
# parser.add_argument('-m', action='store', nargs = '+', required=True, help = "the meta files") #for emotiona category tweet ids
# parser.add_argument('-l', action='store', nargs = '+', required=True, help = "the list of emotion labels")
parser.add_argument('-b', action='store', required=True, help = "the file with background meta") #for background tweet ids
parser.add_argument('-w', action='store', required=True, help = "dir to write results to")
args = parser.parse_args()

# if not (len(args.t) == len(args.c) and len(args.c) == len(args.m)):
#     print "no equal sizes of label lists, exiting program"
#     quit()
# else:
#     print "label dicts of equal size, proceeding with program"
num_labels = len(args.t)

#load background dict
backgroundfile_tid = {}
print "loading in background dict"
backgroundfile_uid_time = defaultdict(lambda : {})
user_time_text_tid = defaultdict(lambda : defaultdict(lambda : {}))
background_meta = open(args.b)
ts = re.compile(r"\d{2}:\d{2}:\d{2}")
for line in background_meta.readlines():
    tokens = line.strip().split("\t")
    if ts.search(tokens[5]):
        time = tokens[5]
    else:
        time = tokens[4]
    #print tokens[1],",",time,",",tokens[-1]
    user_time_text_tid[tokens[6]][time][tokens[-1]] = tokens[0]
    if not time in backgroundfile_uid_time[tokens[1]].keys():
        backgroundfile_uid_time[tokens[6]][time] = tokens[0]
    else:
        backgroundfile_uid_time[tokens[6]][time] = "double"
background_meta.close()

# print "skimming through tweet files"
# for f in args.f:
#     tweetfile = open(f)
#     for line in tweetfile.readlines():
#         tokens = line.strip().split("\t")
#         time = tokens[2] + " " + tokens[3]
#         try:
#             if not backgroundfile_uid_time[tokens[1]][time] == "double":
#                 filename = backgroundfile_uid_time[tokens[1]][time]
#             else:
#                 words = tokens[-1].split(" ")
#                 new_words = []
#                 for w in words:
#                     if re.search("http",w):
#                         new_words.append("URL")
#                     else:
#                         new_words.append(w)
#                 #print tokens[1],time," ".join(new_words)
#                 filename = user_time_text_tid[tokens[1]][time][" ".join(new_words)]
#                 #print filename
#             backgroundfile_tid[filename] = tokens[0]
#         except:
#             continue

tweetfile = open(args.f)
for line in tweetfile.readlines():
    tokens = line.strip().split("\t")
    if ts.search(tokens[5]):
        time = tokens[5]
    else:
        time = tokens[4]
    try:
        if not backgroundfile_uid_time[tokens[6]][time] == "double":
            filename = backgroundfile_uid_time[tokens[6]][time]
        else:
            filename = user_time_text_tid[tokens[6]][time][tokens[7]]
            #print filename
        backgroundfile_tid[filename] = tokens[0]
    except:
        continue
tweetfile.close()


#for every label
print "running through labels"
for i in range(num_labels):
    labeldir = args.t[i]
    label = labeldir.split("/")[-2]
    train_file = open(labeldir + "train")
    test_file = open(labeldir + "test")
    meta_file = open(labeldir + "meta.txt")
    print i,"of",num_labels,",",label
    trainout = open(args.w + label + "_train.txt","w")
    testout = open(args.w + label + "_test.txt","w")
    #get trainids label from metafile
    for line in meta_file.readlines():
        trainout.write(line.split("\t")[1] + " " + label + "\n")
    meta_file.close()
    #obtain background train tweet ids
    print "obtaining background train tweet ids"
    for line in train_file.readlines():
        tokens = line.strip().split()
        if tokens[1] == "background":
            trainout.write(backgroundfile_tid[tokens[0]] + " background\n")
    train_file.close()
    trainout.close()
    #obtain background train tweet ids
    print "obtaining test tweet ids"
    for line in test_file.readlines():
        tokens = line.strip().split()
        testout.write(backgroundfile_tid[tokens[0]] + " " + tokens[1] + "\n")
    test_file.close()
    testout.close()




