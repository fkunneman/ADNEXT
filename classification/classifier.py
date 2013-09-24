#! /usr/bin/env python

from __future__ import division
import codecs
import os
from collections import defaultdict
import math
from numpy import *
from numpy.linalg import *

class Classifier():

    def __init__(self,trainlist,testlist,metalist,directory=False, vocabulary=False):
        self.training=trainlist
        self.test=testlist
        self.meta=metalist
        self.directory=directory
        self.feature_info=vocabulary

    def classify(self, algorithm, arguments, prune=False, select=False, timelabels=False):
        if algorithm=="knn":
            self.perform_knn(arguments,prune,select,timelabels)
        elif algorithm=="lcs":
            self.perform_lcs(arguments,prune,select,timelabels)
        elif algorithm=="ibt":
            self.informed_baseline_date(arguments)
        elif algorithm=="dist":
            self.lin_reg_event(arguments)
    
    def adjust_index_space(self,ranked_list,value_dict,boundary):
        new_feature_info={}
        feature_status={}        
        
        #assign new feature_info indexes based on the ranked list
        for i,old_index in enumerate(ranked_list[:boundary]):
            new_index=str(i+1)
            new_feature_info[new_index]=self.feature_info[old_index] + [str(value_dict[old_index])]
            feature_status[old_index]=new_index
        self.feature_info=new_feature_info
        #set status of all pruned features to False
        for feature_index in ranked_list[boundary:]:
            feature_status[feature_index]=False

        #adjust instances
        index = 0
        while index < len(self.training):
            instance = self.training[index]
            new_features=[]
            features = instance["features"]
            for feature in features:
                if feature_status[feature]:
                    new_index=int(feature_status[feature])
                    new_features.append(new_index)
            if len(new_features) == 0:
                self.training.pop(index)
            else:
                new_features_str = [str(feature) for feature in sorted(new_features)]
                self.training[index]["features"]=new_features_str
                index += 1
            
        index = 0
        while index < len(self.test): 
            instance = self.test[index]
            new_features=[]
            features=instance["features"]
            for feature in features:
                try: 
                    if feature_status[feature]:
                        new_index=int(feature_status[feature])
                        new_features.append(new_index)
                except KeyError:
                    continue
            if len(new_features) == 0:
                self.test.pop(index)
                self.meta.pop(index)
            else:   
                new_features_str = [str(feature) for feature in sorted(new_features)]
                self.test[index]["features"]=new_features_str
                index += 1

    def prune_features(self,minimum_threshold,classifier):
        #generate feature_frequency dict
        feature_freq=defaultdict(int)
        if classifier == "knn":
            for instance in self.training:
                features=instance["features"]
                for feature in features:
                    feature_freq[feature] += 1
        elif classifier == "lcs":
            for instance in self.training:
                filename=instance["features"][0]
                fileread=codecs.open(self.file_dir + filename,"r","utf-8")
                for feature in fileread.readlines():
                    feature_freq[feature.strip()] += 1
                fileread.close()
        print "num features before pruning: ",len(feature_freq.keys())
        #prune features 
        sorted_feature_freq=sorted(feature_freq, key=feature_freq.get, reverse=True)
        boundary=0
        for i,f in enumerate(sorted_feature_freq):
            if feature_freq[f] <= minimum_threshold:
                boundary=i
                break
        if classifier == "knn":
            #generate new indexes and make a new feature_info 
            self.adjust_index_space(sorted_feature_freq,feature_freq,boundary)
            print "num features after pruning: ", len(self.feature_info.keys())
        elif classifier == "lcs":
            #generate stoplist
            self.stoplist=[]
            for feature in sorted_feature_freq[:boundary]:
                self.stoplist.append(feature)
                
    def infogain(self,classifier,prune):
    
        feature_infogain={}
        label_freq=defaultdict(int)
        label_feature_freq=defaultdict(lambda : defaultdict(int))
        feature_freq=defaultdict(int)
        if classifier == "knn":
            for instance in self.training:
                features=instance["features"][0]
                label=instance["label"]
                label_freq[label] += 1
                for feature in features:
                    label_feature_freq[label][feature] += 1
        elif classifier == "lcs":
            print "counting features..."
            for instance in self.training:
                filename=instance["features"][0]
                label=instance["label"]
                label_freq[label] += 1
                fileread=codecs.open(self.file_dir + filename,"r","utf-8")
                features=[]
                for feature in fileread.readlines():
                    feature=feature.strip()
                    features.append(feature)
                for feature in list(set(features)):
                    label_feature_freq[label][feature] += 1
                    feature_freq[feature] += 1
                fileread.close()
        
        problabels=[]
        for label in label_freq.keys():
            problabels.append(label_freq[label] / len(self.training)) #probs of the classes
        entropy_before=-sum([p * math.log(p,2) for p in problabels]) #entropy before splitting
        
        def compute_infogain(feature,frequency):
            inverse_frequency=len(self.training) - frequency
            p1=frequency / len(self.training)
            p0=inverse_frequency / len(self.training)
            probs1=[]
            probs0=[]
            for label in label_freq.keys():
                probs1.append(label_feature_freq[label][feature] / frequency)
                probs0.append((label_freq[label]-label_feature_freq[label][feature]) / inverse_frequency)
            entropy1=(-sum([p * math.log(p,2) for p in probs1 if p!=0])) * p1
            entropy0=(-sum([p * math.log(p,2) for p in probs0 if p!=0])) * p0
            entropy_after=entropy1 + entropy0 #class entropy of instances with the feature
            infogain=entropy_before-entropy_after #infogain score
            return infogain
            
        if classifier == "knn":
            for feature in self.feature_info.keys(): #compute for each feature
                frequency=int(self.feature_info[feature][1])
                ig=compute_infogain(feature,frequency)
                feature_infogain[feature]=ig
        elif classifier == "lcs":
            print "pruning features..."
            ranked_feature_freq=sorted(feature_freq, key=feature_freq.get, reverse=True)
            boundary=0
            i=0
            inc=100000
            while True:
                if i < 0:
                    i=0
                elif i > len(ranked_feature_freq):
                    i=len(ranked_feature_freq)-1
                feature=ranked_feature_freq[i]
                if feature_freq[feature] <= prune:
                    if inc == 1:
                        boundary=i
                        break
                    else:
                        i -= inc
                        inc=int(inc/10)
                else:
                    i += inc
            print "num features left:",boundary
            self.stoplist.extend(ranked_feature_freq[boundary:])
            print "selecting features..."
            for feature in ranked_feature_freq[:boundary]:
                frequency=feature_freq[feature]
                ig=compute_infogain(feature,frequency)
                feature_infogain[feature]=ig

        return feature_infogain

    def select_features(self,num_features,prune,classifier):
        #make a file of the instances and perform infogain weighting
        feature_weights=self.infogain(classifier,prune)
        selected_features=sorted(feature_weights, key=feature_weights.get, reverse=True)    
        if classifier == "knn":
            self.adjust_index_space(selected_features,feature_weights,num_features)
        elif classifier == "lcs":
            self.stoplist.extend(selected_features[num_features:])

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
            self.file_dir=args[1]
        except IndexError:
            print "not enough arguments for LCS, exiting program..."
            exit()

        if not os.path.exists(self.directory + "test.rnk"):
            if prune:
                self.prune_features(int(prune),"lcs")
            if select:
                self.select_features(int(select),int(prune),"lcs")
            
            train=codecs.open(classification_dir + "train","w","utf-8")
            for t in self.training:
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
        
        if prune:
            print "pruning features..."
            self.prune_features(int(prune),"knn")
        if select:
            print "selecting features..."
            self.select_features(int(select),int(prune),"knn")

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
                os.system("stimbl -n " + str(len(self.feature_info)+1) + " -f " + train + " -W " + weight + " -i -D -m 3 -d 1 -k " + k + " < " + test + " > " + classification) 
            else:
                os.system("stimbl -n " + str(len(self.feature_info)+1) + " -f " + train + " -i -D -m 3 -d 1 -w 2 -k " + k + " < " + test + " > " + classification) 

    def lin_reg_event(self,args):
        
        def return_standard_deviation(windows):
            mean = sum(windows) / len(windows)
            #return sum([(window-mean) for window in windows]) / len(windows)

        def generate_hourly_sequence(instances,instance_dict):
            last_tfz = int(instances[-1]["meta"][4])
            instance_dict["sequence"] = []
            ef = instance_dict["sequence"]
            for hour in range(last_tfz+1):
                ef.append(0)
            est = True
            for instance in instances:
                tfz = int(instance["meta"][4])
                ef[tfz] += 1
                if est:
                    timelabel = instance["meta"][3]
                    if timelabel == "-":
                        instance_dict["start_time"] = tfz+1
                        est = False

        def generate_window_output(sequence,outdict,start_time,window,slider,log):
            #half = int(window/2)
            start = 0
            end = window 
            hist = [sum(sequence[start:start+window]),sum(sequence[start+window:start+(window*2)])]
            stdev_hist = return_standard_deviation(hist)
            start = start+(window*2)
            while start+window < start_time:
#               print window,half,slider,ef,start,half
                #half1 = sequence[start:start+half]
                #half2 = sequence[start+half+1:end]
                #if sum(half1) == 0 or sum(half2) == 0:
                #    value = 0
                hist.append(sequence[start:start+window])
                outdict["value"].append(return_standard_deviation(hist))             
                outdict["target"].append(int((start_time - start+window)/24))
                start += window
                # else:
                #     if log:
                #         if sum(half1) == 1 or sum(half2) == 1:
                #             value = 0
                #         #print sum(half2),sum(half1),math.log(sum(half2),2),math.log(sum(half1),2)
                #         else:
                #             value = math.log(sum(half2),2)/math.log(sum(half1),2)
                #     else:
                #         value = (sum(half2)-sum(half1))/sum(half1)

                # outdict["value"].append(value)
                # outdict["target"].append(target)
                # start += slider
                # end += slider

        #generate input
        event_tweets = defaultdict(list)
        event_frequency = defaultdict(lambda : {}) 
        #generate a list of tweets for each event
        for instance in self.training:
            event = instance["meta"][1]
            event_tweets[event].append(instance)
        #generate an hourly sequence of tweet frequencies for each event
        for event in event_tweets.keys():
            tweets = event_tweets[event]
            generate_hourly_sequence(tweets,event_frequency[event])

        #if args[1] == "log"
        #convert to log

        #slide through windows and generate x-y pairs
        window = int(args[0])
        slider = int(args[1])
        log = int(args[2])
        training = defaultdict(list)
        for event in event_frequency.keys():
            ef = event_frequency[event]["sequence"]
            event_time = event_frequency[event]["start_time"]
            generate_window_output(ef,training,event_time,window,slider,log)

        #calculate w0 and w1
        a = array([[len(training["value"]),sum(training["value"])],[sum(training["value"]),sum((x*x) for x in training["value"])]])
        y = array([[sum(training["target"])],[sum((training["value"][i] * training["target"][i]) for i in range(len(training["value"])))]])
        #print a
        #print y
        w = dot(inv(a),y)
        print w

        #make estimations
        test_dict = {}
        generate_hourly_sequence(self.test,test_dict)
        test = defaultdict(list)
        #generate_window_output(test_dict["sequence"],test,test_dict["start_time"],window,slider,log)
        #for i in range(len(test["value"])):
        #    estimation = (test["value"][i]*w[1][0]) + w[0][0]
        #    print test["value"][i],estimation,test["target"][i]
        # for 

