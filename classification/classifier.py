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
import lineconverter
import itertools

class Classifier():

    def __init__(self,trainlist,testlist,metalist=False,directory=False, vocabulary=False):
        self.training=trainlist
        self.test=testlist
        self.meta=metalist
        self.directory=directory
        self.feature_info=vocabulary

    def classify(self, algorithm, arguments, prune=False, select=False, timelabels=False):
        if algorithm=="svm":
            self.perform_svm()
        elif algorithm=="knn":
            self.perform_knn(arguments,prune,select,timelabels)
        elif algorithm=="lcs":
            self.perform_lcs(arguments,prune,select,timelabels)
        elif algorithm=="dist":
            self.lin_reg_event(arguments)

    def undersample(self):
        label_instances = defaultdict(list)
        label_frequency = defaultdict(int)
        current_label = ""
        label_order = []
        for instance in self.training:     
            label = instance["label"]
            label_frequency[label] += 1
            label_instances[label].append(instance)
            if label != current_label:
                label_order.append(label)
                current_label = label
        sorted_labels = sorted(label_frequency, key=label_frequency.get, reverse=True)
        lowest_freq = label_frequency[sorted_labels[-1]]
        new_training = []
        for label in label_order:
            print label
            if label == sorted_labels[-1]:
                new_training.extend(label_instances[label])
            else:
                lc = lineconverter.Lineconverter(label_instances[label])
                sample = lc.extract_sample(lowest_freq)
                new_training.extend(sample)
        self.training = new_training

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

    def ltqnorm(self,p):
        """
        Modified from the author's original perl code (original comments follow below)
        by dfield@yahoo-inc.com.  May 3, 2004.

        Lower tail quantile for standard normal distribution function.

        This function returns an approximation of the inverse cumulative
        standard normal distribution function.  I.e., given P, it returns
        an approximation to the X satisfying P = Pr{Z <= X} where Z is a
        random variable from the standard normal distribution.

        The algorithm uses a minimax approximation by rational functions
        and the result has a relative error whose absolute value is less
        than 1.15e-9.

        Author:      Peter John Acklam
        Time-stamp:  2000-07-19 18:26:14
        E-mail:      pjacklam@online.no
        WWW URL:     http://home.online.no/~pjacklam
        """

        if p <= 0 or p >= 1:
            # The original perl code exits here, we'll throw an exception instead
            raise ValueError( "Argument to ltqnorm %f must be in open interval (0,1)" % p )

        # Coefficients in rational approximations.
        a = (-3.969683028665376e+01,  2.209460984245205e+02, \
             -2.759285104469687e+02,  1.383577518672690e+02, \
             -3.066479806614716e+01,  2.506628277459239e+00)
        b = (-5.447609879822406e+01,  1.615858368580409e+02, \
             -1.556989798598866e+02,  6.680131188771972e+01, \
             -1.328068155288572e+01 )
        c = (-7.784894002430293e-03, -3.223964580411365e-01, \
             -2.400758277161838e+00, -2.549732539343734e+00, \
              4.374664141464968e+00,  2.938163982698783e+00)
        d = ( 7.784695709041462e-03,  3.224671290700398e-01, \
              2.445134137142996e+00,  3.754408661907416e+00)

        # Define break-points.
        plow  = 0.02425
        phigh = 1 - plow

        # Rational approximation for lower region:
        if p < plow:
           q  = math.sqrt(-2*math.log(p))
           return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                   ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)

        # Rational approximation for upper region:
        if phigh < p:
           q  = math.sqrt(-2*math.log(1-p))
           return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                    ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)

        # Rational approximation for central region:
        q = p - 0.5
        r = q*q
        return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
               (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)

    def scale_features(self):
        label_frequency = defaultdict(int)
        feature_label_frequency = defaultdict(lambda : defaultdict(int))
        feature_label_bns = defaultdict(lambda : {})
        #obtain feature and label frequencies
        for instance in self.training:     
            label = instance["label"]
            label_frequency[label] += 1
            for feature in instance["sparse"]:
                feature_label_frequency[feature][label] += 1
        #make a list of each possible label pair
        labels = label_frequency.keys()
	pairs = []
        perm = itertools.permutations(labels,2)
        for entry in perm:
            pairs.append(list(entry))
	print pairs
        quit()

        #generate bns-values per feature-label pair
        
        for feature in feature_label_frequency.keys():
            feature_labels = feature_label_frequency[feature].keys()
            for i,label in enumerate(feature_labels):
                tp = feature_label_frequency[feature][label]
                pos = label_frequency[label]
                try:
                    fp = sum([feature_label_frequency[feature][x] for x in feature_labels[:i] + feature_labels[i+1:]])
                except IndexError:
                    fp = sum([feature_label_frequency[feature][x] for x in feature_labels[:i]])
                neg = len(self.training) - pos
                tpr = tp/pos
                fpr = fp/neg
                if tpr < 0.0005: 
                    tpr = 0.0005
                elif tpr > (1-0.0005): 
                    tpr = (1-0.0005)
                if fpr < 0.0005: 
                    fpr = 0.0005
                elif fpr > (1-0.0005): 
                    fpr = (1-0.0005)
                feature_label_bns[feature][label] = abs(self.ltqnorm(tpr) - self.ltqnorm(fpr))
            other_labels = list(set(labels) - set(feature_labels))
            for label in other_labels:
                tp = 0
                pos = label_frequency[label]
                fp = sum([feature_label_frequency[feature][x] for x in feature_labels])
                neg = len(self.training) - pos
                tpr = tp/pos
                fpr = fp/neg
                if tpr < 0.0005: 
                    tpr = 0.0005
                elif tpr > (1-0.0005): 
                    tpr = (1-0.0005)
                if fpr < 0.0005: 
                    fpr = 0.0005
                elif fpr > (1-0.0005): 
                    fpr = (1-0.0005)     
                feature_label_bns[feature][label] = abs(self.ltqnorm(tpr) - self.ltqnorm(fpr))
        #adapt instance-features
        outputdirs = {}
        for label in labels:
            d = self.directory + label + "/"
            os.system("mkdir " + d)
            outputdirs[label] = d
        for instance in self.training:
            feature_freq = defaultdict(int)
            for label in labels:
                outfile = open(outputdirs[label] + "train","a")
                inst_label = instance["label"]
                features = list(set(instance["sparse"]))
                if inst_label == label:
                    outlabel = "1"
                else:
                    outlabel = "-1"
                outfile.write(outlabel)
                for index in sorted(features):
                    bns = feature_label_bns[index][label]
                    outfile.write(" " + str(index) + ":" + str(bns))
                outfile.write("\n")
                outfile.close()
        for instance in self.test:
            feature_freq = defaultdict(int)
            for label in labels:
                outfile = open(outputdirs[label] + "test","a")
                inst_label = instance["label"]
                features = list(set(instance["sparse"]))
                if inst_label == label:
                    outlabel = "1"
                else:
                    outlabel = "-1"
                outfile.write(outlabel)
                for index in sorted(features):
                    try:
                        bns = feature_label_bns[index][label]
                        outfile.write(" " + str(index) + ":" + str(bns))
                    except KeyError:
                        continue
                outfile.write("\n")
                outfile.close()

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

    def top_features(self,n):
        #generate feature_frequency dict
        feature_freq=defaultdict(int)
        # if classifier == "knn":
        for instance in self.training:
            features=instance["features"]
            for feature in features:
                feature_freq[feature] += 1
        # elif classifier == "lcs":
        #     for instance in self.training:
        #         filename=instance["features"][0]
        #         fileread=codecs.open(self.file_dir + filename,"r","utf-8")
        #         for feature in fileread.readlines():
        #             feature_freq[feature.strip()] += 1
        # #         fileread.close()
        # print "num features before pruning: ",len(feature_freq.keys())
        #prune features 
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

    #def pca(self):

    def select_features(self,num_features,prune,classifier):
        #make a file of the instances and perform infogain weighting
        feature_weights=self.infogain(classifier,prune)
        selected_features=sorted(feature_weights, key=feature_weights.get, reverse=True)    
        if classifier == "knn":
            self.adjust_index_space(selected_features,feature_weights,num_features)
        elif classifier == "lcs":
            self.stoplist.extend(selected_features[num_features:])

    def perform_svm(self):
        #generate sparse input
        self.index_features()
        #generate classifiers
        self.scale_features()
        labels = [x["label"] for x in self.training]
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
                os.system("stimbl -v -n " + str(len(self.feature_info)+1) + " -f " + train + " -W " + weight + " -i -D -m 3 -d 1 -k " + k + " < " + test + " > " + classification) 
            else:
                os.system("stimbl -n " + str(len(self.feature_info)+1) + " -f " + train + " -i -D -m 3 -d 1 -w 2 -k " + k + " < " + test + " > " + classification) 

    def lin_reg_event(self,args):
        
        def return_standard_deviation(windows):
            #print windows
            mean = sum(windows) / len(windows)
	    try:
                stdef = math.sqrt(sum([((window-mean) * (window-mean)) for window in windows]) / len(windows))
            except ValueError:
                stdef = 0
            return stdef

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

        def generate_window_output(sequence,outdict,start_time,window,slider,log,test):
            #half = int(window/2)
            start = 0
            end = window 
            hist = [sum(sequence[start:start+window]),sum(sequence[start+window:start+(window*2)])]
            stdev_hist = return_standard_deviation(hist)
            start = start+(window*2)
            if test:
                stop = len(sequence)
            else:
                stop = start_time
            while start < stop:
                hist.append(sum(sequence[start:start+window]))
                if log == 1:
                    outdict["stdef"].append(return_standard_deviation(hist))
                    if hist[-1] == 0:
                        outdict["value"].append(0)
                    else:
                        outdict["value"].append(math.log(hist[-1]) / math.log(2))
                else:
                    outdict["value"].append(return_standard_deviation(hist))
                    outdict["stdef"].append(return_standard_deviation(hist))             
                outdict["target"].append(int((start_time - start+window)/24))
                start += window

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

        #slide through windows and generate x-y pairs
        window = int(args[0])
        slider = int(args[1])
        log = int(args[2])
        training = defaultdict(list)
        for event in event_frequency.keys():
            ef = event_frequency[event]["sequence"]
            event_time = event_frequency[event]["start_time"]
            generate_window_output(ef,training,event_time,window,slider,log,test=False)

        m = polyfit(training["value"],training["target"],1)

        #make estimations
        test_dict = {}
        generate_hourly_sequence(self.test,test_dict)
        test = defaultdict(list)
        generate_window_output(test_dict["sequence"],test,test_dict["start_time"],window,slider,log,test=True)
        for i,window in enumerate(test["value"]):
            estimation = (m[0]*window) + m[1]
            try:
                print test["stdef"][i]/test["stdef"][i-1],test["target"][i],round(estimation,2)
            except IndexError:
                print test["target"[i]],round(estimation,2)
