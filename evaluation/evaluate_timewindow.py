#!/usr/bin/env python

import argparse
from evalset import Evalset
from collections import defaultdict
import time_functions
import gen_functions

parser = argparse.ArgumentParser(description = "Program to evaluate the time-to-event of tweets with a slider")

parser.add_argument('-l', action = 'store', required = True, nargs='+', help = "the label / label+classification files (required)")
parser.add_argument('-m', action='store', required=True, nargs='+', help = "the files with meta-information")
parser.add_argument('-v', action='store', required = False, nargs='+', help = "[KNN] give vocabulary files to link indexes to features")
parser.add_argument('-o', action='store', required=True, help = "file to write the results to (required)")
parser.add_argument('-i', action = 'store', choices = ["lcs","ibt","knn"], help="specify the input type of label (and classification) files")
parser.add_argument('-e', action='store', required = True, help = "specify the file with event information")
parser.add_argument('-f', action='store', default = "all_to_one", help = "[WINDOW] filter of output (default = all-to-one")
parser.add_argument('--size', action='store', default = 24, help = "specify the window size (in hours)")
parser.add_argument('--slider', action='store', default = 1, help = "specify the slider (in hours)")
parser.add_argument('--plot', action='store', required = False,  help = "choose whether results are plotted")
parser.add_argument('--metadict',action='store',required=True,nargs='+', help = "if the fields of the metafile are different from the default, specify them here (format: name 0 id 1)")

args = parser.parse_args()

out = open(args.o,"w")
cols = defaultdict(list)

windowsize = int(args.size)
slider = int(args.slider)

if args.v:
    evaluation_seqs = [len(args.l),len(args.m),len(args.v)]
    print evaluation_seqs
else:
    evaluation_seqs = [len(args.l),len(args.m)]
if not max(evaluation_seqs) == min(evaluation_seqs):
    print "no equal amount of evaluation sequences, aborting program..."
    exit()

event_time = time_functions.generate_event_time_hash(args.e)

metadict = {}
i = 0
while i < len(args.metadict):
    metadict[args.metadict[i]] = int(args.metadict[i+1])
    i += 2

#for each evaluation set
for i,t in enumerate(args.l):
    print t
    #set instances
    evaluation = Evalset()
    evaluation.set_meta(args.m[i],metadict,args.i)
    if args.i == "knn":
        evaluation.set_instances_knn(args.l[i],hidden="before",vocabulary=args.v[i])
    elif args.i == "lcs":
        evaluation.set_instances_lcs(args.l[i],timelabels = True)
    elif args.i == "ibt":
        evaluation.set_instances_ibt(args.l[i])
    evaluation.extract_sliding_window_instances(windowsize,slider)
    
    for window in evaluation.windows:
        predictions = defaultdict(int)
        predictions_days = defaultdict(int)
        score_prediction = defaultdict(list)                
        #check for majority
        for instance in window.instances:
            try:
                if instance.time_classification[0] in ["early","during","after","nt"]:
                    predictions[instance.time_classification[0]] += 1
                else:
                    predictions["tte"] += 1
                    predictions_days[instance.time_classification[0]] += 1
                    score_prediction[instance.time_classification[1]].append(instance.time_classification[0])
            except AttributeError:
                predictions[instance.classification] += 1

        print predictions
        majority_rank = sorted(predictions,key = predictions.get,reverse=True)
        if majority_rank[0] == "tte" or predictions["tte"] == predictions[majority_rank[0]] or (args.i == "ibt" and "tte" in majority_rank):
            tte_rank = sorted(predictions_days,key=predictions_days.get,reverse=True)
            score_rank = sorted(score_prediction.keys(),reverse=True)
            estimation = evaluation.extract_timelabel(predictions_days,tte_rank,score_prediction,score_rank)
            window.set_classification(estimation[0])
        else:
            window.set_classification("abstain")

    event_results = []
    rmse = evaluation.calculate_rmse()
    if args.plot:
        plotfile = open("/".join(t.split("/")[:-1]) + "/" + args.plot,"w")
        for window in evaluation.windows:
            if hasattr(window, "error"):
                plotfile.write("\t".join([window.label,window.error]) + "\n")
        plotfile.close()
    event_results.extend(rmse[1:])
    out.write(" ".join([str(e) for e in rmse[1:]]))
    table = evaluation.return_results()
    for label in table[1:]:
        event_results.extend(label[1:4])
        out.write(" " + " ".join([str(e) for e in label[:4]]))
    for i,token in enumerate(event_results):
        cols[i].append(token)
    out.write("\n")

i = 0
while i < len(cols.keys()):
    aggregates = []
    for j in range(3):
        col = cols[i+j]
        mean = round(sum(col)/len(col),2)
        stdev = gen_functions.return_standard_deviation(col)
        aggregates.append(str(mean) + " (" + str(stdev) + ")")
    out.write("\t".join(aggregates) + "\n")
    i += 3

out.close()
