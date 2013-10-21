#! /usr/bin/env python

"""Program to provide percentages of word groups given word categorizations in a tab-delimited txt-format 
    and a set of lcs-tweets"""

from __future__ import division 
import sys
import gen_functions
from collections import defaultdict

partsfile = sys.argv[1]
files_directory = sys.argv[2]
wordgroups = sys.argv[3]
outfile = open(sys.argv[4],"a")
hashtag = sys.argv[5]

print "generating feature sets"
#generate per-file featuresets
feature_sets = gen_functions.read_lcs_files(partsfile,files_directory)

print "generating feature_frequency hash"
#generate feature-frequency hash
feature_frequency = defaultdict(int)
for features in feature_sets:
    for feature in features:
	        feature_frequency[feature] += 1

print "counting shares"
#generate word-category pairs
word_cat = gen_functions.excel2columns(wordgroups)
top_features = word_cat.keys()

shares = defaultdict(int)
total = 0
for feature in feature_frequency.keys():
    frequency = feature_frequency[feature]
    total += frequency
    if feature in top_features:
        shares[word_cat[feature]] += frequency
    else: 
        shares["remainder"] += frequency

outfile.write("\npercentage for " + hashtag + ":\n")
for cat in shares.keys():
    outfile.write(cat + ":\t" + str(round(((shares[cat])/total)*100,2)) + "\n")

outfile.write("\n")
outfile.close()
