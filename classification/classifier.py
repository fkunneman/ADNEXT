#! /usr/bin/env python

from __future__ import division
import codecs
import os
from collections import defaultdict
import math
import numpy
from sklearn import svm
from sklearn.grid_search import GridSearchCV
#from sklearn import preprocessing
from sklearn.multiclass import OutputCodeClassifier
from sklearn.metrics import f1_score
from scipy.sparse import *
from scipy import *
#from pylab import *
import re
import itertools
import glob
import multiprocessing
import gen_functions
import lineconverter
import weight_features

class Classifier():

    def __init__(self,trainlist,testlist,classifier,directory=False,vocabulary=False):
        self.training=trainlist
        self.test=testlist
        #self.meta=metalist
        self.directory=directory
        self.classifier = classifier
        #self.feature_info=vocabulary

    def prune_features_topfrequency(self,n):
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

    def balance_data(self):
        label_instances = defaultdict(list)
        for instance in self.training:     
            label = instance["label"]
            label_instances[label].append(instance)
        mean_instances = int(numpy.mean(numpy.array([len(label_instances[x]) for x in label_instances.keys()])))
        print mean_instances,[len(label_instances[x]) for x in label_instances.keys()]
        exit()
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

    def index_features(self,ind = 0):
        feature_frequency=defaultdict(int)
        self.feature_info={}      
        for i,instance in enumerate(self.training):
            for feature in instance["features"]:
                feature_frequency[feature] += 1
        #feature_frequency_sorted = sorted(feature_frequency.items(), key=lambda x: x[1],reverse=True)
        for i,feature in enumerate(feature_frequency.keys()):
            self.feature_info[feature]=i+ind
        #zerolist = [0] * top_frequency
        instances = self.training + self.test
        for instance in instances:
            #sparse_features = []
            sparse_features = defaultdict(int)
            for feature in instance["features"]:
                try:
                    #sparse_features.append(self.feature_info[feature])
                    sparse_features[self.feature_info[feature]] += 1
                except:
                    continue
            #instance["sparse"] = list(set(sparse_features))
            instance["sparse"] = sparse_features
            # print instance["features"],instance["sparse"]
            # for index in sorted(feature_freq.keys()):
            #     instance["sparse"].append(index)

    def generate_paired_svms(self):

        def perform_svm(pairs):
            #generate bns-values per classifier
            for pair in pairs:
                #feature_bns = weight_features.bns(pair,label_frequency, feature_label_frequency)
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
                #for t in training:
                #    print t["label"],sorted(t["sparse"].keys())
                #exit()
                #print training
                zerolist = [float(0)] * len(self.feature_info.keys())
#                training_instances = [x["sparse"] for x in training]
                rawinput_train_test = [training,self.test]
#                print training, self.test
#                exit()
                svminput_train_test = [[[],[]],[[],[]]]
                for i in [0,1]:
                    for instance in rawinput_train_test[i]:
                        featurev = zerolist[:]
                        #for feature in instance["sparse"]:
                        #for feature in instance["sparse"]:
                            #vector[feature] = feature_bns[feature]
                        for feature in instance["sparse"].keys():
                            featurev[feature] = float(instance["sparse"][feature])
                        #print vector
                        svminput_train_test[i][0].append(featurev)
                labeldict = {pair[0]:1, pair[1]:0}
                trainlabels = [labeldict[x["label"]] for x in training]
                #training_short = svminput_train_test[0][0]
                #print training_short[1]
                #training_normalized = preprocessing.normalize(svminput_train_test[0][0], norm="l2")
                training_csr = csr_matrix(svminput_train_test[0][0])
                #test_ = preprocessing.normalize(svminput_train_test[1][0], norm="l2")
                #test_csr = csr_matrix(svminput_train_test[1][0])
                #test_short = svminput_train_test[1][0]
                #print training_csr
                #clf = svm.SVC(probability=True,verbose=True)
                param_grid = [
                    {'C': [0.001, 0.005, 0.01, 0.5, 1, 5, 10, 50, 100, 500, 1000], 'kernel': ['linear']},
                    {'C': [0.001, 0.005, 0.01, 0.5, 1, 5, 10, 50, 100, 500, 1000], 'gamma': [0.00025, 0.0005, 0.001, 0.002, 0.004, 0.008, 0.16, 0.032, 0.064, 0.128, 0.256, 0.512, 1.024, 2.048], 'kernel': ['rbf']}
                ]
                model = OutputCodeClassifier(SVC(probability=True))
                clf = GridSearchCV(model, param_grid, cv=5, score_func = f1_score, n_jobs=16)
                print "fitting with paramgrid"
#                print svminput_train_test[0][0]
                clf.fit(training_csr,numpy.asarray(trainlabels))
                print dir(clf)
                print clf.best_params_,clf.best_score_
                exit()
                #print training_csr
                #print len(svminput_train_test[0][0]),len(trainlabels)
                #clf.fit(svminput_train_test[0][0],trainlabels)
                #print svminput_train_test[0][1],svminput_train_test[0][0][0],svminput_train_test[1][0][0]
                #print clf.best_params_, clf.best_score_, clf.best_estimator_
                #print clf.n_support_
                #print clf.predict(test)
#                print svminput_train_test[0][0],svminput_train_test[0][1],svminput_train_test[1][0],svminput_train_test[1][1]
                print pair
                #print clf.predict(test_csr)
                #print svminput_train_test[0][0]
                #print svminput_train_test[1][0]
                for i,t in enumerate(svminput_train_test[1][0]):
                    #print t[40:100]
#                   print csr_matrix(t)
                     print self.test[i]["label"],clf.predict(t),clf.predict_proba(t)
                exit()
                #print "new", clf.predict_proba
                # pairstring = re.sub("-","tte",pair[0]) + "_" + re.sub("-","tte",pair[1])
                # d = self.directory + pairstring + "/"
                # os.system("mkdir " + d)
                # train = open(d + "train","w")
                # test = open(d + "test", "w")
                # args = [[training,train],[self.test,test]]
                # if self.classifier == "svm":
                #     output = ["1","-1",":",""]
                # elif self.classifier == "winnow":
                #     output = ["1","0","(",")"]
                # for arg in args:
                #     for instance in arg[0]:
                #         features = list(set(instance["sparse"]))
                #         if instance["label"] == pair[0]:
                #             outstring = output[0]
                #         else:
                #             outstring = output[1]
                #         for feature in sorted(features):
                #             try:
                #                 outstring += (" " + str(feature) + output[2] + str(feature_bns[feature]) + output[3])
                #             except KeyError:
                #                 continue
                #         outstring += "\n"
                #         arg[1].write(outstring)
                #     arg[1].close()

        #obtain feature and label frequencies
        #label_frequency, feature_frequency, feature_label_frequency = weight_features.generate_frequencies(self.training,"sparse")
        #make a list of each possible label pair
        labels = list(set([x["label"] for x in self.training]))
        perm = itertools.combinations(labels,2)
        pairs = [list(entry) for entry in perm]
        #perform_svm(pairs[:2])
        perform_svm(labels)
        # chunks = gen_functions.make_chunks(pairs)
        # processes = []
        # for chunk in chunks:
        #     p = multiprocessing.Process(target=pairow,args=[chunk])
        #     processes.append(p)
        #     p.start()
        # for p in processes:
        #     p.join()

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

    def classify_pairs(self,pairs):
        for pair in pairs:
            tdir = os.getcwd() + "/" + pair.split("/")[-1] + "/"
            os.system("mkdir " + tdir)
            os.chdir(tdir)
            os.system("mv " + pair + "/train .")
            os.system("mv " + pair + "/test .")
            if self.classifier == "svm":
                os.system("$PARAMSEARCH_DIR/paramsearch svmlight train")
                os.system("$PARAMSEARCH_DIR/runfull-svmlight train test")
            elif self.classifier == "winnow":
                os.system("$PARAMSEARCH_DIR/paramsearch winnow train 2")
                os.system("$PARAMSEARCH_DIR/runfull-winnow train test")
            os.system("mv * " + pair + "/")
            os.chdir("..")
            os.system("rm -r " + tdir)

    def classify_pairs_parralel(self):
        pairs = list(glob.iglob(self.directory + '*'))
        chunks = gen_functions.make_chunks(pairs)
        processes = []
        for chunk in chunks:
            p = multiprocessing.Process(target=self.classify_pairs,args=[chunk])
            processes.append(p)
            p.start()
        for pr in processes:
            pr.join()

        # training_instances = [x["sparse"] for x in self.training]
        # training = csr_matrix(training_instances,dtype=float64)
        # test_instances = [x["sparse"] for x in self.test]
        # test = csr_matrix(test_instances,dtype=float64)
        # return training,test

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
