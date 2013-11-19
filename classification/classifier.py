#! /usr/bin/env python

from __future__ import division
import codecs
import os
from collections import defaultdict
import math
import numpy
#from sklearn import svm
from scipy.sparse import *
from scipy import *
from pylab import *
import re
import itertools
import glob
import multiprocessing
import gen_functions
import lineconverter
import weight_features

class Classifier():

    def __init__(self,trainlist,testlist,metalist=False,directory=False, vocabulary=False):
        self.training=trainlist
        self.test=testlist
        self.meta=metalist
        self.directory=directory
        self.feature_info=vocabulary

    def top_features(self,n):
        #generate feature_frequency dict
        feature_freq=defaultdict(int)
        # if classifier == "knn":
        for instance in self.training:
            features=instance["features"]
            for feature in features:
                feature_freq[feature] += 1
        sorted_feature_freq=sorted(feature_freq, key=feature_freq.get, reverse=True)
        boundary=0
        feature_status = {}
        for i,f in enumerate(sorted_feature_freq):
            if i <= n:
                feature_status[f] = True
            else:
                feature_status[f] = False
        for instance in self.training:
            new_features = []
            for f in instance["features"]:
                if feature_status[f]:
                    new_features.append(f)
            instance["features"] = new_features
        # for f in sorted_feature_freq[i:]
        #     feature_status[f] = False
        # print "num features after pruning: ", i
        # for instance in self.training + self.test:
        #     for feature in instance[]
        # # if classifier == "knn":
        #     #generate new indexes and make a new feature_info 
        # self.adjust_index_space(sorted_feature_freq,feature_freq,boundary)
        
        # elif classifier == "lcs":
        #     #generate stoplist
        #     self.stoplist=[]
        #     for feature in sorted_feature_freq[:boundary]:
        #         self.stoplist.append(feature)

    # def half_sample(self):
    #     label_instances = defaultdict(list)
    #     label_frequency = defaultdict(int)
    #     current_label = ""
    #     label_order = []
    #     for instance in self.training:     
    #         label = instance["label"]
    #         label_frequency[label] += 1
    #         label_instances[label].append(instance)
    #         if label != current_label:
    #             label_order.append(label)
    #             current_label = label
    #     sorted_labels = sorted(label_frequency, key=label_frequency.get, reverse=True)
    #     lowest_freq = label_frequency[sorted_labels[-1]]
    #     new_training = []
    #     for label in label_order:
    #         print label
    #         if label == sorted_labels[-1]:
    #             new_training.extend(label_instances[label])
    #         else:
    #             lc = lineconverter.Lineconverter(label_instances[label])
    #             sample = lc.extract_sample(lowest_freq)
    #             new_training.extend(sample)
    #     self.training = new_training

    def index_features(self,top_frequency = -1,ind = 1):
        feature_frequency=defaultdict(int)
        self.feature_info={}      
        for i,instance in enumerate(self.training):
            for feature in instance["features"]:
                feature_frequency[feature] += 1
        #feature_frequency_sorted = sorted(feature_frequency.items(), key=lambda x: x[1],reverse=True)
        for i,feature in enumerate(feature_frequency.keys()):
            self.feature_info[feature]=i+ind
        #zerolist = [0] * len(feature_frequency_sorted[:top_frequency])
        instances = self.training + self.test
        for instance in instances:
            instance["sparse"] = []
            feature_freq = defaultdict(int)
            for feature in instance["features"]:
                try:
                    index = self.feature_info[feature]
                    feature_freq[index] += 1
                except KeyError:
                    continue
            for index in sorted(feature_freq.keys()):
                instance["sparse"].append(index)
        
        # training_instances = [x["sparse"] for x in self.training]
        # training = csr_matrix(training_instances,dtype=float64)
        # test_instances = [x["sparse"] for x in self.test]
        # test = csr_matrix(test_instances,dtype=float64)
        # return training,test

    def generate_paired_classifiers(self):
        #obtain feature and label frequencies
        label_frequency, feature_frequency, feature_label_frequency = weight_features.generate_frequencies(self.training,"sparse")
        #feature_label_frequency = defaultdict(lambda : defaultdict(int))
        #make a list of each possible label pair
        labels = label_frequency.keys()
        pairs = []
        perm = itertools.combinations(labels,2)
        for entry in perm:
            pairs.append(list(entry))
        #generate bns-values per classifier
        for pair in pairs:
            feature_bns = weight_features.bns(pair,label_frequency, feature_label_frequency)
            positive = [instance for instance in self.training if instance["label"] == pair[0]]
            negative = [instance for instance in self.training if instance["label"] == pair[1]]
            #up- and downsample to equalize numbers
            dif = abs(len(positive) - len(negative))
            samplesize = int(dif/2)
            lcp = lineconverter.Lineconverter(positive)
            lcn = lineconverter.Lineconverter(negative)
            if len(positive) > len(negative):
                lcp.sample(samplesize)
                lcn.sample(samplesize,sample_type="up")
            else:
                lcp.sample(samplesize,sample_type="up")
                lcn.sample(samplesize)
            positive = lcp.lines
            negative = lcn.lines
            training = positive + negative
            if re.search("-",pair[0]):
                pair0 = re.sub("-","minus",pair[0])
            else:
                pair0 = pair[0]
            pairstring = pair0 + "_" + pair[1]
            d = self.directory + pairstring + "/"
            os.system("mkdir " + d)
            train = open(d + "train","w")
            test = open(d + "test", "w")
            args = [[training,train],[self.test,test]]
            for arg in args:
                for instance in arg[0]:
                    features = list(set(instance["sparse"]))
                    if instance["label"] == pair[0]:
                        outstring = "1"
                    else:
                        outstring = "-1"
                    for feature in sorted(features):
                        try:
                            outstring += (" " + str(feature) + ":" + str(feature_bns[feature]))
                        except KeyError:
                            continue
                    outstring += "\n"
                    arg[1].write(outstring)
                arg[1].close()

        # i = 0
        # while (i+32) < len(pairs):
        #     try:
        #         shift = pairs[i:i+16]
        #     except IndexError:
        #         shift = pairs[i:]
        #     i += 16
        #     for p in shift:
        #         m = multiprocessing.Process(target=classify_pair,args=[p])
        #         m.start()

    # def adjust_index_space(self,ranked_list,value_dict,boundary):
    #     new_feature_info={}
    #     feature_status={}        
        
    #     #assign new feature_info indexes based on the ranked list
    #     for i,old_index in enumerate(ranked_list[:boundary]):
    #         new_index=str(i+1)
    #         new_feature_info[new_index]=self.feature_info[old_index] + [str(value_dict[old_index])]
    #         feature_status[old_index]=new_index
    #     self.feature_info=new_feature_info
    #     #set status of all pruned features to False
    #     for feature_index in ranked_list[boundary:]:
    #         feature_status[feature_index]=False

    #     #adjust instances
    #     index = 0
    #     while index < len(self.training):
    #         instance = self.training[index]
    #         new_features=[]
    #         features = instance["features"]
    #         for feature in features:
    #             if feature_status[feature]:
    #                 new_index=int(feature_status[feature])
    #                 new_features.append(new_index)
    #         if len(new_features) == 0:
    #             self.training.pop(index)
    #         else:
    #             new_features_str = [str(feature) for feature in sorted(new_features)]
    #             self.training[index]["features"]=new_features_str
    #             index += 1
            
    #     index = 0
    #     while index < len(self.test): 
    #         instance = self.test[index]
    #         new_features=[]
    #         features=instance["features"]
    #         for feature in features:
    #             try: 
    #                 if feature_status[feature]:
    #                     new_index=int(feature_status[feature])
    #                     new_features.append(new_index)
    #             except KeyError:
    #                 continue
    #         if len(new_features) == 0:
    #             self.test.pop(index)
    #             self.meta.pop(index)
    #         else:   
    #             new_features_str = [str(feature) for feature in sorted(new_features)]
    #             self.test[index]["features"]=new_features_str
    #             index += 1

    #def pca(self):

    # def select_features(self,num_features,prune,classifier):
    #     #make a file of the instances and perform infogain weighting
    #     feature_weights=self.infogain(classifier,prune)
    #     selected_features=sorted(feature_weights, key=feature_weights.get, reverse=True)    
    #     if classifier == "knn":
    #         self.adjust_index_space(selected_features,feature_weights,num_features)
    #     elif classifier == "lcs":
    #         self.stoplist.extend(selected_features[num_features:])

    def classify_pairs(self,pairs,classifier):
        for pair in pairs:
            tdir = os.getcwd() + "/" + pair.split("/")[-1] + "/"
            os.system("mkdir " + tdir)
            os.chdir(tdir)
            os.system("mv " + pair + "/train .")
            os.system("mv " + pair + "/test .")
            if classifier == "svm":
                os.system("paramsearch svmlight .")
                os.system("runfull-svmlight train test")
            os.system("mv * " + pair + "/")
            os.chdir("..")
            os.system("rm -r " + tdir)

    def perform_svm(self):
        #generate sparse input
        self.index_features()
        #generate classifiers
        self.generate_paired_classifiers()

        exit()
        pairs = list(glob.iglob(self.directory + '*'))
        chunks = gen_functions.make_chunks(pairs)
        processes = []
        for chunk in chunks:
            p = multiprocessing.Process(target=classify_pairs,args=[chunk])
            processes.append(p)
            p.start()
        for p in processes:
            p.join()

        #clf = svm.SVC()
        #clf.fit(training,labels)
        #print clf.n_support_
        #print clf.predict(test)
        #for i,t in enumerate(self.test):        
        #    print t["label"],clf.predict(test[i])

    def perform_lcs(self,args,prune,select,timelabels):
        
        def performer():
            os.system("lcs --verbose --directory " + classification_dir)
            os.system("mv " + classification_dir + "data " + self.directory)
            os.system("mv " + classification_dir + "test.* " + self.directory)
            os.system("mv " + classification_dir + "lcsg* " + self.directory)
            os.system("mv " + classification_dir + "lcsd* " + self.directory)
            os.system("mv " + classification_dir + "lcs.log " + self.directory)
            os.system("mv " + classification_dir + "train " + self.directory)
            os.system("mv " + classification_dir + "test " + self.directory)
            os.system("mv " + classification_dir + "stoplist.txt " + self.directory)
            os.system("mv " + classification_dir + "keeplist.txt " + self.directory)
            os.system("mv " + classification_dir + "index " + self.directory)
        
        try:
            classification_dir=args[0]
        except IndexError:
            print "not enough arguments for LCS, exiting program..."
            exit()
        
        if prune:
            self.prune_features(int(prune),"lcs")
        if select:
            self.select_features(int(select),int(prune),"lcs")
        
        train=codecs.open(classification_dir + "train","w","utf-8")
        for t in self.training:
#            print t
            train.write(" ".join([t["features"][0],t["label"]]) + "\n")
        train.close()
        test=codecs.open(classification_dir + "test","w","utf-8")
        for t in self.test:
            test.write(" ".join([t["features"][0],t["label"]]) + "\n")
        test.close()
        meta = self.directory + "meta"
        metaout = codecs.open(meta,"w","utf-8")
        for line in self.meta:
            metaout.write(line)
        if prune or select:
            stoplist=codecs.open(classification_dir + "stoplist.txt","w","utf-8")
            for feature in self.stoplist:
                stoplist.write(feature + "\n")
            stoplist.close()
        performer()
        
        if timelabels:
            self.directory=self.directory + "timelabels/"
            os.system("mkdir " + self.directory)
            train=codecs.open(classification_dir + "train","w","utf-8")
            for i,t in enumerate(self.training):
                label = t["label"]
                if label == "before":
                    tl=t["meta"][4]
                    train.write(" ".join([t["features"][0],tl]) + "\n")
            train.close()
            test=codecs.open(classification_dir + "test","w","utf-8")
            for i,t in enumerate(self.test):
                tl=t["meta"][4]
                test.write(" ".join([t["features"][0],tl]) + "\n")
            test.close()
            if prune or select:
                stoplist=codecs.open(classification_dir + "stoplist.txt","w","utf-8")
                for feature in self.stoplist:
                    stoplist.write(feature + "\n")
                stoplist.close()
            performer()

    def perform_knn(self,klist,prune,select,timelabels):
        
        # if prune:
        #     print "pruning features..."
        #     self.prune_features(int(prune),"knn")
        # if select:
        #     print "selecting features..."
        #     self.select_features(int(select),int(prune),"knn")

        #if set on, add timelabels as features to instances
        if timelabels:
            time_label_vocab={}
            timelabel_list = []
            #generate a list of all time labels
            for instance in self.training:
                if instance["label"] == "before":
                    timelabel = instance["meta"][3]
                    timelabel_list.append(timelabel)
            time_label_set=set(timelabel_list)
            #make a new feature_info_dict ending with the timelabels as features  
            num_feats = len(self.feature_info.keys())
            for i,tl in enumerate(time_label_set):
                tl_index = str(num_feats+i)
                self.feature_info[tl_index]=[tl,"0","0"]
                time_label_vocab[tl]=tl_index
            #add the timelabel to each set of features
            for instance in self.training:
                if instance["label"] == "before":
                    timelabel = instance["meta"][3]
                    instance["features"].append(time_label_vocab[timelabel])
            for instance in self.test:
                if instance["label"] == "before":
                    timelabel = instance["meta"][3]
                    instance["features"].append(time_label_vocab[timelabel])
            #output a weightfile with feature weights
            weight = self.directory + "weights"
            try:
                weightout=codecs.open(weight,"w","utf-8")
            except IOError:
                os.system("mkdir " + "/".join(self.directory.split("/")[:-2]))
                os.system("mkdir " + "/".join(self.directory.split("/")[:-1]))
                weightout=codecs.open(weight,"w","utf-8")

            sorted_features = sorted([int(feature) for feature in self.feature_info.keys()])
            for numeric_feature in sorted_features:
                feature = str(numeric_feature)
                weightout.write(":" + feature + " STIMBLWEIGHT=" + str(self.feature_info[feature][-1]) + "\n")
            weightout.close()

        train = self.directory + "train"
        test = self.directory + "test"
        meta = self.directory + "meta"
        trainingout=open(train,"w")
        testout=open(test,"w")
        metaout=codecs.open(meta,"w","utf-8")
        feature_info_out=codecs.open(self.directory + "vocabulary","w","utf-8")
        for instance in self.training:
            trainingout.write(",".join(instance["features"]) + "," + instance["label"] + "\n")
        for instance in self.test:
            testout.write(",".join(instance["features"]) + "," + instance["label"] + "\n")
        for line in self.meta:
            metaout.write(line)
        sorted_features = sorted([int(feature) for feature in self.feature_info.keys()])
        for numeric_feature in sorted_features:
            feature = str(numeric_feature)
            feature_info_out.write(feature + "\t" + "\t".join(self.feature_info[feature]) + "\n")
        trainingout.close()
        testout.close()
        metaout.close()
        feature_info_out.close()

        print "performing knn..."
        for k in klist:
            print "k=",k
            classification=self.directory + "classification" + k + " .txt"
            if timelabels:
                os.system("stimbl -v -n " + str(len(self.feature_info)+1) + " -f " + train + " -W " + weight + " -i -D -m 3 -d 1 -k " + k + " < " + test + " > " + classification) 
            else:
                os.system("stimbl -n " + str(len(self.feature_info)+1) + " -f " + train + " -i -D -m 3 -d 1 -w 2 -k " + k + " < " + test + " > " + classification) 

    # def perform_lin_reg_event(self,args):
        
    #     def return_standard_deviation(windows):
    #         #print windows
    #         mean = sum(windows) / len(windows)
	   #  try:
    #             stdef = math.sqrt(sum([((window-mean) * (window-mean)) for window in windows]) / len(windows))
    #         except ValueError:
    #             stdef = 0
    #         return stdef

    #     def generate_hourly_sequence(instances,instance_dict):
    #         last_tfz = int(instances[-1]["meta"][4])
    #         instance_dict["sequence"] = []
    #         ef = instance_dict["sequence"]
    #         for hour in range(last_tfz+1):
    #             ef.append(0)
    #         est = True
    #         for instance in instances:
    #             tfz = int(instance["meta"][4])
    #             ef[tfz] += 1
    #             if est:
    #                 timelabel = instance["meta"][3]
    #                 if timelabel == "-":
    #                     instance_dict["start_time"] = tfz+1
    #                     est = False

    #     def generate_window_output(sequence,outdict,start_time,window,slider,log,test):
    #         #half = int(window/2)
    #         start = 0
    #         end = window 
    #         hist = [sum(sequence[start:start+window]),sum(sequence[start+window:start+(window*2)])]
    #         stdev_hist = return_standard_deviation(hist)
    #         start = start+(window*2)
    #         if test:
    #             stop = len(sequence)
    #         else:
    #             stop = start_time
    #         while start < stop:
    #             hist.append(sum(sequence[start:start+window]))
    #             if log == 1:
    #                 outdict["stdef"].append(return_standard_deviation(hist))
    #                 if hist[-1] == 0:
    #                     outdict["value"].append(0)
    #                 else:
    #                     outdict["value"].append(math.log(hist[-1]) / math.log(2))
    #             else:
    #                 outdict["value"].append(return_standard_deviation(hist))
    #                 outdict["stdef"].append(return_standard_deviation(hist))             
    #             outdict["target"].append(int((start_time - start+window)/24))
    #             start += window

    #     #generate input
    #     event_tweets = defaultdict(list)
    #     event_frequency = defaultdict(lambda : {}) 
    #     #generate a list of tweets for each event
    #     for instance in self.training:
    #         event = instance["meta"][1]
    #         event_tweets[event].append(instance)
    #     #generate an hourly sequence of tweet frequencies for each event
    #     for event in event_tweets.keys():
    #         tweets = event_tweets[event]
    #         generate_hourly_sequence(tweets,event_frequency[event])

    #     #slide through windows and generate x-y pairs
    #     window = int(args[0])
    #     slider = int(args[1])
    #     log = int(args[2])
    #     training = defaultdict(list)
    #     for event in event_frequency.keys():
    #         ef = event_frequency[event]["sequence"]
    #         event_time = event_frequency[event]["start_time"]
    #         generate_window_output(ef,training,event_time,window,slider,log,test=False)

    #     m = polyfit(training["value"],training["target"],1)

    #     #make estimations
    #     test_dict = {}
    #     generate_hourly_sequence(self.test,test_dict)
    #     test = defaultdict(list)
    #     generate_window_output(test_dict["sequence"],test,test_dict["start_time"],window,slider,log,test=True)
    #     for i,window in enumerate(test["value"]):
    #         estimation = (m[0]*window) + m[1]
    #         try:
    #             print test["stdef"][i]/test["stdef"][i-1],test["target"][i],round(estimation,2)
    #         except IndexError:
    #             print test["target"[i]],round(estimation,2)
