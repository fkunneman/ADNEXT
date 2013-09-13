#!/usr/bin/env python

import argparse
import gen_functions
import codecs
from collections import defaultdict

parser = argparse.ArgumentParser(description = "Script to calculate the cosine similarity for a given set of text files")
parser.add_argument('-i', action = 'store', required = True, nargs='+', help = "the input files (with features divided by spaces")  
args = parser.parse_args()


if len(args.i) < 2:
    print "less than the minimum of 2 files was inputted, aborting program..."
    exit()

feature_freqs = defaultdict(lambda : defaultdict(int))
vectors = defaultdict(list)
indexvector = []

# make file-vectors
print "extracting feature frequencies..."
for doc in args.i:
    name = doc.split("/")[-1]
    docread = codecs.open(doc,"r","utf-8")
    terms = docread.read().split(" ")
    indexvector.extend(terms)
    feature_freq = defaultdict(int)
    for term in terms:
        feature_freq[term] += 1
    feature_freqs[name] = feature_freq
    docread.close()

# make feature-index dictionary
print "making feature-index dictionary..."
feature_index = {}
unique_features = list(set(indexvector))     
for i,feature in enumerate(unique_features):
    feature_index[feature] = i

# making vectors
print "making vectors..."
for docname in feature_freqs.keys():
    feature_freq = feature_freqs[docname]
    vector = [0] * len(feature_index.keys())
    for feature in feature_freq.keys():
        frequency = feature_freq[feature]
        index = feature_index[feature]
        vector[index] = frequency
    vectors[docname] = vector

print "scoring similarities..."
docnames = vectors.keys()
for i,docname in enumerate(docnames):
    vector1 = vectors[docname]
    for j in docnames[i+1:]:
        vector2 = vectors[j]
        print "cosine similarity",docname,"-",j,":",gen_functions.calculate_cosine_similarity(vector1,vector2)

