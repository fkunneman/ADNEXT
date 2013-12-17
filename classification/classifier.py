#! /usr/bin/env python

from __future__ import division
import codecs
import os
import multiprocessing
from collections import defaultdict
from collections import Counter

import math
import numpy
from scipy.sparse import *
from scipy import *
from sklearn import svm
from sklearn.grid_search import GridSearchCV
from sklearn.multiclass import OutputCodeClassifier
from sklearn.metrics import f1_score

import lineconverter
import gen_functions
import weight_features

class Classifier():

    def __init__(self,trainlist,testlist,classifier,scaling,directory=False):
        self.training=trainlist
        self.test=testlist #self.test should be a list with multiple lists for each testset
        self.scaling=scaling
        self.directory=directory
        self.classifier = classifier

    def count_feature_frequency(self):
        
        counted = 0
        self.feature_frequency = Counter()
        
        def ff(instances,queue):
            #n_instances = len(self.training)
            feature_frequency = defaultdict(int)
            for i,instance in enumerate(instances):
                for feature in instance["features"]:
                    feature_frequency[feature] += 1
            queue.put(feature_frequency)
        
        q = multiprocessing.Queue()
        chunks = gen_functions.make_chunks(self.training,16)
        for chunk in chunks:
            p = multiprocessing.Process(target=ff,args=[chunk,q])
            p.start()

        ds = []
        while True:
            l = q.get()
            ds.append(l)
            if len(ds) == len(chunks):
                break
        
        self.feature_frequency = defaultdict(int)
        for d in ds:
            for k in d:
                self.feature_frequency[k] += d[k]

    def prune_features_topfrequency(self,n):
        #generate feature_frequency dict
        sorted_feature_freq=sorted(self.feature_frequency, key=self.feature_frequency.get, reverse=True)
        boundary=0
        feature_status = {}
        self.pruned_features = sorted_feature_freq[:n]
        for f in sorted_feature_freq[:n]:
            feature_status[f] = True 
        for f in sorted_feature_freq[n:]:
            feature_status[f] = False

        def prune_features(instances,queue):
            for instance in instances:
                new_features = []
                #print feature_status
                for f in instance["features"]:
                    if feature_status[f]:
                        new_features.append(f)
                instance["features"] = new_features
                queue.put(instance)

        print "before",len(self.training)
        q = multiprocessing.Queue()
        chunks = gen_functions.make_chunks(self.training)
        for chunk in chunks:
            p = multiprocessing.Process(target=prune_features,args=[chunk,q])
            p.start()

        new_instances = []
        while True:
            ins = q.get()
            new_instances.append(ins)
            if len(new_instances) == len(self.training):
                break

        self.training = new_instances
        print "after",len(self.training)

    def balance_data(self):
        label_instances = defaultdict(list)
        new_training = []
        for instance in self.training:     
            label = instance["label"]
            label_instances[label].append(instance)
        median = int(numpy.median(numpy.array([len(label_instances[x]) for x in label_instances.keys()])))
        for label in label_instances.keys():
            if len(label_instances[label]) == median:
                new_training.extend(label_instances[label])
            else:
                instances = lineconverter.Lineconverter(label_instances[label])
                if len(instances.lines) < median:
                    instances.sample(median-len(instances.lines),sample_type="up")
                else:
                    instances.sample(len(instances.lines)-median)
                new_training.extend(instances.lines)
        self.training = new_training

    def index_features(self,ind = 0):
        feature_frequency=defaultdict(int)
        self.feature_info={}      
        for i,feature in enumerate(self.pruned_features):
            self.feature_info[feature]=i+ind
        
        def sparsify(instances,writelist):
            for instance in instances:
                sparse_features = defaultdict(int)
                for feature in instance["features"]:
                    try:
                        sparse_features[self.feature_info[feature]] += 1
                    except:
                        continue
                instance["sparse"] = sparse_features
                writelist.append(instance)         

        print "before",len(self.training)
        # q = multiprocessing.Queue()
        # chunks_training = gen_functions.make_chunks(self.training)
        # for chunk in chunks_training:
        #     p = multiprocessing.Process(target=sparsify,args=[chunk,q])
        #     p.start()



        new_instances = []
        sparsify(self.training,new_instances)
        # while True:
        #     ins = q.get()
        #     new_instances.append(ins)
        #     if len(new_instances) == len(self.training):
        #         break

        self.training = new_instances
        print "after",len(self.training)

        for tset in self.test:
            for instance in tset["instances"]:
                sparse_features = defaultdict(int)
                for feature in instance["features"]:
                    try:
                        sparse_features[self.feature_info[feature]] += 1
                    except:
                        continue
                instance["sparse"] = sparse_features

    def classify_svm(self):

        def vectorize(instances):
            zerolist = [float(0)] * len(self.feature_info.keys())
            matrix = []
            for instance in instances:
                featurev = zerolist[:]
                for feature in instance["sparse"].keys():
                    if self.scaling == "binary":
                        featurev[feature] = float(1)
                    elif self.scaling == "log": 
                        featurev[feature] = math.log(instance["sparse"][feature],10)
                    elif self.scaling == "tfidf":
                        featurev[feature] = instance["sparse"][feature] * self.idf[feature]
                matrix.append(featurev)
            return matrix

        
        #generate scipy libsvm input
        print "Dimensions:",len(self.feature_info.keys())
        trainlabels_raw = [x["label"] for x in self.training]
        labels = set(trainlabels_raw)
        labeldict = dict(zip(labels,range(len(labels))))
        labeldict_back = dict(zip(range(len(labels)),labels))
        if self.scaling == "tfidf":
            self.idf = weight_features.return_idf(self.training)
        trainingvectors = vectorize(self.training)
        trainlabels = [labeldict[x["label"]] for x in self.training]
        training_csr = csr_matrix(trainingvectors)
        #obtain the best parameter settings for an svm outputcode classifier
        param_grid = {'estimator__C': [0.001, 0.005, 0.01, 0.5, 1, 5, 10, 50, 100, 500, 1000], 'estimator__kernel': ['linear','rbf'], 'estimator__gamma': [0.0005, 0.002, 0.008, 0.032, 0.128, 0.512, 1.024, 2.048]}
        model = OutputCodeClassifier(svm.SVC(probability=True),n_jobs=-14)
        paramsearch = GridSearchCV(model, param_grid, cv=5, score_func = f1_score,verbose=2)
        print "Grid search..."
        paramsearch.fit(training_csr,numpy.asarray(trainlabels))
        #print the best parameters to the file
        print "Prediction..."
        #train an svm outputcode classifier using the best parameters
        parameters = paramsearch.best_params_
        outstring = "best parameter settings:\n"
        for parameter in parameters.keys():
            outstring += (parameter + ": " + str(parameters[parameter]) + "\n")
        outstring += ("best score: " + str(paramsearch.best_score_) + "\n\n")
        clf = svm.SVC(probability=True, C=parameters['estimator__C'],kernel=parameters['estimator__kernel'],gamma=parameters['estimator__gamma'])
        multiclf = OutputCodeClassifier(clf,n_jobs=-15)
        multiclf.fit(training_csr,trainlabels)
        for tset in self.test:
            testvectors = vectorize(tset["instances"])
            outfile = codecs.open(tset["out"],"w","utf-8")
            outfile.write(outstring)
            #predict labels and print them to the outfile
            for i,t in enumerate(testvectors):
                classification = multiclf.predict(t)
                classification_label = labeldict_back[classification[0]]
                outfile.write(tset["instances"][i]["label"] + " " + classification_label + "\n")
            outfile.close()

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
