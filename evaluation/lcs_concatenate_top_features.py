#! /usr/bin/env python

import defaultdict
import sys
import codecs

outfile = sys.argv[1]
infiles = sys.argv[2:]

feature_scores = defaultdict(list)

for infile in infiles:
    open_infile = codecs.open(infile,"r","utf-8") 
    for line in open_infile.readlines()[6:]
        tokens = line.split("\t")
        feature = tokens[0]
        winnow = tokens[1]
        feature_scores[feature].append(winnow)

#rank
feature_rank = sorted([(x,sum(feature_scores[x])) for x in feature_scores.keys()],key=lambda x: x[1])
print feature_rank[:100]