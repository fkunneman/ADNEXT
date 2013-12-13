#!/usr/bin/env python

import argparse
from classifier import Classifier
from collections import defaultdict
import codecs
import os
import re

parser=argparse.ArgumentParser(description="Program to perform a classification experiment with event tweets in a sliding window fashion")
parser.add_argument('-i', action='store', nargs='+', required=True, help="the files with tweets per event")
parser.add_argument('-d', action='store', help="the directory in which to write classification files")
parser.add_argument('-c', action='store', required=True, choices=["svm","lcs","knn","winnow","ibt","dist","random","majority"], help="the classifier")
parser.add_argument('-f', action='store', required=False, type=int, help="[OPTIONAL] to select features based on frequency, specify the top n features in terms of frequency")
parser.add_argument('--step', action='store', default=1, type=int, help="specify the stepsize of instance windows; [DEFAULT] = 1")
parser.add_argument('--window', action='store', default=100, type=int, help="specify the size of instance windows; [DEFAULT] = 100")
parser.add_argument('--depth', action='store', default=1, type=int, help="specify the depth of file characterizations; [DEFAULT] = 1)")
parser.add_argument('--scaling', action='store', default='binary', help='')

args=parser.parse_args() 

print "Window",args.window,"step",args.step

if len(args.i) <= 1:
    print "not enough event  files, exiting program..."
    exit()
depth = args.depth * -1

#read in instances
print "Reading in events..."
event_instances = defaultdict(list)
for ef in args.i:
    instance_file=codecs.open(ef,"r","utf-8")
    instances_raw=instance_file.readlines()
    instance_file.close()
    event_txt = "/".join(ef.split("/")[depth:])
    event = re.sub(".txt","",event_txt)
    #make list of tweet dicts
    tweets = []
    for tweet in instances_raw:
        values = tweet.strip().split("\t")
        tweets.append({"features":(values[-1].split(" ")),"label":values[1],"meta":values[:-1]})    
    #generate instance windows based on window- and stepsize
    i = 0
    while i+args.window < len(tweets):
        window = tweets[i+args.window]
        features = []
        for tweet in tweets[i:i+args.window]:
            features.extend(tweet["features"])
        i+=args.step     
        event_instances[event].append({"features":features,"label":window["label"],"meta":window["meta"]})

print "Starting classification..."
#divide train and test events
events = event_instances.keys()
testlen = int(len(events)/10)
#make folds
for i in range(0,len(events),testlen):
#,event in enumerate(events):
    try:
        train_events = events[:i] + events[i+testlen:]
        test_events = [events[j] for j in range(i,i+testlen)]
    except IndexError:
        train_events = events[:i]
        test_events = [events[j] for j in range(i,len(events))]
    train = sum([event_instances[x] for x in train_events],[])
    test = []
    for event in test_events:
        testdict = {}
        eventdir = args.d + event + "/" + args.scaling + "/"
        eventout = eventdir + str(args.window) + "_" + str(args.step) + ".txt"
        if not os.path.exists(eventdir):
            d = depth
            while d <= -1: 
                if not os.path.exists("/".join(eventdir.split("/")[:d])):
                    os.system("mkdir " + "/".join(eventdir.split("/")[:d]))
                d+=1
        testdict["out"] = eventout
        testdict["instances"] = event_instances[event]
        test.append(testdict)
    #set up classifier object
    cl = Classifier(train,test,classifier=args.c,scaling=args.scaling)
    print "balancing..."
    cl.balance_data()
    print "counting..."
    cl.count_feature_frequency()
    if args.f:
        print "pruning..."
        cl.prune_features_topfrequency(args.f)
    #generate sparse input
    print "indexing..."
    cl.index_features()
    #generate classifiers
    print "classifying..."
    if args.c == "svm":
        cl.classify_svm()
    #print events
    # train = sum([event_instances[x] for x in train_events],[])
    # test = event_instances[event]
    # #set up classifier object
    # eventdir = args.d + event + "/" + args.scaling + "/"
    # eventout = eventdir + str(args.window) + "_" + str(args.step) + ".txt"
    # if not os.path.exists(eventdir):
    #     d = depth
    #     while d <= -1: 
    #         if not os.path.exists("/".join(eventdir.split("/")[:d])):
    #             os.system("mkdir " + "/".join(eventdir.split("/")[:d]))
    #         d+=1
    # print "Classifier " + event + "..."
    # cl = Classifier(train,test,directory = eventout,classifier=args.c,scaling=args.scaling)
    # print "balancing..."
    # cl.balance_data()
    # print "counting..."
    # cl.count_feature_frequency()
    # if args.f:
    #     print "pruning..."
    #     cl.prune_features_topfrequency(args.f)
    # #generate sparse input
    # print "indexing..."
    # cl.index_features()
    # #generate classifiers
    # print "classifying..."
    # if args.c == "svm":
    #     cl.classify_svm()
