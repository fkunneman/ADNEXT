#!/usr/bin/env python

import argparse
from evalset import Evalset
from collections import defaultdict

"""
"""
parser = argparse.ArgumentParser(description = "Program to process a file containing tweets with Frog en write output")

parser.add_argument('-l', action = 'store', required = True, nargs='+', help = "the label / label+classification files")
parser.add_argument('-c', action='store', required=False, nargs='+', help = "the classification files (if separated)")
parser.add_argument('-o', action='store', required=True, help = "file to write the results to")
parser.add_argument('-f', action='store', required=False, nargs = '+', choices = ["all_to_one","inner_domain","outer_domain"], help = "[WINDOW] filter of output")
parser.add_argument('-m', action='store', required=False, help = "meta-file")
parser.add_argument('--multi', action='store_true', help = "confirm when the meta-file contains instances for multiple testsets")
parser.add_argument('-i', action = 'store', choices = ["lcs","meta","knn"], help="specify the input type of label (and classification) files")
#parser.add_argument('-e', action='store', required=False, nargs='+', help = "eventfiles (needed to calculate the time to event for sorting tweets in time)")
parser.add_argument('-fp', action='store_true', help = "choose whether a ranked list of the most confident false positive instances is written to a file")
parser.add_argument('-w', action='store', required = False, nargs = '+', help = "to classify in time windows,specify the window size, slider (in terms of hours) and threshold after which to score; this option presumes a metafile with time-from-zero values")
parser.add_argument('-d', action='store', default = 1, help = "Define the depth of a distinct testset in terms of the path of scorefiles; [Default = 1]  (in the case of the testset \'bla\' and the paths \'bla/score1.txt\' and \'bla/score2.txt\', give two as the depth and the results for the different scorefiles are outputted in the same row)")
#parser.add_argument('-v', action='store_true', help = "to store a vocabulary dictionary, specify the filename")
parser.add_argument('--hidden', action='store', required = False, nargs = '+', help = "[KNN] if instances contain hidden classes to be retrieved in evaluation, specify their topclas(ses)")
parser.add_argument('-ot', action='store', required = False, help = "[WINDOW] specify the output type")
parser.add_argument('--plot', action='store_true', help = "[WINDOW] choose to plot data")
parser.add_argument('-e', action='store', required = False, help = "[WINDOW] give a file with event information")

args = parser.parse_args()

evaluation = Evalset(args.i)

#if args.v:
#    evaluation.set_vocabulary(args.v)
if args.w:
    depth = int(args.d) * -1
    dir_scores = defaultdict(list)
    for i,f in enumerate(args.l):
        cats = f.split("/")
        dir_scores[cats[depth]].append(f)
    window_size = int(args.w[0])
    slider = int(args.w[1])
    threshold = int(args.w[2])
    evaluation.set_meta(args.m,args.multi)
    evaluation.evaluate_window(dir_scores,window_size,slider,threshold,args.o,args.ot,args.hidden,args.plot,args.f,args.e)
        
else:
    if args.i == "lcs":
        labelfiles = args.l
        observationfiles = args.c
        for i,l in enumerate(labelfiles):
            evaluation.set_instances_lcs(l,observationfiles[i],"normal")
        evaluation.print_results(outfile)
        
        if args.fp:
            c = raw_input("Please specify the class for which false positives should be extracted...\n")
            freq = int(raw_input("Please choose the number of instances to write...\n"))
            files = raw_input("Please specify the directory with instance files...\n")
            out = raw_input("Please give the file to write the instances to...\n")
            evaluation.extract_top_fp(out,c,freq,files)

    elif args.i == "meta":
        metafiles = args.l
        for m in metafiles:
            evaluation.set_instances_meta(m,args.w)
        
    elif args.i == "sparsebin":
        exit()

