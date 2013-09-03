#!/usr/bin/env python

import argparse
import codecs
from collections import defaultdict

parser = argparse.ArgumentParser(description = "Program to process sentences (divided by linebreaks) and count the frequency of feature categories")

parser.add_argument('-i', action = 'store', required = True, help = "the txt file to be processed")
parser.add_argument('-f', action = 'store', required = True, help = "the file with feature categories (txt; each feature in a separate column, divided by tabs)")

args = parser.parse_args()

feature_cats_open = codecs.open(args.f,"read","utf-8") 
feature_cats = defaultdict(list)
for line in feature_cats_open.readlines():



for line in markerfile:
        line = line.strip()
        tokens = line.split("\t")
        intensifiers.append(tokens[1])
        exclamations.append(tokens[0])
        try:
                markers.append(tokens[2])
        except IndexError:
                print "IE"

for line in parts:
        tokens = line.split(" ")
        filename = tokens[0]
        try:
                label = tokens[1].strip()
        except IndexError:
                print line
        file_label[filename] = label
labels = list(set(file_label.values()))

testrank = open(directory + "test.rnk", "r")
for line in testrank:
        tokens = line.split("  ")
        filename = tokens[0].strip()
        scores = tokens[1]
        classification_score = scores.split(" ")[0].split(":")
        classification = classification_score[0]
        score = classification_score[1]
        classification_scores[filename] = score
        if not re.search(r"\?",classification):
                file_classification[filename] = classification
        else:
                fn_ranks[filename] = score

for filename in file_label.keys():
        label = file_label[filename]
        try:
                classification = file_classification[filename]
                if label == classification:
                        evaldict[label]["tp"] += 1
                        for other_label in labels:
                                if other_label != label:
                                        evaldict[other_label]["tn"] += 1
                else:
                        evaldict[label]["fn"] += 1
                        evaldict[classification]["fp"] += 1
                        if classification in labels_of_interest:
                                fp_ranks[filename] = classification_scores[filename]
        except KeyError:
                evaldict[label]["fn"] += 1
                if label in labels_of_interest:
                        fn_ranks[filename] = classification_scores[filename]

# calculate scores and write to resultsfile
microaverage = defaultdict(int)
for label in evaldict.keys():
        print label
        labelscores = evaldict[label]
        for score in labelscores.keys():
                microaverage[score] += labelscores[score]

        frequency = labelscores["tp"] + labelscores["fn"]
        pr_re_f1 = classification_devs.return_pr_re_f1(labelscores["tp"],labelscores["fp"],labelscores["tn"],labelscores[$
        roc = classification_devs.return_roc(labelscores["tp"],labelscores["fp"],labelscores["tn"],labelscores["fn"])
        correct = labelscores["tp"]
        classified = labelscores["tp"] + labelscores["fp"]
        labeled = labelscores["tp"] + labelscores["fn"]
        resultout.write(label + " " + str(frequency) + " " + str(pr_re_f1[0]) + " " + str(pr_re_f1[1]) + " " + str(pr_re_$
#microaverage_precision = microaverage["tp"] / (microaverage["tp"] + microaverage["fp"])
#microaverage_recall = microaverage["tp"] / (microaverage["tp"] + microaverage["fn"])
#microaverage_f1 = round(2 * ((microaverage_precision*microaverage_recall) / (microaverage_precision+microaverage_recall)$
#resultout.write("micro's: " + str(round(microaverage_precision,2)) + " " + str(round(microav

total = 0
for i,filename in enumerate(sorted(fp_ranks, key=fp_ranks.get, reverse=True)[:250]):
        fileread = open(files + filename,"r")
        words = []
        print i
        if agreement[i] == "1":
                total += 1
                marker = False
                intensifier = False
                exclamation = False
                for line in fileread:
                        term = line.strip()
                        if term in markers:
                                #if not marker:
                                        #percent_mi["marker"] += 1
                                marker = True
                                #if intensifier and not mi:
                                #       percent_mi["mi"] += 1
                                #       mi = True
                        elif term in intensifiers:
                                #if not intensifier:
                                #       percent_mi["intensifier"] += 1
                                intensifier = True
                                #if marker and not mi:
                                #       percent_mi[mi] += 1
                                #       mi = True
                        elif term in exclamations:
                                exclamation = True

                if marker or intensifier or exclamation:
                        if marker:
                                if intensifier or exclamation:
                                        if intensifier and exclamation:
                                                percent_mi["triple"] += 1
                                        elif intensifier:
                                                percent_mi["mi"] += 1
                                        else:
                                                percent_mi["me"] += 1
                                else:
                                        percent_mi["marker"] += 1
                        elif intensifier:
                                if exclamation:
                                        percent_mi["ie"] += 1
                                else:
                                        percent_mi["intensifier"] += 1
                        else:
                                percent_mi["exclamation"] += 1
                else:
                        percent_mi["none"] += 1
                #text = " ".join(words)
                #fp_out.write(str(fp_ranks[filename]) + "\t" + text + "\n")

print "total: ", total
for cat in percent_mi.keys():
        freq = percent_mi[cat]
        percent = freq / total
        print cat + ": ", percent
#percent_marker = percent_mi["marker"] / 250
#percent_intensifier = percent_mi["intensifier"] / 250
#pmi = percent_mi["mi"] / 250
        resultout.write("\n" + cat + ": " + str(percent))

for filename in sorted(fn_ranks, key=fn_ranks.get, reverse=True):
        fileread = open(files + filename,"r")
        words = []
        for line in fileread:
                if not re.search("_",line):
                        if not re.match("intensifier",line):
                                words.append(line.strip())
        text = " ".join(words)
        fn_out.write(str(fn_ranks[filename]) + "\t" + text + "\n")