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
weights = defaultdict(float)
window_weights = []
for estimation in estimations_file.readlines()[args.s:]:
    tokens = estimation.strip().split(args.d)
    try:
        target = int(tokens[args.t])
        classification = int(tokens[args.c])
        dif = classification-target
        weights[target+dif] += 1
    except:
        weights[classification] += 1
    window_weights.append((target,weights.copy()))
estimations_file.close()
# return RMSE, responsiveness and prediction@
print window_weights

# es = evalset.Evalset()
# es.add_instances(event_estimations)
# rmse = es.calculate_rmse()
# rmses.append(rmse)
# outfile.write("\t".join([event,str(rmse[0]),str(rmse[1])]) + "\n")
# # write to file and keeplist  

# rmse_all,responsiveness_all = zip(*rmses)
# rmse_mean = str(sum(rmse_all) / len(rmse_all))
# responsiveness_mean = str(sum(responsiveness_all) / len(responsiveness_all))
# outfile.write("\t".join(["mean",rmse_mean,responsiveness_mean]) + "\n")
# outfile.close()
