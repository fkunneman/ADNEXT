#!/usr/bin/env python

import argparse
import codecs
from collections import defaultdict

parser = argparse.ArgumentParser(description = "Program to process sentences (divided by linebreaks) and count the frequency of feature categories")

parser.add_argument('-i', action = 'store', required = True, nargs='+', help = "the txt file to be processed and the column of the text")
parser.add_argument('-f', action = 'store', required = True, help = "the file with feature categories (txt; each feature in a separate column, divided by tabs)")
parser.add_argument('-m', action = 'store', required = True, nargs='+', help = "specify the names of the feature categories, in order of the columns; divided by spaces")

args = parser.parse_args()

feature_cat_frequencies = defaultdict(int)

# generate a dictionary with lists of feature categories
feature_cats_open = codecs.open(args.f,"read","utf-8") 
feature_cats = defaultdict(list)
for line in feature_cats_open.readlines():
    tokens = line.strip().split("\t")
    for i,feature in enumerate(tokens):
        feature_cats[i].append(feature)
feature_cats_open.close()
sorted_featurecats = sorted(feature_cats.keys())

text_file_open = codecs.open(args.i[0],"read","utf-8")
textcolumn = int(args.i[1])
for line in text_file_open.readlines():
    tokens = line.strip().split("\t")
    text = tokens[textcolumn]
    occurences = []
    for i in range(len(sorted_featurecats)):
        occurences.append(0)
    for word in text.split(" "):
        for featurecat in sorted_featurecats:
            if word in feature_cats[featurecat]:
                occurences[featurecat] = 1
    cat = ""
    for i,entry in enumerate(occurences):
        if entry:
            if cat == "":
                cat = args.m[i]
            else: 
                cat = cat + "&" + args.m[i]

    feature_cat_frequencies[cat] += 1

for t in feature_cat_frequencies:
    percentage = feature_cat_frequencies[t] / len(text_fiel_open.readlines())
    print t,percentage