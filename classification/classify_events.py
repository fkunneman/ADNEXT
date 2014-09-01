#!/usr/bin/env python

import argparse
from collections import defaultdict
import codecs
import os
import re
import numpy

from classifier import Classifier
import time_functions
import gen_functions

parser=argparse.ArgumentParser(description="Program to perform a classification experiment with event tweets in a sliding window fashion")
parser.add_argument('-i', action='store', nargs='+', required=True, help="the files with tweets per event (only events in -i gives 10-fold cross-validation)")
parser.add_argument('-t', action='store', nargs='+', required=False, help="the test-events (for a train-test setting)")
parser.add_argument('-d', action='store', help="the directory in which to write classification files")
parser.add_argument('-c', action='store', required=True, choices=["svm","svr","median_baseline"], help="the classifier")
parser.add_argument('-f', action='store', required=False, type=int, help="[OPTIONAL] to select features based on frequency, specify the top n features in terms of frequency")
parser.add_argument('--featurecol', action='store', required=False, type=int, help="the column of features")
parser.add_argument('--stdev', action='store', required = False, type=float, help = "choose to remove features with a standard deviation above the given threshold")
parser.add_argument('--step', action='store', default=1, type=int, help="specify the stepsize of instance windows; [DEFAULT] = 1")
parser.add_argument('--window', action='store', default=100, type=int, help="specify the size of instance windows; [DEFAULT] = 100")
parser.add_argument('--depth', action='store', default=1, type=int, help="specify the depth of file characterizations; [DEFAULT] = 1)")
parser.add_argument('--deptht', action='store', default=1, type=int, help="specify the depth of test file characterizations; [DEFAULT = 1)")
parser.add_argument('--scaling', action='store', default='binary', help='')
parser.add_argument('--majority', action='store_true', help = 'specify if tweet windows are classified as sets of loose tweets')
parser.add_argument('--jobs', action='store', type = int, required=False, help = 'specify the number of cores to use')
parser.add_argument('--cw', action='store_true', help = 'choose to set class weights based on training frequency (instead of balancing the training data)')
parser.add_argument('--balance', action='store_true', help = 'choose to balance class frequency')
parser.add_argument('--date', action='store', type = int, required=False,help='specify the date column to convert time features')
parser.add_argument('--median', action='store_true',help='choose to calculate median time to event of time expressions')
parser.add_argument('--tt', action='store_true',help='choose to only include tweets with time_expressions')
parser.add_argument('--median_out', action='store', help = 'choose to write median values to a file')

args=parser.parse_args() 

if args.median_out:
    median_out = codecs.open(args.median_out,"w","utf-8")

print "Window",args.window,"step",args.step

if len(args.i) <= 1:
    print "not enough event files, exiting program..."
    exit()
depth = args.depth * -1
deptht = args.deptht * -1

def read_events(eventfiles,d):
    #read in instances
    print "Reading in events..."
    event_instances = defaultdict(list)
    if args.majority or args.median:
        event_instances_loose = defaultdict(list)
    for ef in eventfiles:
        instance_file=codecs.open(ef,"r","utf-8")
        instances_raw=instance_file.readlines()
        instance_file.close()
        event_txt = "/".join(ef.split("/")[d:])
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
                if args.tt:
                    timeinfo = False
                for f in features:
                    if re.search("^(timex|date)",f):
                        timeinfo = True
                        break
                if args.date:
                    for i,feature in enumerate(features_tweet):
                        if re.match(r"date_\d{2}-\d{2}-\d{4}",feature):
                            timeinfo = True
                            windowdate = time_functions.return_datetime(window["meta"][args.date],setting="vs")
                            date_extract = re.search(r"date_(\d{2}-\d{2}-\d{4})",feature)
                            refdate = time_functions.return_datetime(date_extract.groups()[0],setting="eu")
                            features_tweet[i] = str(time_functions.timerel(refdate,windowdate,"day") * -1) + "_days"
                            #print refdate,windowdate,str(time_functions.timerel(refdate,windowdate,"day") * -1) + "_days"
                      #print refdate,windowdate,str(time_functions.timerel(refdate,windowdate,"day") * -1) + "_days"
                if args.median:
                    for i,feature in enumerate(features_tweet):
                        if re.search(r"timex_",feature):
                            timeinfo=True
                            windowdate = time_functions.return_datetime(window["meta"][args.date],setting="vs")
                            tweetdate = time_functions.return_datetime(tweet["meta"][args.date],setting="vs")
                            extra = time_functions.timerel(windowdate,tweetdate,"day")
                            features_tweet[i] = feature + "_" + str(extra)
                if args.tt:
                    if timeinfo:
                        features.extend(features_tweet)
                else:
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
                event_instances[event].append({"features":features[:],"label":lab,"meta":window["meta"]})
            j+=args.step
    if args.median:
        return [event_instances, event_instances_loose]
    else:
        return [event_instances]

train_instances = read_events(args.i,depth)
if args.t:
    test_instances = read_events(args.t,deptht)

print "Starting classification..."
    
def classify(event_instances,train_events,test_events):
    if args.median:
        #generate feature_tte list
        print "generating feature_tte list"
        feature_tte = defaultdict(list)
        for ev in train_events:
            for tweet in event_instances[1][ev]:
                for feature in tweet["features"]:
                    if re.search(r"timex_",feature):
                        try:
                            feature_tte[feature].append(int(tweet["label"]))
                            # print "after","_".join(feature.split("_")[:-1])
                        except:
                            continue
        #calculate_median
        print "calculating median"
        feature_new = {}
        for feature in feature_tte.keys():
            if gen_functions.return_standard_deviation(feature_tte[feature]) < 2 and len(feature_tte[feature]) >= 2:
                feature_new[feature] = str(int(numpy.median(feature_tte[feature]))) + "_days"
                if args.median_out:
                    median_out.write(feature + "\t" + feature_new[feature] + "\n")
#               print feature,feature_tte[feature],feature_new[feature]
            else:
                feature_new[feature] = feature
        #convert features
        print "converting features"
        for ev in train_events:
            for instance in event_instances[0][ev]:
                new_features = []
                for r,feature in enumerate(instance["features"]):
                    if re.search(r"timex_",feature):
                        featureo = "_".join(feature.split("_")[:-1])
                        if not re.search(r"timex_",feature_new[featureo]):
                            extra_reg = int(feature.split("_")[-1])
                            new_feature = str(int(feature_new[featureo].split("_")[0]) + extra_reg) + "_days"
                            new_features.append(new_feature)
                    else:
                        new_features.append(feature)
                instance["features"] = new_features
        for ev in test_events:
            for instance in event_instances[0][ev]:
                new_features = []
                for r,feature in enumerate(instance["features"]):
                    if re.search(r"timex_",feature):
                        featureo = "_".join(feature.split("_")[:-1])
                        try:
                            if not re.search(r"timex_",feature_new[featureo]):
                                extra_reg = int(feature.split("_")[-1])
                                new_feature = str(int(feature_new[featureo].split("_")[0]) + extra_reg) + "_days"
                                new_features.append(new_feature)
#                                if re.search("ajaaz",ev):
#                                    print feature,new_feature
                        except:
                            continue
                    else:
                        new_features.append(feature)
                instance["features"] = new_features

    train = sum([event_instances[0][x] for x in train_events],[])
    test = []
    for event in test_events:
        print event
        testdict = {}
        eventparts = event.split("/") + [args.scaling]
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
        testdict["out"] = eventout
        testdict["instances"] = event_instances[0][event]
        test.append(testdict)
    if args.c == "median_baseline":
        for td in test:
            outfile = open(td["out"],"w")
            instances = td["instances"]
            for instance in instances:
                #extract day_estimations
                ests = []
                labelcount = defaultdict(int)
                for feature in instance["features"]:
                    if re.search(r"days",feature):
                       ests.append(feature)
                if len(ests) > 0:
                    for est in ests:
                        labelcount[est] += 1
                    topest = [e for e in sorted(labelcount, key=labelcount.get, reverse=True)][0]
                    num = re.search(r"(-?\d+)_days",topest).groups()[0]
                else:
                    num = "during"
#                if re.search("ajaaz",td["out"]):
  #                  if re.search("fall_11",td["out"]):
   #                     print instance["features"],num
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

if args.t:
#divide train and test events
    tr_events = train_instances[0].keys()
    te_events = test_instances[0].keys()
    if args.median:
        e_instances = [dict(train_instances[0].items() + test_instances[0].items()),dict(train_instances[1].items() + test_instances[1].items())]
    else:
        e_instances = [dict(train_instances[0].items() + test_instances[0].items())]
    classify(e_instances,tr_events,te_events)
else:
    events = train_instances[0].keys()
    testlen = int(len(events)/10)
    #make folds
    for i in range(0,len(events),testlen):
        try:
            tr_events = events[:i] + events[i+testlen:]
            te_events = [events[j] for j in range(i,i+testlen)]
        except IndexError:
            tr_events = events[:i]
            te_events = [events[j] for j in range(i,len(events))]
        classify(train_instances,tr_events,te_events)

