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

    def __init__(self,trainlist,testlist,directory=False, vocabulary=False):
        #if type(trainlist[0]).__name__ == 'list':
        #    self.training=[]
        #    self.meta_training=[]
        #    self.test=[]
        #    self.meta_test=[]
        #    for i,x in enumerate(trainlist):
        #        self.training.append(x[0])
        #        self.meta_training.append(x[1])
        #    for i,x in enumerate(testlist):
        #        self.test.append(x[0])
        #        self.metatest.append(x[1])
        #else:
        self.training=trainlist
        self.test=testlist
        self.directory=directory
        self.feature_info=vocabulary

    def classify(self, algorithm, arguments, prune=False, select=False, timelabels=False):
        if algorithm=="knn":
            self.perform_knn(arguments,prune,select,timelabels)
        elif algorithm=="lcs":
            self.perform_lcs(arguments,prune,select,timelabels)
        elif algorithm=="ibt":
            self.informed_baseline_date(arguments)

    #def set_directory(self,directory):
    #    self.directory=directory
    
    #def set_feature_info(self,feature_infolines):
    #    self.feature_info={}
    #    for line in feature_infolines:
    #        tokens=line.split("\t")
    #        self.feature_info[int(tokens[0])]=[tokens[1].strip()]
    
    def adjust_index_space(self,ranked_list,value_dict,boundary):
        #create new feature_info dictionary
        new_feature_info={}
        feature_status={}        

        # if time_labels:
        #     time_label_vocab={}
        #     time_label=defaultdict(int)
        #     for instance in self.training:
        #         tl=instance[1].split("\t")[3]
        #         time_label[tl] += 1
        #     time_label_set=list(set(time_label.keys())) 
        #     for i,tl in enumerate(time_label_set):
        #         new_feature_info[i+1]=[tl,0,0]
        #         time_label_vocab[tl]=i+1
        
        #assign new feature_info indexes based on the ranked list
        for i,f in enumerate(ranked_list[:boundary]):
            # if time_labels: 
            #     new_index=i+len(time_label_set)+1
            # else:
            new_index=i+1
            #feature_tokens=self.feature_info[old_index]
            #feature_tokens.append(value_dict[old_index])
            new_feature_info[new_index]=self.feature_info[f] + value_dict[f]
            feature_status[f]=new_index
        self.feature_info=new_feature_info
        #set status of all pruned features to False
        for f in ranked_list[boundary:]:
            feature_status[f]=False

        #adjust instances
        index = 0
        for instance in self.training:
            new_features=[]
            tokens=instance[0].split(",")
            token_features=tokens[:-1]
            # if time_labels:
            #     tl=instance[1].split("\t")[3]
            #     tli=time_label_vocab[tl]
            #     new_features.append(tli)
            for token in token_features:
                feature_index=int(token)
                if feature_status[feature_index]:
                    new_index=feature_status[feature_index]
                    new_features.append(new_index)
            
            if len(new_features) == 0:
                print "before train",new_features,self.train[index],self.train[index+1]
                self.training.pop(index)
                print "after train",self.train[index]
            else:
                self.training[i]=[",".join(["%s" % el for el in sorted(new_features)]) + "," + tokens[-1],instance[1]]
                index += 1
            
        index = 0
        for instance in self.test: 
            new_features=[]
            tokens=instance[0].split(",")
            token_features=tokens[:-1]
            # if time_labels:
            #     tl=instance[1].split("\t")[4]
            #     try:
            #         tli=time_label_vocab[tl]
            #     except KeyError:
            #         tle=time_label_vocab["-"]
            #     new_features.append(tli)
            for token in token_features:
                feature_index=int(token)
                try: 
                    if feature_status[feature_index]:
                        new_index=feature_status[feature_index]
                        new_features.append(new_index)
                except KeyError:
                    continue
            if len(new_features) == 0:
                print "before test",new_features,self.test[index],self.test[index+1]
                self.test.pop(index)
                print "after test",self.test[index]
            else:   
                self.test[i]=[",".join(["%s" % el for el in sorted(new_features)]) + "," + tokens[-1],instance[1]]
                index += 1

    def prune_features(self,minimum_threshold,classifier):
        #generate feature_frequency dict
        feature_freq=defaultdict(int)
        if classifier == "knn":
            for instance in self.training:
                features=instance[0].split(",")[:-1]
                for feature in features:
                    feature_freq[int(feature)] += 1
        elif classifier == "lcs":
            for instance in self.training:
                tokens=instance.split(" ")
                filename=tokens[0]
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
                tokens=instance[0].split(",")
                features=tokens[:-1]
                label=tokens[-1]
                label_freq[label] += 1
                for feature in features:
                    label_feature_freq[label][int(feature)] += 1
        elif classifier == "lcs":
            print "counting features..."
            for instance in self.training:
                tokens=instance.split(" ")
                filename=tokens[0]
                label=tokens[1]
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
                probs1.append(label_feature_freq[label][f] / frequency)
                probs0.append((label_freq[label]-label_feature_freq[label][f]) / inverse_frequency)
            entropy1=(-sum([p * math.log(p,2) for p in probs1 if p!=0])) * p1
            entropy0=(-sum([p * math.log(p,2) for p in probs0 if p!=0])) * p0
            entropy_after=entropy1 + entropy0 #class entropy of instances with f
            infogain=entropy_before-entropy_after #infogain score
            return infogain
            
        if classifier == "knn":
            for f in self.feature_info.keys(): #compute for each feature
                frequency=int(self.feature_info[f][2])
                ig=compute_infogain(f,frequency)
                feature_infogain[f]=ig
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
            for f in ranked_feature_freq[:boundary]:
                frequency=feature_freq[f]
                ig=compute_infogain(f,frequency)
                feature_infogain[f]=ig

        return feature_infogain

    def select_features(self,num_features,prune,classifier):
        #make a file of the instances and perform infogain weighting (based on timbl)
        feature_weights=self.infogain(classifier,prune)
        selected_features=sorted(feature_weights, key=feature_weights.get, reverse=True)    
        if classifier == "knn":
            self.adjust_index_space(selected_features,feature_weights,num_features)
            # if timelabels:
            #     weightout=codecs.open(self.directory + "weights","w","utf-8")
            #     for i in sorted(self.feature_info.keys()):
            #         weightout.write(":" + str(i) + " STIMBLWEIGHT=" + str( self.feature_info[i][-1]) + "\n")
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

        if select:
            self.select_features(int(select),int(prune),"lcs")
        
        train=codecs.open(classification_dir + "train","w","utf-8")
        for i in self.training:
            train.write(i)
        train.close()
        test=codecs.open(classification_dir + "test","w","utf-8")
        for t in self.test:
            test.write(t)
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
                tokens=t.split(" ")
                if tokens[1].strip() == "before":
                    tl=self.metatraining[i].split("\t")[4]
                    tokens[1]=tl
                    train.write(" ".join(tokens) + "\n")
            train.close()
            test=codecs.open(classification_dir + "test","w","utf-8")
            for i,t in enumerate(self.test):
                tokens=t.split(" ")
                tl=self.metatest[i].split("\t")[4]
                tokens[1]=tl
                test.write(" ".join(tokens) + "\n")
            test.close()
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
            self.select_features(int(select),int(prune),"knn",timelabels)
        
        #if set on, add timelabels as features to instances
        if timelabels:
            new_feature_info = []
            time_label_vocab={}
            time_label=defaultdict(int)
            #generate a list of all time labels
            for instance in self.training:
                tl=instance[1].split("\t")[3]
                time_label[tl] += 1
            time_label_set=list(set(time_label.keys()))
            #make a new feature_info_dict starting with the timelabels as features  
            # for i,tl in enumerate(time_label_set):
            #     feature_info[i+1]=[tl,0,0]
            #     time_label_vocab[tl]=i+1    
            print self.feature_info

        train=self.directory + "train"
        test=self.directory + "test"
        trainingout=open(train,"w")
        testout=open(test,"w")
        feature_info_out=codecs.open(self.directory + "vocabulary","w","utf-8")
        for instance in self.training:
            trainingout.write(instance[0])
        for instance in self.test:
            testout.write(instance[0])
        for feature_index in sorted(self.feature_info.keys()):
            info=str(self.feature_info[feature_index][0])
            for field in self.feature_info[feature_index][1:]:
                info=info + "\t" + unicode(field)
            feature_info_out.write(str(feature_index) + "\t" + info + "\n")
        if timelabels:
            weight=self.directory + "weights"
            weightout=codecs.open(weight,"w","utf-8")
            for i in sorted(self.feature_info.keys()):
                weightout.write(":" + str(i) + " STIMBLWEIGHT=" + str(self.feature_info[i][-1]) + "\n")
            weightout.close()
        trainingout.close()
        testout.close()
        feature_info_out.close()
        print "performing knn..."
        for k in klist:
            print "k=",k
            classification=self.directory + "classification" + k + " .txt"
            if timelabels:
                os.system("stimbl -n " + str(len(self.feature_info)+1) + " -f " + train + " -W " + weight + " -v -D -i -m 3 -k " + k + " < " + test + " > " + classification) 
            else:
                os.system("stimbl -n " + str(len(self.feature_info)+1) + " -f " + train + " -v -D -i -m 3 -w 2 -k " + k + " < " + test + " > " + classification) 

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
