#!/usr/bin/env python

import argparse
import codecs

from classifier import Classifier
import gen_functions

"""
Script to perform svm classification with scikit-learn. 
"""
parser = argparse.ArgumentParser(description = "Script to perform svm classification with scikit-learn.")
parser.add_argument('-i', action = 'store', required = True, 
    help = "file with either all instances or testinstances")
parser.add_argument('-t', action = 'store', required = False, 
    help = "file with test data (no testfile means ten-fold cross-validation is performed)")
parser.add_argument('-p', action = 'store', type=int,default=10, 
    help = "decide on the number of parameter settings to compare during training (default = 10)")
parser.add_argument('-o', action = 'store', required=True, 
    help = "The output file")
parser.add_argument('--jobs', action='store', type = int, default = 12, help = 'specify the number of cores to use')

#parser.add_argument('--learning_curve', action = 'store_true', 
#    help = "choose to classify by learning curve")

args = parser.parse_args() 

expdir = "/".join(args.i.split("/")[:-1]) + "/"

def make_instances(lines):
    instances = []
    for line in lines:
        tokens = line.strip().split("\t")
        instance = {}
        instance["label"] = tokens[1]
        instance["meta"] = tokens[:-1]
        instance["features"] = tokens[-1].split()
        instances.append(instance)
    return instances

def classify(tr,te):
    cl = Classifier(tr,te,jobs=args.jobs)
    cl.balance_data()
    cl.count_feature_frequency()
    cl.prune_features_topfrequency(args.f)
    cl.index_features()
    cl.classify_svm(params=args.p)

trainfile = codecs.open(args.i,"r","utf-8")
trainfile.close()
train = make_instances(trainfile.readlines())
if args.t:
    testfile = codecs.open(args.t,"r","utf-8")
    test = [{"out" : args.o, "instances" : make_instances(testfile.readlines())}]
    testfile.close()
    classify(train,test)
else:
    folds = gen_functions.make_folds(train)
    for j,fold in enumerate(folds):
        try:
            tr_folds = folds[:j] + folds[j+1:]
        except IndexError:
            tr_folds = folds[:j]
        traininstances = []
        for tr_fold in tr_folds:
            traininstances.extend(tr_fold)
        testinstances = [{"out" : args.o, "instances" : fold}]
        classify(traininstances,testinstances)

