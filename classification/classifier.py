#! /usr/bin/env python

from __future__ import division
import codecs
import os
import re
import time_functions
import datetime
from collections import defaultdict
import math

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

    def informed_baseline_date(self,args):
        
        future=re.compile(r"(straks|zometeen|vanmiddag|vanavond|vannacht|vandaag|morgen|morgenavond|morgenmiddag|morgenochtend|overmorgen|weekend|maandag|dinsdag|woensdag|donderdag|vrijdag|zaterdag|zondag|maandagavond|dinsdagavond|woensdagavond|donderdagavond|vrijdagavond|zaterdagavond|zondagavond|januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december|nog.+(dagen|slapen))")       
        today=re.compile(r"(straks|zometeen|vanmiddag|vanavond|vannacht|vandaag)")
        tomorrow=re.compile(r"morgen(avond|middag|ochtend)?")
        day_after_t=re.compile(r"overmorgen")
        weekend=re.compile(r"\b(weekend)\b")
        weekday=re.compile(r"(maandag|dinsdag|woensdag|donderdag|vrijdag|zaterdag|zondag)(avond|middag|ochtend)?")
        weekdays=["maandag","dinsdag","woensdag","donderdag","vrijdag","zaterdag","zondag"]
        month=re.compile(r"(\d{1,2}) (januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december)")
        months=["januari","februari","maart","april","mei","juni","juli","augustus","september","oktober","november","december"]
        nog=re.compile(r"nog(.+) (dagen|slapen)")
        num=re.compile(r"\b(twee|drie|vier|vijf|zes|zeven|acht|negen|tien|elf|twaalf|dertien|veertien|vijftien|zestien|zeventien|achttien|negentien|twintig|eenentwintig|1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21)\b")
        wordnums=["twee","drie","vier","vijf","zes","zeven","acht","negen","tien","elf","twaalf","dertien","veertien","vijftien","zestien","zeventien","achttien","negentien","twintig","eenentwintig"]
        
        if len(args)>0:
            dummy=True
        else:
            dummy=False
        
        tested_instances=[]
        for i in self.test:
            tokens=i.split("\t")
            label=tokens[4]
            date=tokens[5]
            text=tokens[8]
            text=text.strip()
            if future.search(text):
                if today.search(text):
                    tokens[2]=tokens[2] + "\t" + "0"
                elif tomorrow.search(text):
                    tokens[2]=tokens[2] + "\t" + "-1"
                elif day_after_t.search(text):
                    tokens[2]=tokens[2] + "\t" + "-2"
                else:
                    if dummy:
                        tokens[2]=tokens[2] + "\t" + "nt"
                    else:
                        tweet_date=time_functions.return_datetime(date,setting="vs")
                        if weekend.search(text) or weekday.search(text):
                            tweet_weekday=tweet_date.weekday()
                            if weekend.search(text):
                                ref_weekday=weekdays.index("zaterdag")
                            elif weekday.search(text):
                                ref_weekday=weekdays.index(weekday.search(text).groups()[0])
                            if ref_weekday == tweet_weekday:
                                tokens[2]=tokens[2] + "\t" + "0"
                            else:
                                if tweet_weekday < ref_weekday:
                                    dif=ref_weekday - tweet_weekday
                                else:
                                    dif=ref_weekday + (7-tweet_weekday)
                                estimate=str(dif * -1)
                                tokens[2]=tokens[2] + "\t" + estimate
                        elif month.search(text):
                            ref=month.search(text).groups()
                            day=int(ref[0])
                            mth=months.index(ref[1]) + 1
                            tweet_month=tweet_date.month
                            tweet_year=tweet_date.year
                            if mth >= tweet_month:
                                year=tweet_year
                            else:
                                year=tweet_year + 1
                            try:
                                ref_date=datetime.datetime(year,mth,day,0,0,0)
                                tte=str(time_functions.timerel(ref_date,tweet_date,"day") * -1)
                                if int(tte) < -21:
                                    tte="early"
                                tokens[2]=tokens[2] + "\t" + tte
                            except ValueError:
                                continue
                        elif nog.search(text):
                            in_between=nog.search(text).groups()[0]
                            numbers=num.findall(in_between)
                            if len(numbers) == 1:
                                number=numbers[0]
                                if re.search(r"[a-z]",number):
                                    number=wordnums.index(number) + 2
                                number=str(int(number) * -1)
                                if int(number) < -21:
                                    number="early"
                                tokens[2]=tokens[2] + "\t" + number
                            else:
                                tokens[2]=tokens[2] + "\t" + "nt"
                        else:
                            tokens[2]=tokens[2] + "\t" + "nt"
            else:
                tokens[2]=tokens[2] + "\t" + "nt"
            tested_instances.append("\t".join(tokens))
        if dummy:
            baseline_out=codecs.open(self.directory + "baseline_dummy.txt","w","utf-8")
        else: 
            baseline_out=codecs.open(self.directory + "baseline.txt","w","utf-8")
        for ti in tested_instances:
            baseline_out.write(ti)
        baseline_out.close()
