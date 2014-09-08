#!/usr/bin/env python

import argparse
import codecs

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
    choices = ['arbiter','majority','weighted'], help = 'choose to apply voting over classifiers:' + 
        ' give the type of voting as shown in the options, and next list the classifiers over ' +
        'which voting is performed (choose from the listed classifiers in the \'c\'-argument)')

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
    cl = Classifier(tr,te,scaling=args.scaling,jobs=args.jobs)
    cl.balance_data()
    cl.count_feature_frequency()
    cl.prune_features_topfrequency(args.f)
    cl.index_features()
    if args.voting:
        cl.tenfold_train(args.voting[:-1],args.voting[-1],args.p)
    cl.model_necessities()
    if args.c == "svm":
        cl.train_svm(params=args.p)
    elif args.c == "nb":
        cl.train_nb()
    elif args.c == "tree":
        cl.train_decisiontree()
    elif args.c == "ripper":
        cl.train_ripper()
    cl.test_model()

trainfile = codecs.open(args.i,"r","utf-8")
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
        try:
            tr_folds = folds[:j] + folds[j+1:]
        except IndexError:
            tr_folds = folds[:j]
        traininstances = []
        for tr_fold in tr_folds:
            traininstances.extend(tr_fold)
        testinstances = [{"out" : args.o + "fold_" + str(j) + ".txt", "instances" : fold}]
        classify(traininstances,testinstances)
