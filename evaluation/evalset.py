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

    def __init__(self):
        self.instances = []
        # self.results = defaultdict(list)

    # def set_vocabulary(self,vocabfile):
    #     self.vocabulary = {}
    #     vocab = codecs.open(vocabfile,"r","utf-8")
    #     for line in vocab.readlines():
    #         tokens = line.strip().split("\t")
    #         self.vocabulary[tokens[0]] = tokens[1]
    #     vocab.close()

    def add_instances(self,instances):
        for instance_line in instances:
            instance = Evalset.Instance()
            instance.set_label(instance_line[0])
            instance.set_classification(instance_line[1])
            self.instances.append(instance)

    def calculate_rmse(self):
        estimation_sequence = []
        responsiveness_vals = []
        rmse_vals = []
        plot_vals = defaultdict(list)
        for instance in self.instances:
            target = instance.label
            prediction = instance.classification
            estimation_sequence.append((target,prediction))
            if not target == "during" and not target == "after":
                if prediction == "during" or prediction == "after":
                    responsiveness_vals.append(0)
                else:
                    if int(prediction) > 0:
                        responsiveness_vals.append(0)
                    else:
                        responsiveness_vals.append(1)
                        dif = abs(int(target) - int(prediction))
                        rmse_vals.append(dif*dif)
                        plot_vals[int(target)].append(dif)
        responsiveness = round(sum(responsiveness_vals)/len(responsiveness_vals),2)  
        try:
            rmse = round(math.sqrt(sum(rmse_vals)/len(rmse_vals)),2)
        except:
            rmse = 0
        plot_vals_mean = [(v,(sum(plot_vals[v]) / len(plot_vals[v]))) for v in sorted(plot_vals.keys(),reverse=True)]
        print plot_vals_mean
        exit()
        return (rmse,responsiveness,plot_vals)

    def extract_sliding_window_instances(self,window,incre):
        #make tfz hash
        tfz_instances = defaultdict(list)            
        for instance in self.instances:
#            print instance.dict
            tfz_instances[int(instance.dict["tfz"])].append(instance)
        highest_tfz = sorted(tfz_instances.keys())[-1]
        slider = [0,0+window]
        tfz_set = tfz_instances.keys()
        windows = []
        while slider[1] <= highest_tfz:
            windowtweets = []
            slider_range = range(slider[0],slider[1]+1)
            for tfz in slider_range:
                if tfz in tfz_set:            
                    instances = tfz_instances[tfz]
                    windowtweets.extend(tfz_instances[tfz])
            if len(windowtweets) > 0:
                window = self.Window(windowtweets,seen_instances)
                windows.append(window)
            slider[0] += incre
            slider[1] += incre
        self.windows = windows

    # def set_meta(self,metafile,metadict,input_type):
    #     meta = codecs.open(metafile,"r","utf-8")
    #     if input_type == "lcs":
    #         self.name_instance = {}
    #     for line in meta.readlines():
    #         instance = Evalset.Instance()
    #         tokens = line.strip().split("\t")
    #         for meta_info in metadict.keys():
    #             instance.dict[meta_info] = tokens[metadict[meta_info]]
    #         if input_type == "lcs":
    #             self.name_instance[instance.dict["name"]] = instance
    #             instance.set_label(instance.dict["label"])
    #         self.instances.append(instance)
    #     meta.close()

    def set_instances_lcs(self,classificationfile,labelfile=False,timelabels = False,threshold = False):         
   
        if labelfile:
            self.name_instance = {}
            labels = codecs.open(labelfile,"r","utf-8")
            for line in labels.readlines():
                instance = Evalset.Instance()
                tokens = line.strip().split(" ")
                self.name_instance[tokens[0]] = instance
                instance.set_label(tokens[1])
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
                instance.set_classification(classification)
                if classification != instance.label:
                    instance.set_fp()
                    instance.set_fn()
                else:
                    instance.set_tp() 
                instance.set_score(score)
        classifications.close()

        if timelabels:
            timelabel_classifications = codecs.open("/".join(classificationfile.split("/")[:-1]) + "/timelabels/test.rnk","r","utf-8")
            for line in timelabel_classifications.readlines():
                tokens = line.split("  ")
                filename = tokens[0].strip()
                instance = self.name_instance[filename]
                scores = tokens[1]
                classification_score = scores.split(" ")[0].split(":")
                if not (threshold and re.search(r"\?",classification_score[0])):  
                    classification = re.sub("\?","",classification_score[0])
                    score = float(classification_score[1])
                    instance.set_time_classification((classification,score))
            timelabel_classifications.close()            
    
    def set_instances_knn(self,classification_file,hidden=False,vocabulary=False):
        #extract information
        cl_open = open(classification_file)
        classifications_nn = defaultdict(list)
        classifications = []
        nn = []
        test = ""
        if vocabulary:
            self.set_vocabulary(vocabulary)
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
        # print classifications_nn
        cl_open.close()
        if len(classifications) != len(self.instances):
            print len(classifications),len(self.instances),"classification and meta do not align, exiting program..."
            exit()
        #set classification
        for i,line in enumerate(classifications):
            instance = self.instances[i]
            tokens = line.split("==")[1].split("  ")[1].split(" ")
            if not instance.dict["label"] == tokens[0]:
                print "error: no label match; exiting program"
                exit()
            instance.set_label(tokens[0])
            classification = tokens[1]
            instance.set_classification(classification)
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
                        timelabel_index = neighbour_tokens[-2]
                        timelabel = self.vocabulary[timelabel_index]
                        timelabel_freq[timelabel] += 1
                        score_timelabel[score].append(timelabel)
                
                timelabel_rank = sorted(timelabel_freq,key=timelabel_freq.get, reverse=True)
                score_rank = sorted(score_timelabel.keys(),reverse = True)
                selected_tl = self.extract_timelabel(timelabel_freq,timelabel_rank,score_timelabel,score_rank)
                instance.set_time_classification(selected_tl)
            else:
                # print neighbours
                for neighbour in neighbours:
                    label = neighbour.split(" ")[1].split(",")[-1]
                    score = float(neighbour.split("  ")[1])
                    label_scores[label].append(score)
                highest_score = sorted(label_scores[classification],reverse=True)[0]
                instance.set_time_classification((classification,highest_score))

    def set_instances_ibt(self,classificationfile):
        classifications = codecs.open(classificationfile,"r","utf-8")
        for i,estimation in enumerate(classifications.read().split(" ")):
            self.instances[i].set_time_classification((estimation,0))





    # def calculate_rmse(self):
    #     estimation_sequence = []
    #     correct_abstain_vals = [0,0]
    #     responsiveness_vals = [0,0]
    #     rmse_vals = [0,0]
    #     for window in self.windows:
    #         target = window.label
    #         prediction = window.classification
    #         estimation_sequence.append((target,prediction))
    #         if target == "-" or target == "early":
    #             correct_abstain_vals[0] += 1
    #             if prediction == "abstain":
    #                 correct_abstain_vals[1] += 1
    #         else:
    #             responsiveness_vals[0] += 1
    #             rmse_vals[0] += 1
    #             #before += 1
    #             if prediction == "abstain":
    #                 continue
    #                 window.set_error("NaN")
    #             else:
    #                 responsiveness_vals[1] += 1
    #                 target = int(target)
    #                 prediction = int(prediction)
    #                 dif = target - prediction
    #                 if dif < 0:
    #                     dif = dif * -1
    #                 window.set_error(str(dif))
    #                 se = dif * dif
    #                 rmse_vals[1] += se
    #     try:
    #         correct_abstain = round(correct_abstain_vals[1]/correct_abstain_vals[0],2)
    #     except ZeroDivisionError:
    #         correct_abstain = 0
    #     responsiveness = round(responsiveness_vals[1]/responsiveness_vals[0],2)  
    #     rmse = round(math.sqrt(rmse_vals[1] / rmse_vals[0]),1)

    #     return (estimation_sequence,rmse,responsiveness,correct_abstain)

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
       
    def plot_instances_time(self,plotfile):
        # generate coordinates
        x = []
        y = []
        ce = evaluation.ClassEvaluation()
        for tte in sorted(self.time_buckets.keys()):
            if tte > -20:
                for instance in self.time_buckets[tte]:
                    ce.append(instance.label,instance.classification)
                f1 = ce.fscore()
                x.append(tte)
                y.append(f1)
        plt.plot(x,y)
        #plt.legend(legend,loc = "upper right",ncol = 2)
        plt.ylabel("Micro-f1 score")
        plt.xlabel("Time-to-event in days")
        #plt.title("\'Micro-f1 score at\' as event time nears")
        plt.savefig(plotfile)
        
                 
    def return_results(self):
        # out_write = open(outfile,"w")
        # out_write.write("\t".join(["Class","Precision","Recall","F1","TPR","FPR","AUC","Samples","Classifications","Correct"]) + "\n")
        table = [["Class","Precision","Recall","F1","TPR","FPR","AUC","Samples","Classifications","Correct"]]
        #rows = [["Class","Precision","Recall","F1","TPR","FPR","AUC","Samples","Classifications","Correct"]]
        ce = evaluation.ClassEvaluation()
        for instance in self.instances:
            # print instance.label
            ce.append(instance.label,instance.classification)
        for label in sorted(list(set(ce.goals))):
            # print label
            if not label == "":
                row = [label,round(ce.precision(cls=label),2),round(ce.recall(cls=label),2),round(ce.fscore(cls=label),2)]
                row.extend([round(ce.tp_rate(cls=label),2),round(ce.fp_rate(cls=label),2),round(auc([0,round(ce.fp_rate(cls=label),2),1],[0,round(ce.tp_rate(cls=label),2),1]),2)])
                row.extend([(ce.tp[label] + ce.fn[label]),(ce.tp[label] + ce.fp[label]),ce.tp[label]])
                #rows.append(table)
                # out_write.write("\t".join(table) + "\n")
                table.append(row)
        micro_row = [round(ce.precision(),2),round(ce.recall(),2),round(ce.fscore(),2)]
        micro_row.extend([round(ce.tp_rate(),2),round(ce.fp_rate(),2),round(auc([0,round(ce.fp_rate(),2),1],[0,round(ce.tp_rate(),2),1]),2)])
        micro_row.extend([len(ce.observations),len(ce.observations),""])
        table.append(micro_row)
        return table

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

        def set_time_classification(self,tc):
            self.time_classification = tc

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
    
    class Window():

        def __init__(self,instances,seen):
            self.instances = instances
            self.label = instances[-1].dict["timelabel"]
            self.start = instances[0].dict["tfz"]
            self.end = instances[-1].dict["tfz"]
            self.seen = seen
            self.classification = False

        def set_classification(self,classification):
            self.classification = classification

        def set_error(self,error):
            self.error = error

