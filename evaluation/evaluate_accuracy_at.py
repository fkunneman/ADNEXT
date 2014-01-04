#!/usr/bin/env python

import argparse
import evalset
import re
from collections import defaultdict

parser = argparse.ArgumentParser(description = "Program to score window estimations")

parser.add_argument('-i', action = 'store', required = True, nargs='+', help = "the files with estimations")
parser.add_argument('-r', action='store', required=True, help = "the file to write results to")
parser.add_argument('-t', action='store', type = int, default = 0, help = "the target column")
parser.add_argument('-c', action='store', type = int, default = 1, help = "the estimation column")
parser.add_argument('-o', action='store', type = int, required=False, help = "[OPTIONAL] the score column")
parser.add_argument('-a', action='store', choices = ["estimation","threshold"], help = "the domain of the stop condition (estimation or threshold)")
parser.add_argument('-v', action='store', type = int, nargs='+', required = True, help = "the value(s) at which to stop")
parser.add_argument('-s', action='store', type = int, default = 0, help = "specify the first line of classification files to process from [DEFAULT = 0]")
parser.add_argument('-d', action = 'store', default = "\t", help="specify the delimiter of target and estimator columns [DEFAULT = \'\\t\']")
parser.add_argument('--depth', action='store', default=1, type=int, help="specify the depth of file characterizations; [DEFAULT = 1]")

args = parser.parse_args()

depth = args.depth * -1
outfile = open(args.r,"w")
outfile.write(args.a + "\n")
aats = defaultdict(list)
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
        if args.o:
            score = tokens[args.o]
            event_estimations.append((target,estimation,score))
        else:
            event_estimations.append((target,classification))
    estimations_file.close()
    # return RMSE, responsiveness and prediction@
    es = evalset.Evalset()
    es.add_instances(event_estimations)
    outfile.write(event + "\n\t")
    for v in args.v:
        aat = es.accuracy_at(v,args.a)
        aats[v].append(aat)
        outfile.write(" ".join([str(v),str(aat[0]),str(aat[1]),str(aat[2])]) + "\t") 
    outfile.write("\n")

outfile.write("\nMeans:\n")
for v in args.v:
    outfile.write("scores for prediction at " + args.a + " " + str(v) + "\n")
    timeat_all,prediction_all,dif_all = zip(*aats[v])
    timeat_mean = str(sum(timeat_all) / len(timeat_all))
    prediction_mean = str(sum(prediction_all) / len(prediction_all))
    dif_mean = str(sum(dif_all) / len(dif_all))
    outfile.write(" ".join([str(v),str(timeat_mean),str(prediction_mean),str(dif_mean)]) + "\n")
outfile.close()
