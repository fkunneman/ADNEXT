#!/usr/bin/env python

import argparse
from classifier import Classifier
import codecs
import os
import re
import multiprocessing
from collections import defaultdict
import informed_baseline_time
import random

"""
Script to perform classification with a chosen algorithm and parameter settings. The used data should be in the right format.
"""
parser = argparse.ArgumentParser(description = "Script to perform classification with a chosen algorithm and parameter settings. The used data should be in the right format.")
parser.add_argument('-i', action = 'store', required = False, help = "file with either all instances or training instances")
parser.add_argument('-d', action = 'store', default = "\t", help = "the delimiter between features and the label in the instance file")
parser.add_argument('-v', action = 'store', required = True, choices = ["test","n-fold","learning_curve","looe"], help = "specify the type of validation")
parser.add_argument('-t', action = 'store', required = False, help = "[TEST] give the file with test data")
parser.add_argument('-n', action = 'store', required = False, help = "[N-FOLD] specify n")
parser.add_argument('-m', action = 'store', required = False, nargs = "+", help = "[LOOE] specify a meta-file and the column of the event in the metafile ")
parser.add_argument('-c', action = 'store', required = True, choices = ["lcs","knn","ibt","dist","random","majority"], help = "the classifier")
parser.add_argument('-a', action = 'store', required = False, nargs = '+', help = "the arguments needed for the chosen algorithm:\n\n[LCS] specify the directory in which classification is performed (make sure the config file and optionally a data-directory with indexes are present in this directory)\n[KNN] specify value(s) of k (the classifier will be ran for each value of k)\n[IBT] for the informed baseline time, choose to set the system to dummy by filling in \"dummy\"")
parser.add_argument('-p', action = 'store', required = False, help = "[OPTIONAL] to prune features, give a minimum frequency threshold")
parser.add_argument('-s', action = 'store', required = False, help = "[OPTIONAL] to select features based on their infogain, specify the number of features to select") 
parser.add_argument('--tl', action = 'store_true', required = False, help = "[OPTIONAL] set \'tl\' in order to have second stage or hidden timelabel classification")
parser.add_argument('--parralel', action = 'store_true', required = False, help = "choose whether distinct train and test sets are ran in parrallel")

args = parser.parse_args() 
if args.i:
    instance_file = codecs.open(args.i,"r","utf-8")
    instances_raw = instance_file.readlines()
    instance_file.close()
    instances = []
    for instance in instances_raw:    
        values = instance.strip().split(args.d)
        instances.append({"features":values[:-1],"label":values[-1],"meta":[]})

validation = args.v
classifier = args.c
arguments = args.a

def classify(instance_dict,directory = False):
    traininglines = instance_dict["training"]
    testlines = [instance_dict["test"]]
    metalines = instance_dict["meta"]
    cl = Classifier(traininglines,testlines)
    cl.classify(classifier,arguments,args.p,args.s,args.tl)

if validation == "test":
    if classifier == "random":
        outfile = open("/".join(args.i.split("/")[:-1]) + "/random.txt","w")
        #extract list of possible labels
        labels = []
        for instance in instances:
            labels.append(instance["label"])
        for instance in instances:
            classification = random.choice(labels)
            outfile.write(instance["label"] + " " + classification + "\n")
        outfile.close()

    elif classifier == "majority":
        outfile = open("/".join(args.i.split("/")[:-1]) + "/majority.txt","w")
        #extract majority class
        class_frequency = defaultdict(int)
        for instance in instances:
            class_frequency[instance["label"]] + =  1
        majority_class = sorted(class_frequency, key = class_frequency.get, reverse = True)[0]
        print majority_class
        for instance in instances:
            outfile.write(instance["label"] + " " + majority_class + "\n")
        outfile.close()

    else:
        test_instances = codecs.open(args.t,"r","utf-8")
        directory = "/".join(args.t.split("/")[:-1]) + "/"
        classify({"training":instances,testtest_instances.readlines(),directory)
        test_instances.close()

elif validation == "n-fold":
    main_dir = "/".join(args.i.split("/")[:-1]) + "/" 
    #sort instances based on their label       
    sorted_instances = sorted(instances, key = lambda k: k['label'])
    #make folds based on taking the n-th instance as test
    n = int(args.n)
    size = len(sorted_instances)
    for i in range(n):
        fold_dir = main_dir + "fold_" + str(i) + "/"
        os.system("mkdir " + fold_dir)
        print fold_dir
        train_test = defaultdict(list)
        train_test["training"] = list(sorted_instances)
        j = i
        offset = 0
        while j < size:
            train_test["test"].append(sorted_instances[j])
            #print i,j-offset,len(train_test["train"]),j,size,len(sorted_instances)
            del train_test["training"][j-offset]
            j + =  n
            offset + =  1
        train_test["meta"] = []
        classify(train_test,fold_dir)

elif validation == "learning_curve":
    main_dir = "/".join(args.i.split("/")[:-1]) + "/learning_curve/" 
    #sort instances based on their label       
    sorted_instances = sorted(instances, key = lambda k: k['label'])
    #split train and static test
    size = len(sorted_instances)
    train = list(sorted_instances)
    test = []
    j = 0
    offset = 0
    while j < size:
        test.append(sorted_instances[j])
        #print i,j-offset,len(train_test["train"]),j,size,len(sorted_instances)
        del train[j-offset]
        j + =  10
        offset + =  1
    logajumps = [2,5,10]
    loga = 10

    trainincr = list(train)
    trainhist = []
    print train
    while loga < len(train):
        for jump in logajumps:
            cycle_loga = loga * jump
            add = cycle_loga - len(trainhist)
            inds = int(len(trainincr) / add)
            offset = 0
            if cycle_loga > len(train):
                train_test = {"training":train,"test":test, "meta":[]}
                classification_dir = main_dir + "train_total/"
                os.system("mkdir " + classification_dir)
                classify(train_test,classification_dir)
                break
            else:
                for i in range(add):
                    trainhist.append(trainincr[(i*inds)-offset])
                    del trainincr[(i*inds)-offset]
                    offset + =  1
                train_test = {"training":trainhist,"test":test, "meta":[]}
                classification_dir = main_dir + "train_" + str(cycle_loga) + "/"
                os.system("mkdir " + classification_dir)
                classify(train_test,classification_dir)
        loga = cycle_loga

elif validation == "looe":
    print "generating train-test"
    meta_parameters = args.m
    meta = codecs.open(meta_parameters[0],"r","utf-8")
    metaread = meta.readlines()
    event_column = int(meta_parameters[1])
    event_train_test = defaultdict(lambda : defaultdict(list))
    event_instances = defaultdict(list)
    event = ""
    meta = []
    eventcount = 0
    for i,record in enumerate(metaread):
        tokens = instance.split("\t")
        instance_event = tokens[event_column]
        if instance_event ! =  event:
            eventcount = 0
            if not event == "":
                event_train_test[event]["test"] = event_instances
                event_train_test[event]["meta"] = meta
            event = instance_event
            event_instances = []
            meta = []
            test = []
        eventcount + =  1 
        meta.append(record)
        test.append(instances[i])

    if classifier == "ibt":
        d = "/".join(meta_parameters[0].split("/")[:-1]) + "/" + "baseline/"
        os.system("mkdir " + d)
        for event in event_train_test.keys():
            # print event
            event_write = event
            if re.search(" ",event_write):
                event_write = "_".join(event_write.split(" "))
            d_event = d + event_write + "/"
            os.system("mkdir " + d_event)
            meta = event_train_test[event]["meta"]
            informed_baseline_time.ibt(meta,d_event,arguments)

    else:
        parameters = args.l
        for i in range(len(metaread)):
            meta_values = metaread[i].strip().split("\t")
            instances[i]["meta"] = meta_values
        for i,event_bound in enumerate(event_bounds):
            event = event_bound[0]
            start = event_bound[1]
            if i == len(event_bounds)-1:
                test = instances[start:]
                training = instances[:start]
            else:
                end = event_bounds[i+1][1]
                test = instances[start+i]
                training = list(instances)
                del training[start:end]
            event_train_test[event]["training"] = training
            event_train_test[event]["test"] = test
            
        if parameters[0] == "regular":
            #events_done = ["utrfey_s11","ajaaz_f11","ajautr_f12","psvutr_f11","utraz_s11","ajaaz_f12","tweaja_s12","utraz_s12","ajafey_s11","azpsv_f11","psvfey_f12","twefey_f12","utrpsv_f12","ajapsv_s12","feypsv_f11","psvtwe_f12","utraja_f11"]
            print "classification"
            for event in event_train_test.keys():
                # if not event in events_done:
                print event
                # if event == "azfey_f11":
                #     print event
                event_write = event
                if re.search(" ",event_write):
                    event_write = "_".join(event_write.split(" "))
                d = "/".join(args.i.split(".txt")[0].split("/")[:-1]) + "/" + event_write + "/all_to_one/"
                print d
                if not os.path.exists(d):
                    if not os.path.exists("/".join(d.split("/")[:-1])):
                        if not os.path.exists("/".join(d.split("/")[:-2])):
                            print "mkdir " + "/".join(d.split("/")[:-2])
                            os.system("mkdir " + "/".join(d.split("/")[:-2]))
                        print "mkdir " + "/".join(d.split("/")[:-1])
                        os.system("mkdir " + "/".join(d.split("/")[:-1]))
                    os.system("mkdir " + d)
                if args.parralel:
                    # print event
                    # print len(event_train_test[event]["meta"])
                    #try:
                    p = multiprocessing.Process(target = classify,args = [event_train_test[event],d])
                    p.start()
                    #except OSError:
                    #    classify(event_train_test[event],d)
                else:
                    classify(event_train_test[event],d)
        
        else:
            domain_events = codecs.open(parameters[3],"r","utf-8")
            domain_event_hash = defaultdict(list)
            for line in domain_events.readlines():
                tokens = line.strip().split("\t")
                domain_event_hash[tokens[0]].append(tokens[1])
            domain_events.close()

            if parameters[0] == "outer_domain":
                domains = domain_event_hash.keys()
                for i,domain in enumerate(domains):
                    print domain
                    training = []
                    for j in range(len(domains)):
                        if j ! =  i:
                            train_domain = domain_event_hash[domains[j]]
                            for train_event in train_domain:
                                training.extend(event_train_test[train_event][1])
                    for event in domain_event_hash[domain]:
                        test = event_train_test[event][1]
                        if re.search(" ",event):
                            event = "_".join(event.split(" "))
                        print event
                        d = "/".join(args.i.split(".txt")[0].split("/")[:-1]) + "/" + args.a + "/" + event + "/outer_domain/"
                        if not os.path.exists(d):
                            if not os.path.exists("/".join(d.split("/")[:-2])):
                                if not os.path.exists("/".join(d.split("/")[:-1])):
                                    os.system("mkdir " + "/".join(d.split("/")[:-1]))
                                os.system("mkdir " + "/".join(d.split("/")[:-2]))
                            os.system("mkdir " + d) 
                        if args.parralel:
                            p = multiprocessing.Process(target = classify,args = [training,test,d])
                            p.start()
                        else:
                            classify(training,test,d)
                            
            elif parameters[0] == "inner_domain":
                domains = domain_event_hash.keys()
                for i,domain in enumerate(domains):
                    print domain
                    for event in domain_event_hash[domain]:
                        train_events = list(domain_event_hash[domain])
                        train_events.remove(event)
                        training = []
                        for te in train_events:
                            training.extend(event_train_test[te][1]) 
                        test = event_train_test[event][1]
                        if re.search(" ",event):
                            event = "_".join(event.split(" "))
                        print event
                        d = "/".join(args.i.split(".txt")[0].split("/")[:-1]) + "/" + args.a + "/" + event + "/" + "/" + "inner_domain"
                        if not os.path.exists(d):
                            if not os.path.exists("/".join(d.split("/")[:-2])):
                                if not os.path.exists("/".join(d.split("/")[:-1])):
                                    os.system("mkdir " + "/".join(d.split("/")[:-1]))
                                os.system("mkdir " + "/".join(d.split("/")[:-2]))
                            os.system("mkdir " + d) 
                        
                        if args.parralel:
                                p = multiprocessing.Process(target = classify,args = [training,test,d])
                                p.start()
                        else:
                            classify(training,test,d)
