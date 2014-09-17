#!/usr/bin/env python

import argparse
import codecs
import re
import os

"""
Script to perform classification with ripper. 
"""
parser = argparse.ArgumentParser(
    description = "Script to perform classification with ripper.")
parser.add_argument('-i', action = 'store', required = True, 
    help = "file with traindata")
parser.add_argument('-t', action = 'store', required = False, 
    help = "file with test data")
parser.add_argument('-o', action = 'store', required=True, 
    help = "The output directory")

args = parser.parse_args() 

#generate ripper-formatted train and testfiles, and a vocabulary
trainfile = codecs.open("ripper.data","w","utf-8")
testfile = codecs.open("ripper.test","w","utf-8")
vocabulary = codecs.open("ripper.names","w","utf-8")
classes = []
attributes = []
infile = codecs.open(args.i,"r","utf-8")
for line in infile.readlines():
    tokens = line.strip().split()
    label = tokens[0]
    classes.append(label)
    features = tokens[1]
    bow = [x for x in features if not re.search("___",x)]
    classifiers = [x for x in features if re.search("___",x)]
    if len(bow) > 0:
        if "WORDS" not in [x[0] for x in features]:
            attributes.append(("WORDS",["bag"]))
        for i,word in enumerate(bow):
            bow[i] = "\'" + word + "\'"
        trainfile.write(" ".join(bow) + ",")
    for classifier in classifiers:
        if classifier not in [x[0] for x in features]:
            attributes.append((classifier,["1","0"])) 
    trainfile.write(",".join(classifiers) + "," + label + "\n")
infile.close()
trainfile.close()
vocabulary.write(",".join(list(set(classes))) + "\.\n\n" + "\n".join(["\t".join(x[0],",".join(x[1])) for x in attributes]))
vocabulary.close()
testdata = codecs.open(args.t,"r","utf-8")
for line in testdata.readlines():
    tokens = line.strip().split()
    label = tokens[0]
    features = tokens[1]
    bow = [x for x in features if not re.search("___",x)]
    classifiers = [x for x in features if re.search("___",x)]
    if len(bow) > 0:
        for i,word in enumerate(bow):
            bow[i] = "\'" + word + "\'"
        testfile.write(" ".join(bow) + ",")
    testfile.write(",".join(classifiers) + "," + label + "\n")
testfile.close()
quit()

#perform classification
#os.system("ripper ")
