#! /usr/bin/env python

from collections import defaultdict
import sys
import codecs

outfile = sys.argv[1]
top_n = int(sys.argv[2])
infiles = sys.argv[3:]

feature_scores = defaultdict(list)

for infile in infiles:
    open_infile = codecs.open(infile,"r","utf-8") 
    for line in open_infile.readlines()[6:]:
        tokens = line.split("\t")
        feature = tokens[0]
        winnow = float(tokens[1])
        feature_scores[feature].append(winnow)
    open_infile.close()

outfile_open = codecs.open(outfile,"w","utf-8")
#rank
feature_rank = sorted([(x,str(sum(feature_scores[x]))) for x in feature_scores.keys()],key=lambda x: x[1], reverse=True)
for tokens in feature_rank[:top_n]:
    outfile_open.write(" ".join(tokens) + "\n")
outfile_open.close()
