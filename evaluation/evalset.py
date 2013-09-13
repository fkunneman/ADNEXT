#! /usr/bin/env python

from __future__ import division
import re
from pynlpl import evaluation
import time_functions
from collections import defaultdict
import datetime
import matplotlib.pyplot as plt
from sklearn.metrics import auc
import codecs
import math

class Evalset():

    def __init__(self,input_type):
        self.input_type = input_type
        # instances = codecs.open(instancefile,"r","utf-8")
        self.instances = []
        # instances.close()
        # self.name_instance = {}
        # self.testset_instances = defaultdict(list)
        # self.time_buckets = defaultdict(list)

    def set_meta(self,metafile,metadict):
        meta = codecs.open(metafile,"r","utf-8")
        if self.input_type == "lcs":
            self.name_instance = {}
        for line in meta.readlines():
            instance = Evalset.Instance()
            tokens = line.strip().split("\t")
            for meta_info in metadict.keys():
                instance.dict[meta_info] = tokens[metadict[meta_info]]
            if self.input_type == "lcs":
                self.name_instance[tokens[metadict["name"]]] = instance
            self.instances.append(instance)
        meta.close()
        #         instance.set_name(tokens[0])
        #         instance.set_id(tokens[1])
        #         instance.set_event(tokens[2])
        #         instance.set_label(tokens[3])
        #         instance.set_tfz(int(tokens[5]))
        #         instance.set_timelabel(tokens[4])
        #         instance.set_date(tokens[6])
        #         instance.set_time(tokens[7])
        #         self.name_instance[tokens[0]] = instance
        #         self.instances.append(instance)
        #         if multiple:
        #             self.testset_instances[instance.event].append(instance)
        # else:
        #     for line in meta.readlines():
        #         instance = Evalset.Instance()
        #         tokens = line.split("\t")
        #         instance.set_id(tokens[0])
        #         instance.set_event(tokens[1])
        #         instance.set_label(tokens[2])
        #         instance.set_tfz(int(tokens[3]))
        #         instance.set_timelabel(tokens[4])
        #         instance.set_date(tokens[5])
        #         instance.set_time(tokens[6])
        #         self.instances.append(instance)
        #         if multiple:
        #             self.testset_instances[instance.event].append(instance)

    def set_instances_lcs(self,labelfile,classificationfile,evaluationtype,threshold = False):         
        labels = open(labelfile)
        for line in labels:
            tokens = line.split(" ")
            filename = tokens[0]
            label = tokens[1].strip()
            instance = Evalset.Instance()
            instance.set_label(label)
            instance.set_name(filename)
            self.name_instance[filename] = instance
            self.instances.append(instance) 
   
        classifications = codecs.open(classificationfile,"r","utf-8")
        for line in classifications.readlines():
            tokens = line.split("  ")
            filename = tokens[0].strip()
            instance = self.name_instance[filename]
            scores = tokens[1]
            classification_score = scores.split(" ")[0].split(":")
            if not (threshold and re.search(r"\?",classification_score[0])):  
                classification = re.sub("\?","",classification_score[0])
                score = float(classification_score[1])
                if evaluationtype == "timelabel":
                    if instance.classification[0] == "before":
                        instance.set_classification((classification,score))
                else:
                    instance.set_classification(classification)
                    if classification != instance.label:
                        instance.set_fp()
                        instance.set_fn()
                    else:
                        instance.set_tp() 
                    instance.set_score(score)
        classifications.close()
    
    def set_instances_knn(self,classification_file,hidden=False):
        #extract information
        cl_open = open(classification_file)
        classifications_nn = defaultdict(list)
        classifications = []
        nn = []
        test = ""
        for line in cl_open.readlines():
            if re.search("==",line):
                classifications.append(line)
                if not test == "":
                    classifications_nn[test] = nn
                nn = []
                test = line
            else:
                nn.append(line)
        classifications_nn[test] = nn
        cl_open.close()
        if len(classifications) != len(self.instances):
            print len(classifications),len(self.instances),"classification and meta do not align, exiting program..."
            exit()
        #set classification
        for i,line in enumerate(classifications):
            instance = instances[i]
            tokens = line.split("==")[1].split("  ")[1].split(" ")
            if instance.label == tokens[0]:
                classification = tokens[1]
                neighbours = classifications_nn[line]
                label_scores = defaultdict(list)
                if hidden and classification in hidden:
                    timelabel_freq = defaultdict(int)
                    score_timelabel = defaultdict(list)
                    for neighbour in neighbours:
                        neighbour_tokens = neighbour.split(" ")[1].split(",")
                        label = neighbour_tokens[-1]
                        score = float(neighbour.split("  ")[1])
                        label_scores[label].append(score)
                        if label in hidden:
                            timelabel_index = neighbour_tokens[0]
                            timelabel = self.vocabulary[timelabel_index]
                            timelabel_freq[timelabel] += 1
                            score_timelabel[score].append(timelabel)
                    
                    timelabel_rank = sorted(timelabel_freq,key=timelabel_freq.get, reverse=True)
                    score_rank = sorted(score_timelabel.keys(),reverse = True)
                    selected_tl = self.extract_timelabel(timelabel_freq,timelabel_rank,score_timelabel,score_rank)
                    instance.set_classification(selected_tl)
                else:
                    for neighbour in neighbours:
                        label = neighbour.split(" ")[1].split(",")[-1]
                        score = float(neighbour.split("  ")[1])
                        label_score[label].append(score)
                    highest_score = sorted(label_score[classification],reverse=True)[0]
                    instance.set_classification((classification,highest_score))
            else:
                print "error: no label match; exiting program"
                exit()

    def set_instances_sparse_meta(self,infile):
        readfile = open(infile,"r").readlines()
        for line in readfile:
            tokens = line.strip().split("\t")
            instance = Evalset.Instance()
            instance.set_name(tokens[0])
            instance.set_event(tokens[1])
            instance.set_label(tokens[2])
            instance.set_classification(tokens[3])
            instance.set_tfz(tokens[4])
            self.name_instance[filename] = instance
            self.instances.append(instance) 


    def set_vocabulary(self,vocabfile):
        self.vocabulary = {}
        vocab_read = codecs.open(vocabfile,"r","utf-8")
        vocabularylines = vocab_read.readlines()
        vocab_read.close()
        for line in vocabularylines:
            tokens = line.strip().split("\t")
            self.vocabulary[tokens[0]] = tokens[1]

    def calculate_rmse(self,instances,plotfile = False):
        outcomes = []
        if plotfile:
            plot_out = open(plotfile,"w")
        sse = 0
        rsse = 0
        scores = 0
        fes = 0
        ab = 0
        es = 0
        fab = 0
        before = 0
        for instance in instances:
            target = instance.label
            target_tl = str(instance.timelabel)
            prediction = str(instance.classification)
            outcome = [str(instance.tfz),target,prediction]
            if target == "-" or target == "early":
                outcome.extend(["ab","ab"])
                ab += 1
                fes += 1
            else:
                before += 1
                if prediction == "abstain":
                    outcome.extend(["ab","ab"])
                    ab += 1
                else:
                        
                    es += 1
                    target = int(target)
                    prediction = int(prediction)
                    dif = target - prediction
                    if plotfile:
                        if dif < 0:
                            dif = dif * -1
                        plot_out.write(str(instance.tfz*-1) + "\t" + str(dif) + "\n")
                    se = dif * dif
                    if se == 0:
                        rse = 0
                    else:
                        rse = round(se / (se-target),2)
                    scores += 1
                    sse += se
                    rsse += rse
                    outcome.extend([str(se),str(rse)])
                    
            outcomes.append(outcome)
        if plotfile:
            plot_out.close()
        if scores > 0:
            rmse = round(math.sqrt(sse / scores),1)
            mrse = round((rsse/scores),2)
            fabs = round(fab/es,2)
        else:
            rmse = "-"
            mrse = "-"
            fabs = "-"
        #fes_percent = round(fes/ab,2)
        responsiveness = round((scores/before),2)
        outcomes.extend([rmse,responsiveness,len(instances),mrse])
        return outcomes

    def extract_timelabel(self,timelabel_freq,timelabel_rank,score_timelabel,score_rank):
        
        def select_highest_score_tl(rank_ds,ds_tl,tl):
            for ds in rank_ds:
                if tl in ds_tl[ds]:
                    return ds
        
        if len(timelabel_rank) == 1:
            return (timelabel_rank[0],score_rank[0])
        elif timelabel_freq[timelabel_rank[0]] > timelabel_freq[timelabel_rank[1]]:
            score = select_highest_score_tl(score_rank,score_timelabel,timelabel_rank[0])
            return (timelabel_rank[0],score)
        else: #there is no majority class
            selected = []
            majoritybound = 0
            majorityfreq = timelabel_freq[timelabel_rank[0]]
            #generate a list of the most frequent classes
            for i,tl in enumerate(timelabel_rank[1:]):
                if timelabel_freq[tl] < majorityfreq:
                    majoritybound = i+2
                    break
                if i+2 == len(timelabel_rank):
                    majoritybound = i+2
            majority_timelabels = timelabel_rank[:majoritybound]
            score_bound = 0
            score_highest = score_rank[0]
            
            for i,sr in enumerate(score_rank):
                if sr < score_highest:
                    score_bound = i
                    break
                if i+1 == len(score_rank):
                    score_bound = i+1
            for score in score_rank[:score_bound]:
                timelabels = score_timelabel[score]
                for timelabel in timelabels:
                    if timelabel in majority_timelabels:
                        selected.append(timelabel)
             
            selected = list(set(selected))
            if len(selected) == 0:
                selected = self.extract_timelabel(timelabel_freq,timelabel_rank,score_timelabel,score_rank[score_bound:])
                return selected
            elif len(selected) == 1:
                score = select_highest_score_tl(score_rank,score_timelabel,selected[0])
                return (selected[0], round(score,4))
            elif len(selected) > 1:
                sum_selected = 0
                for s in selected:
                    if s == "early":
                        sum_selected += -22
                    else:
                        sum_selected += int(s)
                mean = int(sum_selected / len(selected))
                score = select_highest_score_tl(score_rank,score_timelabel,selected[0])
                return (mean, round(score,4))

    def evaluate_window(self,event_scores,windowsize,slider,threshold,outfile,output = "rmse",hidden = False,plot = False,filt = False,eventfile=False):
        
        if eventfile:
            event_time = time_functions.generate_event_time_hash(eventfile)

        out = open(outfile,"w")
        out_dict = {}
        if output == "fscore":
            out_dict = defaultdict(lambda: defaultdict(list))
        #walk through events
        for event in self.testset_instances.keys():
            event_file = re.sub(" ","_",event)
            print event_file
            if hidden:
                file_tokens = event_scores[event_file][0].split("/")
                file_tokens[-1] = "vocabulary"
                vocabulary_file = "/".join(file_tokens)
                vocabulary_read = codecs.open(vocabulary_file,"r","utf-8")
                self.vocabulary = {}
                for line in vocabulary_read:
                    tokens = line.strip().split("\t")
                    self.vocabulary[tokens[0]] = tokens[1] 
            if self.input_type == "meta":
                metafile_baseline = codecs.open(event_scores[event_file][0],"r","utf-8")
                meta_instances = []
                for line in metafile_baseline:
                    instance = Evalset.Instance()
                    tokens = line.split("\t")
                    instance.set_id(tokens[0])
                    instance.set_event(tokens[1])
                    instance.set_label(tokens[2])
                    instance.set_classification([tokens[3]])
                    instance.set_tfz(int(tokens[4]))
                    instance.set_timelabel(tokens[5])
                    instance.set_date(tokens[6])
                    instance.set_time(tokens[7])
                    self.instances.append(instance)
                    meta_instances.append(instance)
            else:
                meta_instances = self.testset_instances[event]
            #temporal
            #bda = defaultdict(int)
            #for ins in meta_instances:
            #    bda[ins.label] += 1
            #for key in sorted(bda.keys()):
            #    print key,"\t",bda[key]
            #generate windows
            instance_tfz = []
            #print len(meta_instances)
            for instance in meta_instances:
                instance_tfz.append(([instance],instance.tfz))
            windows = time_functions.extract_sliding_window_instances(instance_tfz,windowsize,slider)
            #for each file with classifications
            for scorefile in event_scores[event_file]:
                #print scorefile
                #link classifications to instances
                if self.input_type == "knn":
                    classification_info = codecs.open(scorefile,"r","utf-8")
                    scorefile_context = scorefile.split("/")
                    validation = scorefile_context[-2]
                    if filt and not validation in filt:
                        continue
                    k = scorefile_context[-1]
                    print validation,k
                    self.set_instances_knn(classification_info.readlines(),meta_instances,hidden)
                    classification_info.close()
                elif self.input_type == "lcs":
                    self.set_instances_lcs(scorefile,"standard")
                    scoretokens = scorefile.split("/")
                    validation = scoretokens[-2]
                    #print validation
                    if filt and not validation in filt:
                        continue
                    scoretokens[-1] = "timelabels"
                    timelabel_score_file = "/".join(scoretokens) + "/test.rnk"
                    self.set_instances_lcs(timelabel_score_file,"timelabel")
                #elif self.input_type == "meta":
                 #   classification_info = codecs.open(scorefile,"r","utf-8")
                    #for i,line in enumerate(classification_info).readlines():
                        #tokens = line.split("\t")
                        #if tokens[3] != "nt":
                        #    print tokens[3]
                        #instance = meta_instances[i]

                        #instance.set_classification([tokens[3]])
                  #  if len(classification_info.readlines()) != len(meta_instances):
                   #     print len(classification_info),len(meta_instances),"classification and meta do not align, exiting program..."
                    #for i,line in enumerate(classification_info.readlines()):
                      #  tokens = line.split("\t")
                     #   instance = meta_instances[i]
                       # instance.set_classification([tokens[3]])
                    #classification_info.close()
                #for each window
                testwindows = []
                num_tweets = 0
                if output == "rmse":
                    for window in windows:
                        testwindow = Evalset.Instance()
                        testwindow.set_tfz(window[1])
                        if plot:
                            window_tweet = window[0][-1]
                            window_datetime = time_functions.return_datetime(window_tweet.date,window_tweet.time,setting="vs")
                            tfz = time_functions.timerel(event_time[event][0],window_datetime,"hour")
                            testwindow.set_tfz(tfz)
                        num_tweets += len(window[0])
                        if num_tweets <= threshold:
                            testwindow.set_classification("abstain")
                        else:
                            testwindow.set_label(window[0][-1].timelabel)
                            if self.input_type == "meta":
                                estimations = defaultdict(int)
                                for instance in window[0]:
                                    try:
                                        if not instance.classification[0] == "nt":
                                            estimations[instance.classification[0]] += 1
                                    except IndexError:
                                        continue
                                ranked_estimations = sorted(estimations,key = estimations.get,reverse=True)
                                if len(ranked_estimations) == 0:
                                    testwindow.set_classification("abstain")
                                else:
                                    majority = ranked_estimations[0]
                                    if len(ranked_estimations) == 1 or estimations[majority] > estimations[ranked_estimations[1]]:
                                        if majority == "early":
                                            testwindow.set_classification("abstain")
                                        else:
                                            testwindow.set_classification(majority)
                                    else:
                                        testwindow.set_classification("abstain")
                            
                            else:
                                predictions = defaultdict(int)
                                predictions_other = defaultdict(int)
                                score_prediction = defaultdict(list)
                                
                                #check for majority
                                for instance in window[0]:

                                    try:
                                        if instance.classification[0] in ["early","during","after"]:
                                            predictions[instance.classification[0]] += 1
                                        else:
                                            predictions["tte"] += 1
                                            predictions_other[instance.classification[0]] += 1
                                            score_prediction[instance.classification[1]].append(instance.classification[0])
                                    except IndexError:
                                        print "window IE",instance.classification
                                        #continue
                                                                
                                majority_rank = sorted(predictions,key = predictions.get,reverse=True)
                                if majority_rank[0] == "tte" or predictions["tte"] == predictions[majority_rank[0]]:
                                    tte_rank = sorted(predictions_other,key=predictions_other.get,reverse=True)
                                    score_rank = sorted(score_prediction.keys(),reverse=True)
                                    estimation = self.extract_timelabel(predictions_other,tte_rank,score_prediction,score_rank)
                                    testwindow.set_classification(estimation[0])
                                else:
                                    testwindow.set_classification("abstain")
                        testwindows.append(testwindow)
                    if plot:
                        plotfile = "/".join(outfile.split("/")[:-1]) + "/" + self.input_type + "_" + event + "_plot.png"
                        evaluation = self.calculate_rmse(testwindows,plotfile)
                    else:
                        evaluation = self.calculate_rmse(testwindows)
                    if self.input_type == "meta":
                        out_dict[event] = evaluation[-4:]
                    elif self.input_type == "knn":
                        out_dict[event + "_" + validation + "_" + k] = evaluation[-4:]
                    elif self.input_type == "lcs":
                        out_dict[event + "_" + validation] = evaluation[-4:]
                
                elif output == "fscore":
                    print "fscore"
                    ce = proy_evaluation.ClassEvaluation()
                    for window in windows:
                        testwindow = Evalset.Instance()
                        testwindow.set_tfz(window[1])
                        label = (window[0][-1].label)
                        if label == "during" or label == "after":
                            label = "late"
                        else:
                            if window[0][-1].timelabel == "early":
                                label = "early"
                            else:
                                label = "before"
                        if self.input_type == "meta":
                            estimations = defaultdict(int)
                            for instance in window[0]:
                                try:
                                    if not instance.classification[0] == "nt":
                                        estimations[instance.classification[0]] += 1
                                except IndexError:
                                    continue
                            ranked_estimations = sorted(estimations,key = estimations.get,reverse=True)
                            if len(ranked_estimations) == 0:
                                classification = "late"
                            else:
                                majority = ranked_estimations[0]
                                if len(ranked_estimations) == 1 or estimations[majority] > estimations[ranked_estimations[1]]:
                                    if majority == "early":
                                        classification = "early"
                                    else:
                                        classification = "before"
                                else:
                                    classification = "late"
                            
                        else:
                            predictions = defaultdict(int)
                            predictions_other = defaultdict(int)
                            score_prediction = defaultdict(list)
                            #check for majority
                            
                            for instance in window[0]:
                                try:
                                    if instance.classification == "early":
                                        print instance.classification[0]
                                    if instance.classification[0] in ["early","during","after"]:
                                        predictions[instance.classification[0]] += 1
                                    else:
                                        predictions["before"] += 1
                                except IndexError:
                                    continue
                            majority_rank = sorted(predictions,key = predictions.get,reverse=True)
                            if majority_rank[0] == "before" or predictions["before"] == predictions[majority_rank[0]]:
                                classification = "before"
                            else:
                                if majority_rank[0] == "early" or predictions["early"] == predictions[majority_rank[0]]:
                                    classification = "early"
                                else:
                                    classification = "late"
                        ce.append(label,classification)
                    for label in sorted(list(set(ce.goals))):
                        out_dict[label]["precision"].append(round(ce.precision(cls=label),2))
                        out_dict[label]["recall"].append(round(ce.recall(cls=label),2))
                        out_dict[label]["f1"].append(round(ce.fscore(cls=label),2))

        if output == "rmse":
            rmses = defaultdict(list)
            if self.input_type == "meta":
                for v in sorted(out_dict.keys()):
                    scores = out_dict[v]
                    if scores[0] != "-":
                        rmses[v].extend(scores)
                    out.write(str(scores[0]) + "\t" + str(scores[1]) + "\t")
            elif self.input_type == "knn":
                for v in sorted(out_dict.keys()):
                    scores = out_dict[v]
                    if scores[0] != "-":
                        rmses[v].extend(scores)
                    out.write(str(scores[0]) + "\t" + str(scores[1]) + "\t")
                        
            elif self.input_type == "lcs":
                for v in sorted(out_dict.keys()):
                    scores = out_dict[v]
                    if scores[0] != "-":
                        rmses[v] = scores
                    out.write(str(scores[0]) + "\t" + str(scores[1]) + "\t")
            
            scorelists = [[],[],[]]
            for x in rmses.keys():
                for i,score in enumerate(rmses[x][:3]):
                    if not score == "-":
                        scorelists[i].append(score)
            out.write("\nmean " + x + "\t" + str(round(sum(scorelists[0])/len(scorelists[0]),2)) + "\t" + str(round(sum(scorelists[1])/len(scorelists[1]),2)) + "\t" + str(sum(scorelists[2])) + "\n")
        
        elif output == "fscore":
            for label in sorted(out_dict.keys()):
                for ever in sorted(out_dict[label].keys()):
                    entries = out_dict[label][ever]
                    mean = round(sum(entries) / len(entries),2)
                    #st_dev = 0
                    #for entry in entries:
                    #    dif = entry - mean
                    #    sdif = dif * dif 
                    #    st_dev += sdif
                    #st_dev = round(math.sqrt(st_dev / len(entries)),2)
                    out.write(str(mean) + "\t")


             
    def extract_top(self,outfile,classification,top_n,files):
        out_write = open(outfile,"w")
        instances = defaultdict(int)
        for i in self.instances:
            if i.classification == classification:
                if i.fp:
                    instances[i] = i.score

        for index,instance in enumerate(sorted(instances, key=instances.get, reverse=True)[:top_n]):
            fileread = open(files + instance.fname,"r").readlines()    
            words = []
            for line in fileread:
                term = line.strip()
                if re.search("_",term):
                    break
                words.append(term)
            text = " ".join(words)
            out_write.write(str(instance.score) + "\t" + text + "\n")    
        out_write.close()
    
    def generate_timebuckets(self,metafiles,eventfiles):
        print "generating event-time hash..."
        # generate event-time hash
        event_time = dict({})
        for eventfile in eventfiles:
            event_time.update(time_functions.generate_event_time_hash(eventfile))

        print "setting tweet_to_event-time..."
        # for each tweet
        for metafile in metafiles:
            metafile = open(metafile,"r")
            for tweet in metafile:
                # link to event
                tokens = tweet.split(" ")
                filename = tokens[0].strip()
                keyterm = tokens[1]
                tweetdate = tokens[2]
                tweettime = tokens[3]
                tweetdatetime = time_functions.return_datetime(tweetdate,tweettime,"vs")
                eventdatetime_begin = event_time[keyterm][0]
                eventdatetime_end = event_time[keyterm][1]
                if (eventdatetime_begin - tweetdatetime) < event_time[keyterm][2]:
                    #print eventdatetime_begin,tweetdatetime
                    try:                        
                        instance = self.name_instance[filename]
                        if not instance.label == "other":
                            self.time_buckets[0].append(instance)
                    except KeyError:
                        continue
                else:
                    eventdatetime_begin = (eventdatetime_begin - event_time[keyterm][2]) + datetime.timedelta(days = 1) 
                    tweetevent_time = time_functions.timerel(eventdatetime_begin,tweetdatetime,"day") * -1
                    #print tweetevent_time
                    if tweetevent_time < 0:
                        try:
                            instance = self.name_instance[filename]
                            #print instance.label,tweetevent_time
                            if not instance.label == "other":
                                self.time_buckets[tweetevent_time].append(instance)
                        except KeyError:
                            continue
                        
        print "sorting instances..."
        #sort instances
        #self.instances = sorted(self.instances,key = lambda x: x.time_to_event)
        #for tte in sorted(self.time_buckets.keys()):
        #    print tte,len(self.time_buckets[tte])
    #def prune_instances_label(self,label):
    #    new_instances = []
    #    for instance in self.instances:
    #        if not instance.label == label:

    
    def plot_instances_time(self,plotfile):
        # generate coordinates
        x = []
        y = []
        ce = evaluation.ClassEvaluation()
        for tte in sorted(self.time_buckets.keys()):
            if tte > -20:
                for instance in self.time_buckets[tte]:
                    #print instance.label,instance.classification
                    ce.append(instance.label,instance.classification)
                #labels = list(set(ce.goals))
                #for label in labels:
                #    if re.search("-",label):
                #        window = re.search("(\d+)-(\d+)",label)
                #        first = int(window.groups()[0]) * - 1
                #        last = int(window.groups()[1]) * -1
                #        if tte <= first and tte >= last:
                #            print label
                #            f1 = ce.fscore(label)
                #    else:
                #        if int(label) * -1 == tte:
                #            f1 = ce.fscore(label)
                f1 = ce.fscore()
                x.append(tte)
                y.append(f1)
        plt.plot(x,y)
        #plt.legend(legend,loc = "upper right",ncol = 2)
        plt.ylabel("Micro-f1 score")
        plt.xlabel("Time-to-event in days")
        #plt.title("\'Micro-f1 score at\' as event time nears")
        plt.savefig(plotfile)
        
                 
    def print_results(self,outfile):

        out_write = open(outfile,"w")
        out_write.write("\t".join(["Class","Precision","Recall","F1","TPR","FPR","AUC","Samples","Classifications","Correct"]) + "\n")
        #rows = [["Class","Precision","Recall","F1","TPR","FPR","AUC","Samples","Classifications","Correct"]]
        ce = evaluation.ClassEvaluation()
        for instance in self.instances:
            ce.append(instance.label,instance.classification)
        for label in sorted(list(set(ce.goals))):
            if not label == "":
                table = [label,str(round(ce.precision(cls=label),2)),str(round(ce.recall(cls=label),2)),str(round(ce.fscore(cls=label),2))]
                table.extend([str(round(ce.tp_rate(cls=label),2)),str(round(ce.fp_rate(cls=label),2)),str(round(auc([0,round(ce.fp_rate(cls=label),2),1], [0,round(ce.tp_rate(cls=label),2),1]),2))])
                table.extend([str((ce.tp[label] + ce.fn[label])),str((ce.tp[label] + ce.fp[label])),str(ce.tp[label])])
                #rows.append(table)
                out_write.write("\t".join(table) + "\n")

    class Instance():
        
        def __init__(self):
            self.fname = ""
            self.id = ""
            self.label = ""
            self.timelabel = ""
            self.event = ""
            self.classification = ""
            self.tfz = ""
            self.time_to_event = 0
            self.score = 0
            self.fp = False
            self.tp = False
            self.fn = False
            self.past_window = []
            self.dict = {}
    
        def set_name(self,name):
            self.fname = name
            
        def set_id(self,tid):
            self.id = tid
            
        def set_label(self,label):
            self.label = label
        
        def set_classification(self,classification):
            self.classification = classification

        def set_event(self,event):
            self.event = event

        def set_tfz(self,tfz):
            self.tfz = tfz

        def set_score(self,score):
            self.score = score

        def set_timelabel(self,tl):
            self.timelabel = tl

        def set_fp(self):
            self.fp = True

        def set_tp(self):
            self.tp = True

        def set_fn(self):
            self.fn = True
            
        def set_time(self,time):
            self.time_to_event = time
            
        def set_past_window(self,instances):
            self.past_window = instances
            
        def set_date(self,date):
            self.date = date
            
        def set_time(self,time):
            self.time = time
    
