#!/usr/bin/env python

import argparse
import re
from collections import defaultdict

import evalset
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
accuracies = []
plotvals = defaultdict(list)
# for each file
for ef in args.i:
    print ef
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
    rmses.append(rmse[:-1])
    accuracy = es.calculate_accuracy()
#    print ef,accuracy
    accuracies.append(accuracy)
    outfile.write("\t".join([event] + [str(x) for x in rmse[:-1]] + [str(accuracy)]) + "\n")
    if args.p:
        for pv in rmse[-1]:
            plotvals[pv[0]].append(pv[1])
    # write to file and keeplist  

rmse_all,mae_all,first_all,before_all,responsiveness_all = zip(*rmses)
rmse_mean = str(round(sum(rmse_all) / len(rmse_all),2))
rmse_stdef = str(gen_functions.return_standard_deviation(rmse_all))
mae_mean = str(round((sum(mae_all) / len(mae_all)),2))
mae_stdef = str(gen_functions.return_standard_deviation(mae_all))
try:
    first_mean = str(round(sum(first_all) / len(first_all),2))
    first_stdef = str(gen_functions.return_standard_deviation(first_all))
except:
    first_mean = 'x'
    first_stdef = 'x'
before_mean = str(round(sum(before_all) / len(before_all),2))
before_stdef = str(gen_functions.return_standard_deviation(before_all))
responsiveness_mean = str(round(sum(responsiveness_all) / len(responsiveness_all),2))
accuracy_mean = str(round((sum(accuracies) / len(accuracies)),2))
accuracy_stdev = str(gen_functions.return_standard_deviation(accuracies))
outfile.write("\t".join(["mean",rmse_mean + "(" + rmse_stdef + ")",mae_mean + "(" + mae_stdef + ")",first_mean + "(" + first_stdef + ")",before_mean + "(" + before_stdef + ")",responsiveness_mean,accuracy_mean + "(" + accuracy_stdev + ")"]) + "\n")
outfile.close()
if args.p:
    plotfile = open(args.p,"w")
    mean_plotvals = [(v,(sum(plotvals[v]) / len(plotvals[v]))) for v in sorted(plotvals.keys())]
    for mp in mean_plotvals:
        plotfile.write(str(mp[0]) + "\t" + str(mp[1]) + "\n")
    plotfile.close()
