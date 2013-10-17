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

#generate per-file featuresets
#feature_sets = gen_functions.read_lcs_files(partsfile,files_directory)

#generate feature-frequency hash
#feature_frequency = defaultdict(int)
#for features in feature_sets:
#    for feature in features:
#	        feature_frequency[feature] += 1

#generate word groups
gen_functions.excel2columns(wordgroups)
