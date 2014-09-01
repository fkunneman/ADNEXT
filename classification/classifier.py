#! /usr/bin/env python

from __future__ import division
import codecs
import multiprocessing
from collections import defaultdict

import re
import math
import numpy
from scipy.sparse import *
from scipy import *
from sklearn import svm
from sklearn.grid_search import GridSearchCV, RandomizedSearchCV
from sklearn.multiclass import OutputCodeClassifier
from sklearn.metrics import f1_score

import lineconverter
import gen_functions
import weight_features

class Classifier():

    def __init__(self,trainlist,testlist,scaling = False,jobs=16,directory=False):
        self.training = trainlist
        self.test = testlist #self.test should be a list with multiple lists for each testset
        self.scaling = scaling
        self.jobs = jobs
        self.directory = directory
        self.feature_status = {}

    def count_feature_frequency(self):
        
        def ff(instances,queue):
            feature_frequency = defaultdict(int)
            for i,instance in enumerate(instances):
                for feature in instance["features"]:
                    feature_frequency[feature] += 1
            queue.put(feature_frequency)
        
        print len(self.training)
        q = multiprocessing.Queue()
        chunks = gen_functions.make_chunks(self.training,self.jobs)
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
        self.features = sorted(self.feature_frequency, key=self.feature_frequency.get, 
            reverse=True)

    def make_feature_labellist(self):
        feature_labellist = defaultdict(list)
        for instance in self.training:
            try:
                label = int(instance["label"])       
                for feature in instance["features"]:
                    feature_labellist[feature].append(label)
            except:
                continue
        self.feature_labellist = feature_labellist

    def prune_features(self):
        for instance in self.training:
            new_features = []
            #print feature_status
            for f in instance["features"]:
                try:
                    if self.feature_status[f]:
                        new_features.append(f)
                except:
                    continue
            instance["features"] = new_features
            # queue.put(instance)

    def convert_features(self,convert_list):
        for instance in self.training:
            new_features = []
            #print feature_status
            #print instance["features"]
            for i,f in enumerate(instance["features"]):
                if f in convert_list.keys():
                     instance["features"][i] = convert_list[f]
            #print instance["features"]

    def filter_stdev(self,threshold,prop):
        self.make_feature_labellist()
        feature_convert = {}
        new_features = []
        for feature in self.feature_labellist.keys():
            if re.search(r"^" + prop,feature):
                if gen_functions.return_standard_deviation(self.feature_labellist[feature]) > threshold or len(self.feature_labellist[feature]) <= 2:
                    self.feature_status[feature] = False
                else:
                    new_feature = str(abs(int(numpy.median(self.feature_labellist[feature])))) + "_days"
                    feature_convert[feature] = new_feature
                    new_features.append(new_feature)
                    self.feature_status[new_feature] = True
                    #print feature, self.feature_labellist[feature], numpy.median(self.feature_labellist[feature])
            else:
                self.feature_status[feature] = True
                new_features.append(feature)
        self.convert_features(feature_convert)
        self.prune_features()
        self.features = list(set(new_features))

    def prune_features_topfrequency(self,n):
        #generate feature_frequency dict
        print n,"len",len(self.features)
        for f in self.features[:n]:
            self.feature_status[f] = True 
        for f in self.features[n:]:
            self.feature_status[f] = False
        self.features = self.features[:n]
        print "len2",len(self.features)
        self.prune_features()


        # print "before",len(self.training)
        # q = multiprocessing.Queue()
        # chunks = gen_functions.make_chunks(self.training,self.jobs)
        # for chunk in chunks:
        #     p = multiprocessing.Process(target=prune_features,args=[chunk,q])
        #     p.start()

        # new_instances = []
        # while True:
        #     ins = q.get()
        #     new_instances.append(ins)
        #     if len(new_instances) == len(self.training):
        #         break

        # self.training = new_instances
        # print "after",len(self.training)

    def balance_data(self):
        label_instances = defaultdict(list)
        new_training = []
        for instance in self.training:     
            label = instance["label"]
            label_instances[label].append(instance)
        median = int(numpy.median(numpy.array([len(label_instances[x]) for \
            x in label_instances.keys()])))
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
        #print self.features      
        for i,feature in enumerate(self.features):
            #print i, feature
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

    def vectorize(self,instances):
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

    def classify_svm(self,t = "discrete",classweight = None,params = 10):
        #generate scipy libsvm input
        print "Dimensions:",len(self.feature_info.keys())
        trainlabels_raw = [x["label"] for x in self.training]
        labels = set(trainlabels_raw)
        print labels
        labeldict = dict(zip(labels,range(len(labels))))
        labeldict_back = dict(zip(range(len(labels)),labels))
        if self.scaling == "tfidf":
            self.idf = weight_features.return_idf(self.training)
        trainingvectors = self.vectorize(self.training)
        print trainingvectors
        trainlabels = [labeldict[x["label"]] for x in self.training]
        training_csr = csr_matrix(trainingvectors)
        print training_csr
        quit()
        #obtain the best parameter settings for an svm outputcode classifier
        if len(labels) > 2:
            print "outputcodeclassifier"
            param_grid = {'estimator__C': [0.001, 0.005, 0.01, 0.5, 1, 5, 10, 50, 100, 500, 1000],
                'estimator__kernel': ['linear','rbf','poly'], 
                'estimator__gamma': [0.0005, 0.002, 0.008, 0.032, 0.128, 0.512, 1.024, 2.048],
                'estimator__degree': [1,2,3,4]}
            model = OutputCodeClassifier(svm.SVC(probability=True,class_weight=classweight))
        else:
            print "svc model"
            param_grid = {'C': [0.001, 0.005, 0.01, 0.5, 1, 5, 10, 50, 100, 500, 1000],
                'kernel': ['linear','rbf','poly'], 
                'gamma': [0.0005, 0.002, 0.008, 0.032, 0.128, 0.512, 1.024, 2.048],
                'degree': [1,2,3,4]}
            model = svm.SVC(probability=True,class_weight=classweight)
        paramsearch = RandomizedSearchCV(model, param_grid, cv=5, verbose=2,n_iter = params,n_jobs=self.jobs) 
        print "Grid search..."
        paramsearch.fit(training_csr,numpy.asarray(trainlabels))
        print "Prediction..."
        #print the best parameters to the file
        parameters = paramsearch.best_params_
        outstring = "best parameter settings:\n"
        for parameter in parameters.keys():
          outstring += (parameter + ": " + str(parameters[parameter]) + "\n")
        outstring += ("best score: " + str(paramsearch.best_score_) + "\n\n")
        #train an svm outputcode classifier using the best parameters

        def predict(ts,mc):
            testvectors = self.vectorize(ts["instances"])
            outfile = codecs.open(ts["out"],"w","utf-8")
            outfile.write(outstring)
            for i,t in enumerate(testvectors):
                classification = mc.predict(t)
                classification_label = labeldict_back[classification[0]]
                outfile.write(ts["instances"][i]["label"] + " " + classification_label + "\n")
            outfile.close()

        if len(labels) > 2:
            clf = svm.SVC(probability=True, C=parameters['estimator__C'],
                kernel=parameters['estimator__kernel'],gamma=parameters['estimator__gamma'],
                degree=parameters['estimator__degree'],class_weight=classweight)
            multiclf = OutputCodeClassifier(clf,n_jobs=self.jobs)
            multiclf.fit(training_csr,trainlabels)
            for tset in self.test:
                p = multiprocessing.Process(target=predict,args=[tset,multiclf])
                p.start()
            p.join()
        else:
            clf = svm.SVC(probability=True, C=parameters['C'],
                kernel=parameters['kernel'],gamma=parameters['gamma'],
                degree=parameters['degree'],class_weight=classweight)
            clf.fit(training_csr,trainlabels)
            for tset in self.test:
                p = multiprocessing.Process(target=predict,args=[tset,clf])
                p.start()
            p.join()
