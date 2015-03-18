
from __future__ import division
import codecs
import multiprocessing
from collections import defaultdict

from copy import deepcopy
import re
import os
import math
import numpy
from scipy.sparse import *
from scipy import *
from sklearn import cross_validation
from sklearn import svm, naive_bayes, tree
from sklearn.grid_search import GridSearchCV, RandomizedSearchCV
from sklearn.multiclass import OutputCodeClassifier
from sklearn.metrics import f1_score
from sklearn.externals import joblib
import cPickle

import lineconverter
import gen_functions
import weight_features

class Classifier():

    def __init__(self,trainlist,testlist,scaling = "binary",jobs=16,directory=False,
            features = False, feature_info = False):
        self.training = trainlist
        self.test = testlist #self.test should be a list with multiple lists for each testset
        self.scaling = scaling
        self.jobs = jobs
        self.directory = directory
        self.feature_status = {}
        self.outstring = False
        self.features = features
        self.feature_info = feature_info

    def count_feature_frequency(self):
        
        def ff(instances,queue):
            feature_frequency = defaultdict(int)
            for i,instance in enumerate(instances):
                for feature in instance["ngrams"]:
                    feature_frequency[feature] += 1
            queue.put(feature_frequency)
        
        print(len(self.training))

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
                for feature in instance["ngrams"]:
                    feature_labellist[feature].append(label)
            except:
                continue
        self.feature_labellist = feature_labellist

    def prune_features(self):
        for instance in self.training:
            new_features = []
            #print feature_status
            for f in instance["ngrams"]:
                try:
                    if self.feature_status[f]:
                        new_features.append(f)
                except:
                    continue
            instance["ngrams"] = new_features
            # queue.put(instance)

    def convert_features(self,convert_list):
        for instance in self.training:
            new_features = []
            #print feature_status
            #print instance["features"]
            for i,f in enumerate(instance["ngrams"]):
                if f in convert_list.keys():
                     instance["ngrams"][i] = convert_list[f]
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
            else:
                self.feature_status[feature] = True
                new_features.append(feature)
        self.convert_features(feature_convert)
        self.prune_features()
        self.features = list(set(new_features))

    def prune_features_topfrequency(self,n):
        #generate feature_frequency dict
        for f in self.features[:n]:
            self.feature_status[f] = True 
        for f in self.features[n:]:
            self.feature_status[f] = False
        self.features = self.features[:n]
        self.prune_features()

    def balance_data(self):
        label_instances = defaultdict(list)
        new_training = []
        for instance in self.training:     
            label = instance["label"]
            label_instances[label].append(instance)
        if len(label_instances.keys()) > 2:
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
            self.feature_info[feature]=i+ind
        
        def sparsify(instances,writelist):
            for instance in instances:
                sparse_features = defaultdict(int)
                for feature in instance["ngrams"]:
                    try:
                        sparse_features[self.feature_info[feature]] += 1
                    except:
                        continue
                instance["sparse"] = sparse_features
                writelist.append(instance)         
        new_instances = []
        sparsify(self.training,new_instances)
        self.training = new_instances

        for tset in self.test:
            for instance in tset["instances"]:
                sparse_features = defaultdict(int)
                for feature in instance["ngrams"]:
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
            for feat in instance["features"]:
                featurev.append(feat)
            matrix.append(featurev)
        return matrix

    def model_necessities(self):
        #generate scipy libsvm input
        self.trainlabels_raw = [x["label"] for x in self.training]
        self.labels = set(self.trainlabels_raw)
        labeldict = dict(zip(self.labels,range(len(self.labels))))
        self.labeldict_back = dict(zip(range(len(self.labels)),self.labels))
        if self.scaling == "tfidf":
            self.idf = weight_features.return_idf(self.training)
        self.trainingvectors = self.vectorize(self.training)
        self.training_csr = csr_matrix(self.trainingvectors)
        self.trainlabels = [labeldict[x["label"]] for x in self.training]

    def predict(self,ts):
        testvectors = self.vectorize(ts)
        predictions = []
        for i,t in enumerate(testvectors):
            classification = self.clf.predict(t)
            proba = self.clf.predict_proba(t)
            classification_label = self.labeldict_back[classification[0]]
            if len(ts[0]["meta"]) == 6:
                predictions.append([ts[i]["meta"][5], ts[i]["label"] + " " + classification_label, \
                    " ".join([str(round(x,2)) for x in proba.tolist()[0]])])
            else:
                predictions.append([" ".join([x for x in ts[i]["ngrams"] if not re.search("_",x)]), ts[i]["label"] + " " + classification_label, \
                    " ".join([str(round(x,2)) for x in proba.tolist()[0]])])
        return predictions

    def train_svm(self,params = 10):
        #obtain the best parameter settings for an svm outputcode classifier
        if len(self.labels) > 2:
            print("outputcodeclassifier")
            param_grid = {'estimator__C': [0.001, 0.005, 0.01, 0.5, 1, 5, 10, 50, 100, 500, 1000],
                'estimator__kernel': ['linear','rbf','poly'], 
                'estimator__gamma': [0.0005, 0.002, 0.008, 0.032, 0.128, 0.512, 1.024, 2.048],
                'estimator__degree': [1,2,3,4]}
            model = OutputCodeClassifier(svm.SVC(probability=True))
        else:
            print("svc model")
            param_grid = {'C': [0.001, 0.005, 0.01, 0.5, 1, 5, 10, 50, 100, 500, 1000],
                'kernel': ['linear','rbf','poly'], 
                'gamma': [0.0005, 0.002, 0.008, 0.032, 0.128, 0.512, 1.024, 2.048],
                'degree': [1,2,3,4]}
            model = svm.SVC(probability=True)
        paramsearch = RandomizedSearchCV(model, param_grid, cv=5, verbose=2,n_iter = params,n_jobs=self.jobs) 
        print("Grid search...")
        paramsearch.fit(self.training_csr,numpy.asarray(self.trainlabels))
        print("Prediction...")
        #print the best parameters to the file
        parameters = paramsearch.best_params_
        self.outstring = "best parameter settings:\n"
        for parameter in parameters.keys():
            self.outstring += (parameter + ": " + str(parameters[parameter]) + "\n")
        self.outstring += ("best score: " + str(paramsearch.best_score_) + "\n\n")
        #train an svm outputcode classifier using the best parameters
        if len(self.labels) > 2:
            clf = svm.SVC(probability=True, C=parameters['estimator__C'],
                kernel=parameters['estimator__kernel'],gamma=parameters['estimator__gamma'],
                degree=parameters['estimator__degree'])
            self.clf = OutputCodeClassifier(clf,n_jobs=self.jobs)
            self.clf.fit(self.training_csr,self.trainlabels)
        else:
            self.clf = svm.SVC(probability=True, C=parameters['C'],
                kernel=parameters['kernel'],gamma=parameters['gamma'],
                degree=parameters['degree'])
            self.clf.fit(self.training_csr,self.trainlabels)

    def train_nb(self):
        self.clf = naive_bayes.MultinomialNB()
        self.clf.fit(self.training_csr,self.trainlabels)

    def train_decisiontree(self):
        self.clf = tree.DecisionTreeClassifier()
        self.clf.fit(self.training_csr.toarray(),self.trainlabels)

    def tenfold_train(self,voting,classifiers = [],p = 10):
        kf = cross_validation.KFold(len(self.training), n_folds=10)
        training = deepcopy(self.training)
        feat = deepcopy(self.features)
        fi = deepcopy(self.feature_info)
        if voting == "weighted":
            self.feature_info = {}
            self.features = []
            for instance in self.training:
                instance["sparse"] = defaultdict(int)
                instance["ngrams"] = []
        len_features = len(self.features)
        for i,fn in enumerate(classifiers):
            featurename = "___" + fn
            self.feature_info[featurename] = len_features + i
            self.features.append(featurename)
        for train_index, test_index in kf:
            train = deepcopy([training[x] for x in train_index])
            test = deepcopy([training[y] for y in test_index])
            cl = Classifier(train,test,features = feat,feature_info = fi)
            cl.model_necessities()
            if "svm" in classifiers:
                cl.train_svm(params = p)
                predictions = cl.predict(test)
                for i,j in enumerate(test_index):
                    prediction = int(float(predictions[i][1].split()[1]))
                    self.training[j]["sparse"][self.feature_info["___svm"]] = prediction
                    if prediction == 1:
                        self.training[j]["ngrams"].append("___svm")
            if "nb" in classifiers:
                cl.train_nb()
                predictions = cl.predict(test)
                for i,j in enumerate(test_index):
                    prediction = int(float(predictions[i][1].split()[1]))
                    self.training[j]["sparse"][self.feature_info["___nb"]] = prediction
                    if prediction == 1:
                        self.training[j]["ngrams"].append("___nb")
            if "dt" in classifiers:
                cl.train_decisiontree()
                predictions = cl.predict(test)
                for i,j in enumerate(test_index):
                    prediction = int(float(predictions[i][1].split()[1]))
                    self.training[j]["sparse"][self.feature_info["___dt"]] = prediction
                    if prediction == 1:
                        self.training[j]["ngrams"].append("___dt")               
            
    def return_classification_features(self):
        prediction_features_testset = []
        for tset in self.test:
            prediction_features = []
            predictions = self.predict(tset["instances"])
            for i,prediction in enumerate(predictions):
                prediction_features.append(int(float(predictions[i][1].split()[1])))
            prediction_features_testset.append(prediction_features)
        return prediction_features_testset    

    def add_classification_features(self,featuredict,featurenames,voter):
        if voter == "majority":
            self.feature_info = {}
            len_features = len(self.feature_info.keys())
            for i,fn in enumerate(featurenames):
                self.feature_info[fn] = len_features + i
                self.features.append(fn)
        for i,tset in enumerate(self.test):
            for j,instance in enumerate(tset["instances"]):
                if voter != "arbiter":
                    tset["instances"][j]["sparse"] = defaultdict(int)
                    tset["instances"][j]["ngrams"] = []
                for fn in featurenames:
                    tset["instances"][j]["sparse"][self.feature_info[fn]] = featuredict[i][j][fn]
                    tset["instances"][j]["ngrams"].append(fn)

    def append_classifier_labelings(self):
        len_features = len(self.feature_info.keys())
        self.feature_info["___append"] = len_features
        self.features.append("___append")
        for instance in self.training:
            instance["sparse"][self.feature_info["___append"]] = instance["append"]
            if instance["append"] == 1:
                instance["features"].append("___append")
        for tset in self.test:
            for instance in tset["instances"]:
                instance["sparse"][self.feature_info["___append"]] = instance["append"]
                if instance["append"] == 1:
                    instance["features"].append("___append")

    def output_data(self):
        if re.search(".txt",self.test[0]["out"]):
            outdir = self.test[0]["out"][:-4] + "_"
        else:
            outdir = self.test[0]["out"]
        #output features
        #featureout = codecs.open(outdir + "features.txt","w","utf-8")
        featureout = codecs.open(outdir + "features.txt","w","utf-8")
        for feature in sorted(self.feature_info, key=self.feature_info.get):
            featureout.write(feature + "\t" + str(self.feature_info[feature]) + "\n")
        featureout.close()
        #output trainfile
        #trainout = codecs.open(outdir + "train.txt","w","utf-8")
        trainout = codecs.open(outdir + "train.txt","w","utf-8")
        for instance in self.training:
            trainout.write(instance["label"] + " " + ",".join(instance["ngrams"]) + " " + 
                ",".join([str(x) for x in instance["sparse"].keys()]) + "\n")
        trainout.close()
        #output testfile
        testout = codecs.open(outdir + "test.txt","w","utf-8")
        for i,tset in enumerate(self.test):
            #testout = codecs.open(outdir + "test" + str(i) + ".txt","w","utf-8")
            for instance in tset["instances"]:
                testout.write(instance["label"] + " " + ",".join(instance["ngrams"]) + " " + 
                    ",".join([str(x) for x in instance["sparse"].keys()]) + "\n")

    def test_model(self):
        for tset in self.test:
            testresults = self.predict(tset["instances"])
            #outfile = codecs.open(tset["out"] + "predictions.txt","w","utf-8")
            if re.search(".txt",tset["out"]):
                outstring = tset["out"][:-4] + "_predictions.txt"
            else:
                outstring = tset["out"] + "predictions.txt"
            outfile = codecs.open(outstring,"w","utf-8")
            if self.outstring:
                outfile.write(self.outstring)
            for instance in testresults:
                outfile.write("\t".join(instance) + "\n") 
            outfile.close()

    def save_model(self):
        for tset in self.test:
            outfile = tset["out"][:-4] + "_model.joblib.pkl"
            with open(outfile, 'wb') as fid:
                cPickle.dump(self.clf, fid)    
            #_ = joblib.dump(, outfile, compress=9)
            #outvocabulary = codecs.open(tset["out"] + "vocabulary.txt","w","utf-8")
            outstring = tset["out"][:-4] + "_vocabulary.txt"
            outvocabulary = codecs.open(outstring,"w","utf-8")
            for feature in self.features:
                outvocabulary.write(feature + "\n")
            outvocabulary.close() 
            outidf = codecs.open(tset["out"][:-4] + "_idfs.txt","w","utf-8")
            for key in self.idf.keys():
                outidf.write(str(key) + "\t" + str(self.idf[key]) + "\n")
            outidf.close()

