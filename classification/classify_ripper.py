#!/usr/bin/env python

import argparse
import codecs
import re
import os
from collections import defaultdict

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
convert = {".":"punctuation_dot",":":"punctuation_colon",";":"punctuation_semicolon","?":"punctuation_qm","\'":"punctuation_apostrophe"}
convertables = convert.keys()
c = ["___svm","___nb","___append"]
trainfile = codecs.open("rip.data","w","utf-8")
testfile = codecs.open("rip.test","w","utf-8")
vocabulary = codecs.open("rip.names","w","utf-8")
classes = []
attributes = []
infile = codecs.open(args.i,"r","utf-8")
instances = []
for line in infile.readlines():
    instance = {}
    tokens = line.strip().split()
    if len(tokens) > 1:
        label = tokens[0].replace("1.0","pos").replace("0.0","neg")
        classes.append(label)
        instance["label"] = label
        features = tokens[1].replace(",,,",",punctuation_comma,").replace("_,,","_punctuation_comma,").replace(",,_",",punctuation_comma_").split(",")
        bow = [x for x in features if not x in c]
        cs = [x for x in features if x in c]
        if len(bow) > 0:
            if "WORDS" not in [x[0] for x in attributes]:
                attributes.append(("WORDS",["bag"]))
            for i,word in enumerate(bow):
                if word in convertables:
                    word = convert[word]
                if re.search(r"\.",word):
                    word = word.replace(".","punctuation_dot")
                if re.search(r"\?",word):
                    word = word.replace("?","punctuation_qm")
                if re.search(r"\:",word):
                    word = word.replace(":","punctuation_colon")
                if re.search(r"\;",word):
                    word = word.replace(";","punctuation_semicolon")
                if re.search(r"\'",word):
                    word = word.replace("'","punctuation_apostrophe")
                bow[i] = "\'" + word + "\'"
            instance["bow"] = bow
        for classifier in cs:
            if classifier not in [x[0] for x in features]:
                attributes.append((classifier,["1","0"]))
        instance["classifiers"] = cs
        instances.append(instance)
classifiers = [x for x in attributes if x[0] != "WORDS"]
if len(classifiers) > 0:
    classi = True
else:
    classi = False
for instance in instances:
    if instance["bow"]:
        trainfile.write(" ".join(instance["bow"]) + ",")
    if classi:
        for x in classifiers:
            if x in instance["classifiers"]:
                trainfile.write("1,")
            else:
                trainfile.write("0,")
    trainfile.write(instance["label"] + ".\n")
infile.close()
trainfile.close()
vocabulary.write(",".join(list(set(classes))) + ".\n" + "\n".join(["\t".join([x[0] + ":",",".join(x[1])]) + "." for x in attributes]))
vocabulary.close()
testdata = codecs.open(args.t,"r","utf-8")
for line in testdata.readlines():
    tokens = line.strip().split()
    label = tokens[0].replace("1.0","pos").replace("0.0","neg")
    features = tokens[1].replace(",,,",",punctuation_comma,").replace("_,,","_punctuation_comma,").replace(",,_",",punctuation_comma_").split(",")
    bow = [x for x in features if not x in c]
    cs = [x for x in features if x in c]
    if len(bow) > 0:
        for i,word in enumerate(bow):
            if word in convertables:
                words = convert[word]
            if re.search(r"\.",word):
                word = word.replace(".","punctuation_dot")
            if re.search(r"\?",word):
                word = word.replace("?","punctuation_qm")
            if re.search(r"\:",word):
                word = word.replace(":","punctuation_colon")
            if re.search(r"\;",word):
                word = word.replace(";","punctuation_semicolon")
            if re.search(r"\'",word):
                word = word.replace("'","punctuation_apostrophe")
            bow[i] = "\'" + word + "\'"
        testfile.write(" ".join(bow) + ",")
    if classi:
        for x in classifiers:
            if x in cs:
                testfile.write("1,")
            else:
                testfile.write("0,")
    testfile.write(label + ".\n")
testfile.close()
quit()

#perform classification
#os.system("ripper ")
