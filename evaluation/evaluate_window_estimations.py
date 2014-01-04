#!/usr/bin/env python

import argparse
import evalset
import re
from collections import defaultdict
import gen_functions

parser = argparse.ArgumentParser(description = "Program to score window estimations")

parser.add_argument('-i', action = 'store', required = True, nargs='+', help = "the files with estimations")
parser.add_argument('-r', action='store', required=True, help = "the file to write results to")
parser.add_argument('-p', action='store', required=False, help = "[OPTIONAL] the file to write error plot coordinates to")
parser.add_argument('-t', action='store', type = int, default = 0, help = "the target column")
parser.add_argument('-c', action='store', type = int, default = 1, help = "the estimation column")
parser.add_argument('-s', action='store', type = int, default = 0, help = "specify the first line of classification files to process from [DEFAULT = 0]")
parser.add_argument('-d', action = 'store', default = "\t", help="specify the delimiter of target and estimator columns [DEFAULT = \'\\t\']")
parser.add_argument('--depth', action='store', default=1, type=int, help="specify the depth of file characterizations; [DEFAULT = 1]")

args = parser.parse_args()

depth = args.depth * -1
outfile = open(args.r,"w")
outfile.write("\n\n")
rmses = []
plotvals = defaultdict(list)
# for each file
for ef in args.i:
    # extract event + windowname
    event_txt = "/".join(ef.split("/")[depth:])
    event = re.sub(".txt","",event_txt)
    # generate target-evaluation list 
    estimations_file = open(ef)
    event_estimations = []
    for estimation in estimations_file.readlines()[args.s:]:
        tokens = estimation.strip().split(args.d)
        target = tokens[args.t]
        classification = tokens[args.c]
        event_estimations.append((target,classification))
    estimations_file.close()
    # return RMSE, responsiveness and prediction@
    es = evalset.Evalset()
    es.add_instances(event_estimations)
    rmse = es.calculate_rmse()
    rmses.append(rmse[:2])
    outfile.write("\t".join([event,str(rmse[0]),str(rmse[1])]) + "\n")
    if args.p:
        for pv in rmse[2]:
            plotvals[pv[0]].append(pv[1])
    # write to file and keeplist  

rmse_all,responsiveness_all = zip(*rmses)
rmse_mean = str(sum(rmse_all) / len(rmse_all))
rmse_stdef = gen_functions.return_standard_deviation(rmse_all)
responsiveness_mean = str(sum(responsiveness_all) / len(responsiveness_all))
outfile.write("\t".join(["mean",rmse_mean,rmse_stdef,responsiveness_mean]) + "\n")
outfile.close()
if args.p:
    plotfile = open(args.p,"w")
    mean_plotvals = [(v,(sum(plotvals[v]) / len(plotvals[v]))) for v in sorted(plotvals.keys())]
    for mp in mean_plotvals:
        plotfile.write(str(mp[0]) + "\t" + str(mp[1]) + "\n")
    plotfile.close()
