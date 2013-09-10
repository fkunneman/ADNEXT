#!/usr/bin/env python

import argparse
from evalset import Evalset
from collections import defaultdict
import time_functions


parser = argparse.ArgumentParser(description = "Program to evaluate the time-to-event of tweets with a slider")

parser.add_argument('-l', action = 'store', required = True, nargs='+', help = "the label / label+classification files (required)")
parser.add_argument('-c', action='store', required=False, nargs='+', help = "the classification files (if separated)")
parser.add_argument('-m', action='store', required=True, nargs='+', help = "the files with meta-information")
parser.add_argument('-v', action='store', required = False, nargs='+', help = "[KNN] give vocabulary files to link indexes to features")
parser.add_argument('-o', action='store', required=True, help = "file to write the results to (required)")
#parser.add_argument('--multi', action='store_true', help = "confirm when the meta-file contains instances for multiple testsets")
parser.add_argument('-i', action = 'store', choices = ["lcs","meta","knn"], help="specify the input type of label (and classification) files")
#parser.add_argument('-d', action='store', default = 1, help = "Define the depth of a distinct testset in terms of the path of scorefiles; [Default = 1]  (in the case of the testset \'bla\' and the paths \'bla/score1.txt\' and \'bla/score2.txt\', give two as the depth and the results for the different scorefiles are outputted in the same row)")
#parser.add_argument('--hidden', action='store', required = False, nargs = '+', help = "[KNN] if instances contain hidden classes to be retrieved in evaluation, specify their topclas(ses)")
parser.add_argument('-e', action='store', required = True, help = "specify the file with event information")
parser.add_argument('-f', action='store', default = "all_to_one", help = "[WINDOW] filter of output")
parser.add_argument('-et', action='store', default = "rmse", help = "specify the evaluation type")
parser.add_argument('--size', action='store', default = 24, help = "specify the window size (in hours)")
parser.add_argument('--slider', action='store', default = 1, help = "specify the slider (in hours)")
parser.add_argument('--threshold', action='store', default = 100, help = "specify the threshold after which to score")
parser.add_argument('--plot', action='store_true', help = "choose whether results are plotted")
parser.add_argument('--metadict',action='store',required=True,nargs='+', help = "if the fields of the metafile are different from the default, specify them here (format: filename 0 id 1)")

args = parser.parse_args()

if args.v:
    evaluation_seqs = [len(args.l),len(args.m),len(args.v)]
    print evaluation_seqs
else:
    evaluation_seqs = [len(args.l),len(args.m)]
if not max(evaluation_seqs) == min(evaluation_seqs):
    print "no equal amount of evaluation sequences, aborting program..."
    exit()

event_time = time_functions.generate_event_time_hash(eventfile)

metadict = {}
i = 0
while i < len(args.metadict):
    metadict[args.metadict[i]] = int(args.metadict[i+1])
    i += 2

#for each evaluation set
for i,t in enumerate(args.l):
    #set instances
    evaluation = Evalset(args.i)
    evaluation.set_meta(args.m[i],metadict)
    if args.i == "knn":
        evaluation.set_instances_knn(args.l[i],"before")
    if args.v:
        evaluation.set_vocabulary(args.v[i])
    windows = time_functions.extract_sliding_window_instances(evaluation.instances,windowsize,slider)


