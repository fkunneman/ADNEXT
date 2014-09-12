#!/usr/bin/env python

import argparse
import codecs
from collections import defaultdict
import re

from classifier import Classifier
import gen_functions

"""
Script to perform svm classification with scikit-learn. 
"""
parser = argparse.ArgumentParser(
    description = "Script to perform svm classification with scikit-learn.")
parser.add_argument('-i', action = 'store', required = True, 
    help = "file with either all instances or testinstances")
parser.add_argument('-t', action = 'store', required = False, 
    help = "file with test data (no testfile means ten-fold cross-validation is performed)")
parser.add_argument('-c', action = 'store', default = "svm", choices = ["svm","nb","tree"],
    help = "choose the classifier")
parser.add_argument('-f', action = 'store', type=int,default=10000, 
    help = "Prune features by taking the top f frequent features from the training data")
parser.add_argument('-p', action = 'store', type=int,default=10, 
    help = "decide on the number of parameter settings to compare during training (default = 10)")
parser.add_argument('-o', action = 'store', required=True, 
    help = "The output directory")
parser.add_argument('--jobs', action='store', type = int, default = 12, 
    help = 'specify the number of cores to use')
parser.add_argument('--scaling', action='store', default = "binary", 
    choices = ["binary","log","tfidf"], help = 'specify the type of feature scaling')
parser.add_argument('--voting', action='store', required = False, nargs='+', 
    help = 'choose to apply voting over classifiers: first give the type of voting ' +
        '(arbiter,majority or weighted) and next list the classifiers over which ' +
        'voting is performed (choose from the listed classifiers in the \'c\'-argument)')
parser.add_argument('--append', action = 'store', required=False, 
    help = "to append classifier output for voting, specify the filename of standard output of " +
        "the classifier")

args = parser.parse_args() 

expdir = "/".join(args.i.split("/")[:-1]) + "/"

def make_instances(lines,appendlines=False):
    instances = []
    for i,line in enumerate(lines):
        tokens = line.strip().split("\t")
        instance = {}
        instance["label"] = tokens[1]
        instance["meta"] = tokens[:-1]
        instance["features"] = tokens[-1].split()
        if appendlines:
            #check if file is same
            info = appendlines[i].strip().split("\t")[1].split()
            label = info[0]
            classification = info[1]
            if label != tokens[1]:
                print "labels of appendfile do not align, exiting program"
            instance["append"] = int(float(classification))
        instances.append(instance)
    return instances

def classify(tr,te):
    cl = Classifier(tr,te,scaling=args.scaling,jobs=args.jobs)
    cl.balance_data()
    cl.count_feature_frequency()
    cl.prune_features_topfrequency(args.f)
    cl.index_features()
    if args.voting:
        cl.model_necessities()
        c = args.voting[1:]
        index_predictions = defaultdict(lambda : defaultdict(lambda : {}))
        featurenames = []
        if "svm" in c:
            cl.train_svm(params=args.p)
            predictions = cl.return_classification_features()
            for i,ts in enumerate(predictions):
                for j,p in enumerate(ts):
                    index_predictions[i][j]["___svm"] = p
            featurenames.append("___svm")
        if "nb" in c:
            cl.train_nb()
            predictions = cl.return_classification_features()
            for i,ts in enumerate(predictions):
                for j,p in enumerate(ts):
                    index_predictions[i][j]["___nb"] = p
            featurenames.append("___nb")
        if "tree" in c:
            cl.train_decisiontree()
            predictions = cl.return_classification_features()
            for i,ts in enumerate(predictions):
                for j,p in enumerate(ts):
                    index_predictions[i][j]["___tree"] = p
            featurenames.append("___tree")
        if args.voting[0] != "majority":
            cl.tenfold_train(args.voting[0],classifiers = c,p = args.p)
        cl.add_classification_features(index_predictions,featurenames,args.voting[0])
    if args.append:
        cl.append_classifier_labelings()
    if args.voting[0] == "majority":
        for tset in cl.test:
            outfile = codecs.open(tset["out"],"w","utf-8")
            for instance in tset["instances"]:
                if instance["sparse"].values().count(1) >= 2:
                    prediction = "1.0"
                else:
                    prediction = "0.0"
                instanceout = [" ".join([x for x in instance["features"] if not re.search("_",x)]), \
                    instance["label"] + " " + prediction, " ".join([str(instance["sparse"][x]) for \
                    x in sorted(instance["sparse"].keys())]), \
                    str(instance["sparse"].values().count(1))]
                outfile.write("\t".join(instanceout) + "\n") 
            outfile.close()
    else:
        cl.model_necessities()
        if args.c == "ripper":
            trainfile = open(args.tmp + "train.arrf","w")
            for i,v in enumerate(cl.training):
                trainfile.write("{")
                for x in sorted(v["sparse"].keys()):
                    trainfile.write(str(x) + " " + str(v["sparse"][x]) + ", ")
                trainfile.write(str(len(cl.feature_info.keys())) + " \"" + str(cl.trainlabels_raw[i]) + "\"}\n")
            trainfile.close()
            testfile = open(args.tmp + "test.arrf","w")
            for tset in cl.test:
                testfile = open(args.tmp + "test.arrf","w")
                for i,v in enumerate(tset["instances"]):
                    testfile.write("{")
                    for x in sorted(v["sparse"].keys()):
                        testfile.write(str(x) + " " + str(v["sparse"][x]) + ", ")
                    testfile.write(str(len(cl.feature_info.keys())) + " \"" + str(cl.trainlabels_raw[i]) + "\"}\n")
            quit()

        else:
            if args.c == "svm":
                cl.train_svm(params=args.p)
            elif args.c == "nb":
                cl.train_nb()
            elif args.c == "tree":
                cl.train_decisiontree()
            cl.test_model()

trainfile = codecs.open(args.i,"r","utf-8")
if args.append:
    appendfile = codecs.open(args.append,"r","utf-8")
    trainlines = trainfile.readlines()
    appendlines = appendfile.readlines()
    if not len(appendlines) == len(trainlines):
        print "uneven lines appendfile and trainfile; exiting program." 
        quit()
    train = make_instances(trainlines,appendlines)
    appendfile.close()
else:
    train = make_instances(trainfile.readlines())
trainfile.close()

if args.t:
    testfile = codecs.open(args.t,"r","utf-8")
    test = [{"out" : args.o + "testout.txt", "instances" : make_instances(testfile.readlines())}]
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
        testinstances = [{"out" : args.o + "fold_" + str(j) + ".txt", "instances" : fold}]
        classify(traininstances,testinstances)
