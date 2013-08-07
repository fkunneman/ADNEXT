#!/usr/bin/env python

import argparse
import gen_functions
import codecs
from collections import defaultdict

parser = argparse.ArgumentParser(description = "Script to calculate the cosine similarity for a given set of text files")
parser.add_argument('-i', action = 'store', required = True, nargs='+', help = "the input files (with features divided by spaces")  

if len(args.i) < 2:
    print "less than the minimum of 2 files was inputted, aborting program..."
    exit()

vectors = defaultdict(list)
indexvector = []

# make file-vectors
for doc in args.i:
    name = doc.split("/")[-1]
    docread = codecs.open(doc,"r","utf-8")
    print len(docread.readlines())

    #vectors[name] =     

#fdaf
#feature_index dictionary
#for 