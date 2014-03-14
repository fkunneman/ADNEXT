#!/usr/bin/env python

import argparse
from classifier import Classifier
from collections import defaultdict
import codecs
import os
import re
import numpy

import time_functions
import gen_functions

parser=argparse.ArgumentParser(description="Program to perform a classification experiment with event tweets in a sliding window fashion")
parser.add_argument('-i', action='store', nargs='+', required=True, help="the files with tweets per event")
parser.add_argument('-d', action='store', help="the directory in which to write classification files")
parser.add_argument('-c', action='store', required=True, choices=["svm","svr","median_baseline"], help="the classifier")
parser.add_argument('-f', action='store', required=False, type=int, help="[OPTIONAL] to select features based on frequency, specify the top n features in terms of frequency")
parser.add_argument('--featurecol', action='store', required=False, type=int, help="the column of features")
parser.add_argument('--stdev', action='store', required = False, type=float, help = "choose to remove features with a standard deviation above the given threshold")
parser.add_argument('--step', action='store', default=1, type=int, help="specify the stepsize of instance windows; [DEFAULT] = 1")
parser.add_argument('--window', action='store', default=100, type=int, help="specify the size of instance windows; [DEFAULT] = 100")
parser.add_argument('--depth', action='store', default=1, type=int, help="specify the depth of file characterizations; [DEFAULT] = 1)")
parser.add_argument('--scaling', action='store', default='binary', help='')
parser.add_argument('--majority', action='store_true', help = 'specify if tweet windows are classified as sets of loose tweets')
parser.add_argument('--jobs', action='store', type = int, required=False, help = 'specify the number of cores to use')
parser.add_argument('--cw', action='store_true', help = 'choose to set class weights based on training frequency (instead of balancing the training data)')
parser.add_argument('--balance', action='store_true', help = 'choose to balance class frequency')
parser.add_argument('--date', action='store', type = int, required=False,help='specify the date column to convert time features')
parser.add_argument('--median', action='store_true',help='choose to calculate median time to event of time expressions')

args=parser.parse_args() 

print "Window",args.window,"step",args.step

if len(args.i) <= 1:
    print "not enough event files, exiting program..."
    exit()
depth = args.depth * -1

#read in instances
print "Reading in events..."
event_instances = defaultdict(list)
if args.majority or args.median:
    event_instances_loose = defaultdict(list)
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
        try:
            features = (values[args.featurecol].split(" "))
        except:
            features = ()
        tweets.append({"features":features,"label":values[1],"meta":values[:-1]})    
    #generate instance windows based on window- and stepsize
    if args.majority or args.median:
        event_instances_loose[event] = tweets
    j = 0
    while j+args.window < len(tweets):
        window = tweets[j+args.window]
        features = []
        for tweet in tweets[j:j+args.window]:
            features_tweet = tweet["features"][:]
            if args.date:
                for i,feature in enumerate(features_tweet):
                    if re.match(r"date_\d{2}-\d{2}-\d{4}",feature):
                        windowdate = time_functions.return_datetime(window["meta"][args.date],setting="vs")
                        date_extract = re.search(r"date_(\d{2}-\d{2}-\d{4})",feature)
                        refdate = time_functions.return_datetime(date_extract.groups()[0],setting="eu")
                        features_tweet[i] = str(time_functions.timerel(refdate,windowdate,"day") * -1) + "_days"
                        #print refdate,windowdate,str(time_functions.timerel(refdate,windowdate,"day") * -1) + "_days"
                  #print refdate,windowdate,str(time_functions.timerel(refdate,windowdate,"day") * -1) + "_days"
            if args.median:
                for i,feature in enumerate(features):
                    if re.search(r"timex_",feature):
                        windowdate = time_functions.return_datetime(window["meta"][args.date],setting="vs")
                        tweetdate = time_functions.return_datetime(tweet["meta"][args.date],setting="vs")
                        extra = time_functions.timerel(windowdate,tweetdate,"day")
                        features[i] = feature + "_" + str(extra)
            features.extend(features_tweet)

        if args.c == "svr":
            try:
                lab = float(window["label"])     
            except:
                if window["label"] == "during" or lab == "after":
                    break
        else:
            lab = window["label"]
        if len(features) > 0:
            event_instances[event].append({"features":features,"label":lab,"meta":window["meta"]})
        j+=args.step

print "Starting classification..."
#divide train and test events
events = sorted(event_instances.keys())
testlen = int(len(events)/10)
#make folds
for i in range(0,len(events),testlen):
    try:
        train_events = events[:i] + events[i+testlen:]
        test_events = [events[j] for j in range(i,i+testlen)]
    except IndexError:
        train_events = events[:i]
        test_events = [events[j] for j in range(i,len(events))]
    if args.median:
        #generate feature_tte list
        print "generating feature_tte list"
        feature_tte = defaultdict(list)
        for ev in train_events:
            for tweet in event_instances_loose[ev]:
                for feature in tweet["features"]:
                    if re.search(r"timex_",feature):
                        print "before",feature
                        try:
                            feature_tte[feature].append(int(tweet["label"]))
                            # print "after","_".join(feature.split("_")[:-1])
                        except:
                            print "after_continue"
                            continue

        #calculate_median
        print "calculating median"
        feature_new = {}
        for feature in feature_tte.keys():
            if gen_functions.return_standard_deviation(feature_tte[feature]) < 2 and len(feature_tte[feature]) >= 2:
                feature_new[feature] = str(int(numpy.median(feature_tte[feature]))) + "_days"
            else:
                feature_new[feature] = feature
        #convert features
        print "converting features"
        for ev in train_events:
            for instance in event_instances[ev]:
                #print "before", instance["features"]
                new_features = []
                print instance["features"]
                for r,feature in enumerate(instance["features"]):
                    if re.search(r"timex_",feature):
                        #print feature
                        featureo = "_".join(feature.split("_")[:-1])
                        if not re.search(r"timex_",feature_new[featureo]):
                            extra_reg = int(feature.split("_")[-1])
                            new_feature = str(int(feature_new[featureo].split("_")[0]) + extra) + "days"
                            new_features.append(new_feature)
                        #instance["features"][r] = feature_new[feature]
                        #print instance["features"][r]
                    else:
                        new_features.append(feature)
                print new_features
                instance["features"] = new_features
                #print "after", instance["features"]
            quit()
        for ev in test_events:
            for instance in event_instances[ev]:
#                print instance["features"]
                new_features = []
                for r,feature in enumerate(instance["features"]):
                    if re.search(r"timex_",feature):
                        try:
                            if not re.search(r"timex_",feature_new[feature]):
                                new_features.append(feature_new[feature])     
                        except:
                            continue
                    else:
                        new_features.append(feature)
                instance["features"] = new_features
#                print instance["features"]

    train = sum([event_instances[x] for x in train_events],[])
    test = []
    for event in test_events:
        print event
        testdict = {}
        eventparts = event.split("/") + [args.scaling]
#        print eventparts
#        quit()
        eventdir = args.d 
        for part in eventparts:
            eventdir = eventdir + part + "/"
            if not os.path.exists(eventdir):
                os.system("mkdir " + eventdir)
        print eventdir
        if args.majority:
            eventout = eventdir + "tweet.txt"
        else:
            eventout = eventdir + str(args.window) + "_" + str(args.step) + ".txt"
#         if not os.path.exists(eventdir):
#             d = depth
#             while d <= -1: 
# #                print eventdir
#                 if not os.path.exists("/".join(eventdir.split("/")[:d])):
#                     print "mkdir " + "/".join(eventdir.split("/")[:d])
#                     os.system("mkdir " + "/".join(eventdir.split("/")[:d]))
#                     d+=1
        testdict["out"] = eventout
        testdict["instances"] = event_instances[event]
        test.append(testdict)
    if args.c == "median_baseline":
        for td in test:
            outfile = open(td["out"],"w")
            instances = td["instances"]
            # print [instance["features"] for instance in instances]
            # quit()

            for instance in instances:
                #extract day_estimations
#                ests = []
                labelcount = defaultdict(int)
                for feature in instance["features"]:
                    #if re.search(r"days",feature):
                    #    ests.append(feature)
                #if len(ests) > 0:
                    num = re.search(r"(-?\d+)_days",topest).groups()[0]
                    for est in ests:
                        labelcount[est] += 1
                    topest = [e for e in sorted(labelcount, key=labelcount.get, reverse=True)][0]
                    
                else:
                    num = "during"
                outfile.write(instance["label"] + " " + str(num) + "\n")
            outfile.close() 
    else:
        #set up classifier object
        if args.jobs:
            cl = Classifier(train,test,jobs=args.jobs,scaling=args.scaling)
        else:
            cl = Classifier(train,test,scaling=args.scaling)
        if args.stdev:
            cl.filter_stdev(args.stdev, "timex_")
        if args.balance:
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
            if args.cw:
                cl.classify_svm(classweight="auto")
            else:
                cl.classify_svm()
        elif args.c == "svr":
            print "svr"
            if args.cw:
                cl.classify_svm(t="continuous",classweight="auto")
            else:
                cl.classify_svm(t="continuous")
