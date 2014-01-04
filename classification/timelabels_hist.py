#!/usr/bin/env python

import argparse
from collections import defaultdict

parser = argparse.ArgumentParser(description = "Program to add historic knowledge to time-to-event estimations")

parser.add_argument('-i', action = 'store', required = True, help = "the files with estimations")
parser.add_argument('-r', action='store', required=True, help = "the file to write new estimations to")
parser.add_argument('-t', action='store', type = int, default = 0, help = "the target column")
parser.add_argument('-c', action='store', type = int, default = 1, help = "the estimation column")
parser.add_argument('-s', action='store', type = int, default = 0, help = "specify the first line of classification files to process from [DEFAULT = 0]")
parser.add_argument('-d', action = 'store', default = "\t", help="specify the delimiter of target and estimator columns [DEFAULT = \'\\t\']")

args = parser.parse_args()

outfile = open(args.r,"w")

estimations_file = open(args.i)
weights = defaultdict(int)
window_weights = []
for estimation in estimations_file.readlines()[args.s:]:
    tokens = estimation.strip().split(args.d)
    classification = tokens[args.c]
    target = tokens[args.t]
    try:
        weights[int(classification)-int(target)] += 1
    except:
        weights[classification] += 1
    window_weights.append((target,classification,weights.copy()))
estimations_file.close()
during = False
for ww in window_weights:
    t = ww[0]
    if t == "during" or t == "after":
        during = True
    c = ww[1]
    if during:
        outfile.write(t + "\t" + c + "\n")
    else:
        d = ww[2]
        topest = [e for e in sorted(d, key=d.get, reverse=True)][0]
        try:
            est = int(t) + topest
        except:
            est = topest
        outfile.write(t + "\t" + str(est) + "\n")
outfile.close() 
