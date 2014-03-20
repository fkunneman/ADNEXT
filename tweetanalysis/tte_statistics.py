#!/usr/bin/env python

from __future__ import division

from collections import defaultdict
import sys
import re

import gen_functions

outfile = open(sys.argv[1],"w")
infiles = sys.argv[2:]

#for each combination
score_dict = defaultdict(list)
for infile in infiles:
    name = infile.split("/")[-2:]
    l = name[0]
    print name
    xpre = re.search(r"(\d+_\d+)_hist\.txt",name[1])
#    print name
    x = xpre.groups()[0]
    fileread = open(infile)
    mean_values = fileread.readlines()[-1]
    fileread.close()
    tokens = mean_values.strip().split("\t")
#    print name,tokens
    mae = float(tokens[2].split("(")[0])
    rmse = float(tokens[1].split("(")[0])
    acc = float(tokens[6].split("(")[0])
    score_dict[x].append(mae)

for setting in score_dict.keys():
    setting_scores = score_dict[setting]
    mean = sum(setting_scores) / len(setting_scores)
    st_dev = gen_functions.return_standard_deviation(setting_scores)
    outfile.write(setting + "\t" + str(mean) + " (" + str(st_dev) + ")\n")
outfile.close()