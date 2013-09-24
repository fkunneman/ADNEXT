#!/usr/bin/env python

import argparse
from evalset import Evalset
from collections import defaultdict
import time_functions
import gen_functions

parser = argparse.ArgumentParser(description = "Program to evaluate the time-to-event of tweets with a slider")

parser.add_argument('-l', action = 'store', required = True, nargs='+', help = "the label / label+classification files (required)")
#parser.add_argument('-g', action='store', required=False, nargs='+', help = "the classification files (if separated)")
parser.add_argument('-m', action='store', required=True, nargs='+', help = "the files with meta-information")
parser.add_argument('-v', action='store', required = False, nargs='+', help = "[KNN] give vocabulary files to link indexes to features")
parser.add_argument('-o', action='store', required=True, help = "file to write the results to (required)")
#parser.add_argument('--multi', action='store_true', help = "confirm when the meta-file contains instances for multiple testsets")
parser.add_argument('-i', action = 'store', choices = ["lcs","ibt","knn"], help="specify the input type of label (and classification) files")
#parser.add_argument('-d', action='store', default = 1, help = "Define the depth of a distinct testset in terms of the path of scorefiles; [Default = 1]  (in the case of the testset \'bla\' and the paths \'bla/score1.txt\' and \'bla/score2.txt\', give two as the depth and the results for the different scorefiles are outputted in the same row)")
#parser.add_argument('--hidden', action='store', required = False, nargs = '+', help = "[KNN] if instances contain hidden classes to be retrieved in evaluation, specify their topclas(ses)")
parser.add_argument('-e', action='store', required = True, help = "specify the file with event information")
# parser.add_argument('-f', action='store', default = "all_to_one", help = "[WINDOW] filter of output (default = all-to-one")
# parser.add_argument('-et', action='store', default = "rmse", help = "specify the evaluation type (default = rmse")
parser.add_argument('--size', action='store', default = 24, help = "specify the window size (in hours)")
parser.add_argument('--slider', action='store', default = 1, help = "specify the slider (in hours)")
# parser.add_argument('--threshold', action='store', default = 100, help = "specify the threshold after which to score")
parser.add_argument('--plot', action='store_true', help = "choose whether results are plotted")
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
        # if window.seen < args.threshold:
        #     window.set_classification("abstain")
        # else:

            # # if self.input_type == "meta":
            # estimations = defaultdict(int)
            
            # #     for instance in window[0]:
            # #         try:
            #             # if not instance.classification[0] == "nt":
            # for instance in window.instances:
            #     estimations[instance.classification[0]] += 1
            #         # except IndexError:
            #         #     continue
            # if len(estimations) == 0:
            #     window.set_classification("abstain")
            # else:
            #     ranked_estimations = sorted(estimations,key = estimations.get,reverse=True)
                # majority = ranked_estimations[0]
                # if len(ranked_estimations) == 1 or estimations[majority] > estimations[ranked_estimations[1]]:
                #     if majority == "early":
                #         testwindow.set_classification("abstain")
                #     else:
                #         testwindow.set_classification(majority)
                # else:
                #     testwindow.set_classification("abstain")
        
        predictions = defaultdict(int)
        predictions_days = defaultdict(int)
        score_prediction = defaultdict(list)                
        #check for majority
        for instance in window.instances:
            # try:
#            print instance.classification[0]
            try:
                if instance.time_classification[0] in ["early","during","after"]:
                    predictions[instance.time_classification[0]] += 1
                else:
                    predictions["tte"] += 1
                    predictions_days[instance.time_classification[0]] += 1
                    score_prediction[instance.time_classification[1]].append(instance.time_classification[0])
            except AttributeError:
                predictions[instance.classification] += 1
                #continue
#        print predictions

        majority_rank = sorted(predictions,key = predictions.get,reverse=True)
        if majority_rank[0] == "tte" or predictions["tte"] == predictions[majority_rank[0]]:
            tte_rank = sorted(predictions_days,key=predictions_days.get,reverse=True)
            score_rank = sorted(score_prediction.keys(),reverse=True)
            estimation = evaluation.extract_timelabel(predictions_days,tte_rank,score_prediction,score_rank)
            window.set_classification(estimation[0])
        else:
            window.set_classification("abstain")
    #     testwindows.append(testwindow)
    # if plot:
    #     plotfile = "/".join(outfile.split("/")[:-1]) + "/" + self.input_type + "_" + event + "_plot.png"
    #     evaluation = self.calculate_rmse(testwindows,plotfile)

    event_results = []
    rmse = evaluation.calculate_rmse()
    event_results.extend(rmse[1:])
    out.write(" ".join([str(e) for e in rmse[1:]]))
    table = evaluation.return_results()
    for label in table[1:]:
        event_results.extend(label[1:4])
        out.write(" " + " ".join([str(e) for e in label[:4]]))
    for i,token in enumerate(event_results):
        cols[i].append(token)
    out.write("\n")

aggregates = []
for i in range(len(cols.keys())):
    col = cols[i]
    mean = sum(col) / len(col)
    stdev = gen_functions.return_standard_deviation(col)
    aggregates.append(str(mean) + " (" + str(stdev) + ")")

out.write("\n".join(aggregates))
out.close()

    # if self.input_type == "meta":
    #     out_dict[event] = evaluation[-4:]
    # elif self.input_type == "knn":
    # out_dict[event + "_" + validation + "_" + k] = evaluation[-4:]
    # elif self.input_type == "lcs":
    #     out_dict[event + "_" + validation] = evaluation[-4:]

# elif output == "fscore":
#     print "fscore"
#     ce = proy_evaluation.ClassEvaluation()
#     for window in windows:
#         testwindow = Evalset.Instance()
#         testwindow.set_tfz(window[1])
#         label = (window[0][-1].label)
#         if label == "during" or label == "after":
#             label = "late"
#         else:
#             if window[0][-1].timelabel == "early":
#                 label = "early"
#             else:
#                 label = "before"
#         if self.input_type == "meta":
#             estimations = defaultdict(int)
#             for instance in window[0]:
#                 try:
#                     if not instance.classification[0] == "nt":
#                         estimations[instance.classification[0]] += 1
#                 except IndexError:
#                     continue
#             ranked_estimations = sorted(estimations,key = estimations.get,reverse=True)
#             if len(ranked_estimations) == 0:
#                 classification = "late"
#             else:
#                 majority = ranked_estimations[0]
#                 if len(ranked_estimations) == 1 or estimations[majority] > estimations[ranked_estimations[1]]:
#                     if majority == "early":
#                         classification = "early"
#                     else:
#                         classification = "before"
#                 else:
#                     classification = "late"
            
#         else:
#             predictions = defaultdict(int)
#             predictions_other = defaultdict(int)
#             score_prediction = defaultdict(list)
#             #check for majority
            
#             for instance in window[0]:
#                 try:
#                     if instance.classification == "early":
#                         print instance.classification[0]
#                     if instance.classification[0] in ["early","during","after"]:
#                         predictions[instance.classification[0]] += 1
#                     else:
#                         predictions["before"] += 1
#                 except IndexError:
#                     continue
#             majority_rank = sorted(predictions,key = predictions.get,reverse=True)
#             if majority_rank[0] == "before" or predictions["before"] == predictions[majority_rank[0]]:
#                 classification = "before"
#             else:
#                 if majority_rank[0] == "early" or predictions["early"] == predictions[majority_rank[0]]:
#                     classification = "early"
#                 else:
#                     classification = "late"
#         ce.append(label,classification)
#     for label in sorted(list(set(ce.goals))):
#         out_dict[label]["precision"].append(round(ce.precision(cls=label),2))
#         out_dict[label]["recall"].append(round(ce.recall(cls=label),2))
#         out_dict[label]["f1"].append(round(ce.fscore(cls=label),2))
