#!/usr/bin/env python

from __future__ import division
import matplotlib.pyplot as plt
from collections import defaultdict
from pynlpl import evaluation
import itertools
import re
import numpy

def calculate_precision(lines,lax = False,plot = False):
    majority_judgements = defaultdict(list)
    precisions = []
    precision_strengths = defaultdict(int)
    if lax:
        annotators = max([len(x) for x in lines])
    else:
        annotators = len(lines[0])
    for line in lines:
        #if len(line) == 1:
        #    if line[0] == 1:
        if not lax and len(line) != annotators:
            print "num annotators not consistent, exiting program"
            exit()
        num_positive = 0
        for annotation in line:
            if annotation == 1:
                num_positive += 1

        percentage = num_positive / len(line)
        majority = int(round(len(line) / 2))
        if percentage >= 0.5: #classification is true
            for i in range(majority,len(line)+1): #for every degree of majority (1.0, .66, .5)
                if i <= num_positive:
                    precision_strengths[i] += 1
                    majority_judgements[i].append(1) #if degree of majority applies, add 1
                else:
                    majority_judgements[i].append(0) #if degree of majority is not met, add 0
        else: #classification is false
            for i in range(majority,len(line)+1):
                majority_judgements[i].append(0) #add 0 to any degree of majority

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
    fields = 0
    for line in lines:
        if len(line) > 1:
            fields += 1
            for i,annotation in enumerate(line):
                annotator_scores[i][annotation] += 1 #annotator - annotation
                j = i
                while j+1 < len(line):
                    if annotation != line[j+1]:
                        annotator_couples[i][j+1]["odd"] += 1
                    else:
                        annotator_couples[i][j+1]["match"] += 1
                    j += 1
    print "lines-fields",len(lines),fields

    cohens_kappas = []
    print(annotator_couples.keys())
    for annotator_1 in annotator_couples.keys():
        for annotator_2 in annotator_couples[annotator_1].keys():
            print(annotator_1,annotator_2)
            agreement = annotator_couples[annotator_1][annotator_2]["match"] / len(lines)
            print("agreement:",agreement)
            random = 0
            for answer in annotator_scores[annotator_1].keys():
                percent_1 = annotator_scores[annotator_1][answer] / len(lines)
                percent_2 = annotator_scores[annotator_2][answer] / len(lines)
                random += (percent_1 * percent_2)
            print("random",random)
            ck = (agreement - random) / (1 - random)
            print("ck",ck)
            cohens_kappas.append(ck)    

    cohens_kappa = round(sum(cohens_kappas) / len(cohens_kappas),2)
    return cohens_kappa

def calculate_weighted_kappa(lines):
    mean_score = []
    coder_annotations = defaultdict(lambda : defaultdict(int))
    pairs_count = defaultdict(lambda : defaultdict(int))
    weights = defaultdict(lambda : defaultdict(float))
    coder_score_pkp = defaultdict(lambda : defaultdict(float))
    missing = 0
    missing_both = 0
    all_annotations = []
    for line in lines:
        l = False
        for x in line:
            if re.search("\d",x):
                l = True
        if l:
            if "miss" in line:
                missing += 1
                mean_score.append(int([x for x in line if x != "miss"][0]))
            else:
                pairs_count[int(line[0])][int(line[1])] += 1
                mean_score.append(numpy.mean([int(x) for x in line]))
            for i,annotation in enumerate(line):
                all_annotations.append(annotation)
                if annotation == "miss":
                    coder_annotations[i]["missing"] += 1
                else:
                    coder_annotations[i][int(annotation)] += 1
        else:
            missing_both += 1

    print mean_score
    nlines = len(lines)-missing_both
    #weights
    scores = list(set(all_annotations))
    scores.remove("miss")
    scores = [int(x) for x in scores]
    difmm = max(scores) - min(scores)
    difmms = difmm * difmm 
    for c in itertools.permutations(scores,2):
        dif = c[0] - c[1]
        difs = dif*dif
        weights[c[0]][c[1]] = 1 - (difs/difmms)
    for score in scores:
        weights[score][score] = 1.0

    #observed
    px = 1 - (missing/nlines)
    observed_total = 0
    for an1 in pairs_count.keys():
        for an2 in pairs_count[an1].keys():
            pkl = pairs_count[an1][an2] / nlines
            observed_total += (pkl/px) * weights[an1][an2]
            print pairs_count[an1][an2],"table observed",an1,an2,(pkl/px),"weight",(pkl/px) * weights[an1][an2]
            print "total",observed_total
    print("observed",observed_total)

    #expected
    expected_total = 0
    for coder in coder_annotations.keys():
        pxp = 1 - (coder_annotations[coder]["missing"] / nlines)
        for score in scores:
            if score in coder_annotations[coder].keys():
                coder_score_pkp[coder][score] = (coder_annotations[coder][score]/nlines) / pxp
    for c in itertools.permutations(scores,2):
        expected_total += (coder_score_pkp[0][c[0]] * coder_score_pkp[1][c[1]]) * weights[c[0]][c[1]]
        print "table expected",c[0],c[1],(coder_score_pkp[0][c[0]] * coder_score_pkp[1][c[1]]),"weight",(coder_score_pkp[0][c[0]] * coder_score_pkp[1][c[1]]) * weights[c[0]][c[1]]
    for score in scores:
        expected_total += (coder_score_pkp[0][score] * coder_score_pkp[1][score]) * weights[score][score]
        print "table expected",score,score,(coder_score_pkp[0][score] * coder_score_pkp[1][score]),"weight",(coder_score_pkp[0][score] * coder_score_pkp[1][score]) * weights[score][score]
    print("expected",expected_total)
    weighted_k = (observed_total - expected_total) / (1 - expected_total)
    print pairs_count
    print("weighted cohens k",weighted_k)
    avg = numpy.mean(mean_score)
    print("avg.",numpy.mean(mean_score))
    return weighted_k,avg,nlines 

def calculate_confusion_matrix(lines):    
    annotator_couples = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(int))))
    annotator_scores = defaultdict(lambda : defaultdict(int))
    for line in lines:
        if len(line) > 1:
            for i,annotation in enumerate(line):
                annotator_scores[i][annotation] += 1
                j = i
                while j+1 < len(line):
                    if annotation != line[j+1]:
                        annotator_couples[i][j+1]["odd"][annotation] += 1
                    else:
                        annotator_couples[i][j+1]["match"][annotation] += 1
                    j += 1

    cohens_kappas = []
    percent = []
    for annotator_1 in annotator_couples.keys():
        for annotator_2 in annotator_couples[annotator_1].keys():
            for combm in annotator_couples[annotator_1][annotator_2]["match"].keys():
                print annotator_1,annotator_2,"match",combm,annotator_couples[annotator_1][annotator_2]["match"][combm]
            for combo in annotator_couples[annotator_1][annotator_2]["odd"].keys():
                print annotator_1,annotator_2,"odd",combo,annotator_couples[annotator_1][annotator_2]["odd"][combo]
            agreement = sum([annotator_couples[annotator_1][annotator_2]["match"][x] for x in annotator_couples[annotator_1][annotator_2]["match"].keys()]) / len(lines)
            random = 0
            for answer in annotator_scores[annotator_1].keys():
                percent_1 = 0.5
                percent_2 = 0.5
                random += (percent_1 * percent_2)
            ck = (agreement - 0.5) / (1 - 0.5)
            cohens_kappas.append(ck) 
            percent.append(agreement)

#function that returns krippendorff's alpha with a nominal distance metric
#input is an array (items) of arrays (values)
def calculate_krippendorffs_alpha(lines):
    #some constants
    num_items = len(lines)
    num_coders = len(lines[0])
    #counter
    annotation_counts = defaultdict(int)
    #calculate observed agreement
    item_agreements = 0
    #for each item
    for item in lines:
        item_agreement = 0
        #count frequency of each annotation
        annotation_counts_item = defaultdict(int)
        for annotation in item:
            annotation_counts_item[annotation] += 1
            annotation_counts[annotation] += 1
        for annotation_value_a in annotation_counts_item.keys():
            for annotation_value_b in annotation_counts_item.keys():
                if annotation_value_a != annotation_value_b:
                    item_agreement += annotation_counts_item[annotation_value_a] * annotation_counts_item[annotation_value_b]
        item_agreements += item_agreement
    multiplier = 1 / (num_items*num_coders*(num_coders-1))
    DO = item_agreements*multiplier
    #calculate expected agreement
    agreement = 0
    for annotation_a in annotation_counts.keys():
        for annotation_b in annotation_counts.keys():
            if annotation_a != annotation_b:
                agreement += annotation_counts[annotation_a] * annotation_counts[annotation_b]
    multiplier = 1 / (num_items*num_coders*((num_items*num_coders)-1))
    DE = agreement*multiplier
    #calculate and return Krippendorffs Alpha
    KA = round(1-(DO/DE),2)
    return KA         

def calculate_fscore(lines,index_1,index_2):
    ce = evaluation.ClassEvaluation()
    for item in lines:
        ce.append(item[index_1],item[index_2])
    return round(ce.fscore(cls='1'),2)

def calculate_mutual_fscore(lines,lax=False):
    if lax:
        num_coders = max([len(x) for x in lines])
    else:
        num_coders = len(lines[0])
    fscores = []
    perms = list(itertools.permutations(range(num_coders),2))
    for p in perms:
        fscores.append(calculate_fscore(lines,p[0],p[1]))
    print(fscores)
    mutual_fscore = round(sum(fscores)/len(fscores),2)
    return mutual_fscore
