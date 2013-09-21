#!/usr/bin/env python

import argparse
from classifier import Classifier
import codecs
import os
import re
import multiprocessing
from collections import defaultdict
import informed_baseline_time

"""
Script to perform classification with a chosen algorithm and parameter settings. The used data should be in the right format.
"""
parser=argparse.ArgumentParser(description="Script to perform classification with a chosen algorithm and parameter settings. The used data should be in the right format.")
parser.add_argument('-i', action='store', required=False, help="file with either all instances or training instances")
parser.add_argument('-v', action='store', required=True, choices=["test","n-fold","looe"], help="specify the type of validation")
parser.add_argument('-t', action='store', required=False, help="[TEST] give the file with test data")
parser.add_argument('-n', action='store', required=False, help="[N-FOLD] specify n")
parser.add_argument('-l', action='store', required=False, nargs="+", help="[LOOE] specify the type of leave-one-out (regular,inner_domain or outer_domain) and (unless the type is \'regular\') a file with domain-event relations")
parser.add_argument('-m', action='store', required=False, nargs="+", help="[LOOE] specify a meta-file and the column of the event in the metafile ")
parser.add_argument('--vocab', action='store', required=False, help="[OPTIONAL] give a file with a vocabulary to use for pruning and feature selection")
parser.add_argument('-c', action='store', required=True, choices=["lcs","knn","ibt","dist"], help="the classifier")
parser.add_argument('-a', action='store', required=False, nargs='+', help="the arguments needed for the chosen algorithm:\n\n[LCS] specify respectively the directory in which classification is performed (make sure the config file and optionally a data-directory with indexes are present in this directory) and the directory in which files are stored\n[KNN] specify value(s) of k (the classifier will be ran for each value of k)\n[IBT] for the informed baseline time, choose to set the system to dummy by filling in \"dummy\"")
parser.add_argument('-p', action='store', required=False, help="[OPTIONAL] to prune features, give a minimum frequency threshold")
parser.add_argument('-s', action='store', required=False, help="[OPTIONAL] to select features based on their infogain, specify the number of features to select") 
parser.add_argument('--tl', action='store_true', required=False, help="[OPTIONAL] set \'tl\' in order to have second stage or hidden timelabel classification")
parser.add_argument('--parralel', action='store_true', required=False, help="choose whether distinct train and test sets are ran in parrallel")

args=parser.parse_args() 
if args.i:
    instance_file=codecs.open(args.i,"r","utf-8")
    instances=instance_file.readlines()
    instance_file.close()
validation=args.v
classifier=args.c
arguments=args.a
if args.vocab:
    vocabulary_read=codecs.open(args.vocab,"r","utf-8")
    vocabulary_list=list(vocabulary_read.readlines())
    vocabulary_read.close()
    vocabulary = {}
    for entry in vocabulary_list:
        tokens = entry.strip().split("\t")
        vocabulary[tokens[0]] = [tokens[1]]
else:
    vocabulary=False

def classify(instance_dict,directory=False):
    traininglines = instance_dict["training"]
    testlines = instance_dict["test"]
    metalines = instance_dict["meta"]
    cl=Classifier(traininglines,testlines,metalines,directory,vocabulary)
    cl.classify(classifier,arguments,args.p,args.s,args.tl)

if validation=="test":
    test_instances=codecs.open(args.t,"r","utf-8")
    directory="/".join(args.t.split("/")[:-1]) + "/"
    classify(instances,test_instances.readlines(),directory)
    test_instances.close()

elif validation=="looe":
    meta_parameters = args.m
    meta=codecs.open(meta_parameters[0],"r","utf-8")
    metaread=meta.readlines()
    event_column=int(meta_parameters[1])
    event_train_test=defaultdict(lambda : defaultdict(list))
    event_bounds=[]
    event=""
    meta=[]
    for i,instance in enumerate(metaread):
        tokens=instance.split("\t")
        instance_event=tokens[event_column]
        if instance_event != event:
            event_bounds.append((instance_event,i))
            if not event == "":
                event_train_test[event]["meta"] = meta
            event=instance_event
            meta = [] 
        meta.append(instance)

    if classifier == "ibt":
        d="/".join(meta_parameters[0].split("/")[:-1]) + "/" + "baseline/"
        os.system("mkdir " + d)
        for event in event_train_test.keys():
            print event
            event_write = event
            if re.search(" ",event_write):
                event_write="_".join(event_write.split(" "))
            d_event = d + event_write + "/"
            os.system("mkdir " + d_event)
            meta = event_train_test[event]["meta"]
            informed_baseline_time.ibt(meta,d_event,arguments)

    else:
        parameters = args.l
        if classifier == "knn":
            delimiter = ","
        elif classifier == "lcs":
            delimiter = " "

        for i,event_bound in enumerate(event_bounds):
            event=event_bound[0]
            start=event_bound[1]
            if i==len(event_bounds)-1:
                test=[]
                for i in range(len(instances[start:])):
                    values = instances[start+i].strip().split(delimiter)
                    meta_values = metaread[start+i].strip().split("\t")
                    instance = {"features":values[:-1],"label":values[-1],"meta":meta_values}
                    test.append(instance)
                training=[]
                for i in range(len(instances[:start])):
                    values = instances[i].strip().split(delimiter)
                    meta_values = metaread[i].strip().split("\t")
                    instance = {"features":values[:-1],"label":values[-1],"meta":meta_values}
                    training.append(instance)
            else:
                end=event_bounds[i+1][1]
                test=[]
                for i in range(len(instances[start:end])):
                    values = instances[start+i].strip().split(delimiter)
                    meta_values = metaread[start+i].strip().split("\t")
                    instance = {"features":values[:-1],"label":values[-1],"meta":meta_values}
                    test.append(instance)
                training=[]
                for i in range(len(instances)):
                    values = instances[i].strip().split(delimiter)
                    meta_values = metaread[i].strip().split("\t")
                    instance = {"features":values[:-1],"label":values[-1],"meta":meta_values}
                    training.append(instance)
                del training[start:end]
            event_train_test[event]["training"] = training
            event_train_test[event]["test"] = test
            
        if parameters[0]=="regular":
            events_done = ["ajaaz_f11","ajautr_f12","psvutr_f11","utraz_s11","ajaaz_f12","tweaja_s12","utraz_s12","ajafey_s11","azpsv_f11","psvfey_f12","twefey_f12","utrpsv_f12","ajapsv_s12","feypsv_f11","psvtwe_f12","utraja_f11"]
            for event in event_train_test.keys():
                if not event in events_done:
                    print event
                    event_write = event
                    if re.search(" ",event_write):
                        event_write="_".join(event_write.split(" "))
                    d="/".join(args.i.split(".txt")[0].split("/")[:-1]) + "/" + event_write + "/all_to_one/"
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
                        p=multiprocessing.Process(target=classify,args=[event_train_test[event],d])
                        p.start()
                        #except OSError:
                        #    classify(event_train_test[event],d)
                    else:
                        classify(event_train_test[event],d)
        
        else:
            domain_events=codecs.open(parameters[3],"r","utf-8")
            domain_event_hash=defaultdict(list)
            for line in domain_events.readlines():
                tokens=line.strip().split("\t")
                domain_event_hash[tokens[0]].append(tokens[1])
            domain_events.close()

            if parameters[0]=="outer_domain":
                domains=domain_event_hash.keys()
                for i,domain in enumerate(domains):
                    print domain
                    training=[]
                    for j in range(len(domains)):
                        if j != i:
                            train_domain=domain_event_hash[domains[j]]
                            for train_event in train_domain:
                                training.extend(event_train_test[train_event][1])
                    for event in domain_event_hash[domain]:
                        test=event_train_test[event][1]
                        if re.search(" ",event):
                            event="_".join(event.split(" "))
                        print event
                        d="/".join(args.i.split(".txt")[0].split("/")[:-1]) + "/" + args.a + "/" + event + "/outer_domain/"
                        if not os.path.exists(d):
                            if not os.path.exists("/".join(d.split("/")[:-2])):
                                if not os.path.exists("/".join(d.split("/")[:-1])):
                                    os.system("mkdir " + "/".join(d.split("/")[:-1]))
                                os.system("mkdir " + "/".join(d.split("/")[:-2]))
                            os.system("mkdir " + d) 
                        if args.parralel:
                            p=multiprocessing.Process(target=classify,args=[training,test,d])
                            p.start()
                        else:
                            classify(training,test,d)
                            
            elif parameters[0]=="inner_domain":
                domains=domain_event_hash.keys()
                for i,domain in enumerate(domains):
                    print domain
                    for event in domain_event_hash[domain]:
                        train_events=list(domain_event_hash[domain])
                        train_events.remove(event)
                        training=[]
                        for te in train_events:
                            training.extend(event_train_test[te][1]) 
                        test=event_train_test[event][1]
                        if re.search(" ",event):
                            event="_".join(event.split(" "))
                        print event
                        d="/".join(args.i.split(".txt")[0].split("/")[:-1]) + "/" + args.a + "/" + event + "/" + "/" + "inner_domain"
                        if not os.path.exists(d):
                            if not os.path.exists("/".join(d.split("/")[:-2])):
                                if not os.path.exists("/".join(d.split("/")[:-1])):
                                    os.system("mkdir " + "/".join(d.split("/")[:-1]))
                                os.system("mkdir " + "/".join(d.split("/")[:-2]))
                            os.system("mkdir " + d) 
                        
                        if args.parralel:
                                p=multiprocessing.Process(target=classify,args=[training,test,d])
                                p.start()
                        else:
                            classify(training,test,d)

