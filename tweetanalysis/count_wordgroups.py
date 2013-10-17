#! /usr/bin/env python

"""Program to provide percentages of word groups given word categorizations in a tab-delimited txt-format 
    and a set of lcs-tweets"""

import sys
import gen_functions
from collections import defaultdict

partsfile = sys.argv[1]
files_directory = sys.argv[2]
wordgroups = sys.argv[3]
outfile = open(sys.argv[4],"a")
hashtag = sys.argv[5]

#generate per-file featuresets
feature_sets = gen_functions.read_lcs_files(partsfile,files_directory)

#generate feature-frequency hash
feature_frequency = defaultdict(int)
for features in feature_sets:
    for feature in features:
	        feature_frequency[feature] += 1

#generate word-category pairs
word_cat = gen_functions.excel2columns(wordgroups)
top_features = word_cat.keys()

shares = defaultdict(int)
total = 0
for feature in feature_frequency.keys():
    frequency = feature_frequency[feature]
    if feature in top_features:
        shares[word_cat[feature]] += frequency
    else: 
        shares["remainder"] += frequency
    total += frequency

outfile.write("\npercentage for " + hashtag + ":\n")
for cat in shares.keys():
    outfile.write(cat + ":\t" + str(shares[cat]))

outfile.write("\n")
outfile.close()
