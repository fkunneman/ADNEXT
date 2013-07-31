#!/usr/bin/env python

from __future__ import division
import matplotlib.pyplot as plt
from collections import defaultdict

def calculate_precision(lines,plot = False):
    majority_judgements = defaultdict(list)
    precisions = []
    precision_strengths = defaultdict(int)
    annotators = len(lines[0])
    for line in lines:
        num_positive = 0
        for annotation in line:
            if annotation == 1:
                num_positive += 1

        percentage = num_positive / len(line)
        majority = int(len(line) / 2) + 1 
        if percentage >= 0.5:
            for i in range(majority,len(line)+1):
                if i <= num_positive:
                    precision_strengths[i] += 1
                    majority_judgements[i].append(1)
                else:
                    majority_judgements[i].append(0)
        else:
            for i in range(majority,len(line)+1):
                majority_judgements[i].append(0) 

    for ps in sorted(precision_strengths.keys()):
        precision_score = precision_strengths[ps] / len(lines)
        precisions.append((ps,precision_score))

    if plot:
        for strength in sorted(majority_judgements.keys()):
            rank = []
            precision = []
            seen = 0
            correct = 0
            for judgement in majority_judgements[strength]:
                seen += 1
                if judgement == 1:
                    correct += 1 
                rank.append(seen)
                precision.append(correct/seen)
            plt.plot(rank,precision)
        
        legend_entries = sorted(majority_judgements.keys())
        for i,entry in enumerate(legend_entries):
            percentage = str(int(entry/annotators * 100))
            legend_entries[i] = percentage + "% positive"
        plt.legend(legend_entries)
        plt.ylabel("precision at rank")
        plt.xlabel("rank")
        plt.savefig(plot)

    return precisions

def calculate_cohens_kappa(lines):    
    annotator_couples = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))
    annotator_scores = defaultdict(lambda : defaultdict(int))
    for line in lines:
        for i,annotation in enumerate(line):
            annotator_scores[i][annotation] += 1
            j = i
            while j+1 < len(line):
                if annotation != line[j+1]:
                    annotator_couples[i][j+1]["odd"] += 1
                else:
                    annotator_couples[i][j+1]["match"] += 1
                j += 1

    cohens_kappas = []
    for annotator_1 in annotator_couples.keys():
        for annotator_2 in annotator_couples[annotator_1].keys():
            agreement = annotator_couples[annotator_1][annotator_2]["match"] / len(lines)
            random = 0
            for answer in annotator_scores[annotator_1].keys():
                percent_1 = annotator_scores[annotator_1][answer] / len(lines)
                percent_2 = annotator_scores[annotator_2][answer] / len(lines)
                random += (percent_1 * percent_2)
            ck = (agreement - random) / (1 - random)
            cohens_kappas.append(ck)    

    cohens_kappa = round(sum(cohens_kappas) / len(cohens_kappas),2)
    return cohens_kappa

#function that returns krippendorff's alpha with a nominal distance metric
#input is an array (items) of arrays (values)
def calculate_krippendorffs_alpha(lines):
    #calculate the value that is used for multiplication in both the observed agreement and expected agreement
    num_items = len(lines)
    num_coders = len(lines[0])
    multiplier = 1 / (num_items*num_coders*(num_coders-1))
    #calculate observed agreement
    item_agreements = 0
    #for each item
    for item in lines:
        item_agreement = 0
        annotation_counts = defaultdict(int)
        #count frequency of each annotation
        for annotation in item:
            annotation_counts(annotation) += 1
        for annotation_value_a in annotation_counts.keys():
            for annotation_value_b in annotation_counts.keys():
                if annotation_value_a != annotation_value_b:
                    item_agreement += annotation_counts[annotation_value_a] * annotation_counts[annotation_value_b]
        item_agreements += item_agreement
        DO = item_agreements*multiplier
    #calculate expected agreement
    
