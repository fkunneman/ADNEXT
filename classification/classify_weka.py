#!/usr/bin/env python

import argparse
import codecs
from collections import defaultdict
import re
import os

from classifier import Classifier
import classify_sklearn
import weka_classifier
import gen_functions

"""
Script to perform classification with weka. 
"""
parser = argparse.ArgumentParser(
    description = "Script to perform classification with weka.")
parser.add_argument('-i', action = 'store', required = True, 
    help = "file with either all instances or testinstances")
parser.add_argument('-t', action = 'store', required = False, 
    help = "file with test data (no testfile means ten-fold cross-validation is performed)")
parser.add_argument('-c', action = 'store', default = "ripper", choices = ["ripper"],
    help = "choose the classifier")
parser.add_argument('-f', action = 'store', type=int,default=10000, 
    help = "Prune features by taking the top f frequent features from the training data")
parser.add_argument('-o', action = 'store', required=True, 
    help = "The output directory")
parser.add_argument('--scaling', action='store', default = "binary", 
    choices = ["binary","log","tfidf"], help = 'specify the type of feature scaling')
parser.add_argument('--balance', action = 'store_true', 
    help = "choose to balance the instances per class")

args = parser.parse_args() 

def classify(tr,te):
    cl = Classifier(tr,te,scaling=args.scaling)
    if args.balance:
        cl.balance_data()
    cl.count_feature_frequency()
    cl.prune_features_topfrequency(args.f)
    cl.index_features()
    #generate trainfile
    tr = "train.arrf"
    trainfile = codecs.open(tr,"w","utf-8")
    trainfile.write("@RELATION sparse.data\n\n")
    for f in cl.features:
        trainfile.write("@ATTRIBUTE \"" + 
            f.replace("\\","\\\\").replace('\"', '\\\"') + "\" numeric\n")
    trainfile.write("\n@ATTRIBUTE class {1.0, 0.0}\n\n@DATA\n")
    for i,v in enumerate(cl.training):
        trainfile.write("{")
        for x in sorted(v["sparse"].keys()):
            if not v["sparse"][x] == 0:
                trainfile.write(str(x) + " " + str(v["sparse"][x]) + ",")
        trainfile.write(str(len(cl.feature_info.keys())) + " \"" + str(cl.trainlabels_raw[i]) + "\"}\n")
    trainfile.close()
    print "training ripper classifier"
    wcl = weka_classifier.Classifier()
    model = wcl.train("ripper",tr)            
    #generate testfile
    for tset in cl.test:
        outfile = codecs.open(tset["out"] + "predictions.txt","w","utf-8")
        outfile.write(model)
        te = "test.arrf"
        testfile = codecs.open(te,"w","utf-8")
        testfile.write("@RELATION sparse.data\n\n")
        for f in cl.features:
            testfile.write("@ATTRIBUTE \"" + \
                f.replace("\\","\\\\").replace('\"', '\\\"') + "\" numeric\n")
        testfile.write("\n@ATTRIBUTE class {1.0, 0.0}\n\n@DATA\n")
        for i,v in enumerate(tset["instances"]):
            testfile.write("{")
            for x in sorted(v["sparse"].keys()):
                if not v["sparse"][x] == 0:
                    testfile.write(str(x) + " " + str(v["sparse"][x]) + ",")
            testfile.write(str(len(cl.feature_info.keys())) + " \"" + str(cl.trainlabels_raw[i]) + "\"}\n")
        testfile.close()
        print "done. testing"
        predictions = wcl.test(te)
        instances = tset["instances"]
        if len(predictions) == len(instances):
            for i,pr in enumerate(predictions):
                outfile.write("\t".join([" ".join([x for x in instances[i]["features"] if not re.search("_",x)]), 
                instances[i]["label"] + " " + str(predictions[i][0]), 
                predictions[i][1]]) + "\n")
            outfile.close()
        else:
            print "number of ripper predictions and instances do not align, exiting program"
            quit()
        os.system("mv " + te + " " + tset["out"])
        os.system("mv " + tr + " " + tset["out"])
    wcl.stop() 

trainfile = codecs.open(args.i,"r","utf-8")
train = classify_sklearn.make_instances(trainfile.readlines())
trainfile.close()
if args.t:
    testfile = codecs.open(args.t,"r","utf-8")
    test = [{"out" : args.o + "testout.txt", "instances" : classify_sklearn.make_instances(testfile.readlines())}]
    testfile.close()
    classify(train,test)
else:
    folds = gen_functions.make_folds(train)
    for j,fold in enumerate(folds):
        print "fold",j
        try:
            tr_folds = folds[:j] + folds[j+1:]
        except IndexError:
            tr_folds = folds[:j]
        traininstances = []
        for tr_fold in tr_folds:
            traininstances.extend(tr_fold)
        outdir = args.o + "fold_" + str(j) + "/"
        os.mkdir(outdir)
        testinstances = [{"out" : outdir, "instances" : fold}]
        classify(traininstances,testinstances)
