#!/usr/bin/env python

import argparse
from classifier import Classifier
import codecs
import os
import re
import multiprocessing
from collections import defaultdict

"""
Script to perform classification with a chosen algorithm and parameter settings. The used data should be in the right format.
"""
parser=argparse.ArgumentParser(description="Script to perform classification with a chosen algorithm and parameter settings. The used data should be in the right format.")
parser.add_argument('-i', action='store', required=True, help="file with either all instances or training instances")
parser.add_argument('-v', action='store', required=True, choices=["test","n-fold","looe"], help="specify the type of validation")
parser.add_argument('-t', action='store', required=False, help="[TEST] give the file with test data")
parser.add_argument('-n', action='store', required=False, help="[N-FOLD] specify n")
parser.add_argument('-l', action='store', required=False, nargs="+", help="[LOOE] specify the type of leave-one-out (regular,inner_domain or outer_domain), a meta-file, the column of the event in the metafile and (unless the type is \'regular\') a file with domain-event relations")
parser.add_argument('--vocab', action='store', required=False, help="[OPTIONAL] give a file with a vocabulary to use for pruning and feature selection")
parser.add_argument('-c', action='store', required=True, choices=["lcs","knn","ibt"], help="the classifier")
parser.add_argument('-a', action='store', required=False, nargs='+', help="the arguments needed for the chosen algorithm:\n\n[LCS] specify respectively the directory in which classification is performed (make sure the config file and optionally a data-directory with indexes are present in this directory) and the directory in which files are stored\n[KNN] specify value(s) of k (the classifier will be ran for each value of k)\n[IBT] for the informed baseline time, choose to set the system to dummy by filling in \"dummy\"")
parser.add_argument('-p', action='store', required=False, help="[OPTIONAL] to prune features, give a minimum frequency threshold")
parser.add_argument('-s', action='store', required=False, help="[OPTIONAL] to select features based on their infogain, specify the number of features to select") 
#parser.add_argument('-k', action='store', required=False, nargs='+', help="[KNN] for knn specify value(s) of k")
#parser.add_argument('-b', action='store_true', required=False, help="[BASELINE] choose to set the baseline to dummy")
parser.add_argument('--tl', action='store_true', required=False, help="[OPTIONAL] set \'tl\' in order to have second stage or hidden timelabel classification")
parser.add_argument('--parralel', action='store_true', required=False, help="choose whether distinct train and test sets are ran in parrallel")

args=parser.parse_args() 
instance_file=codecs.open(args.i,"r","utf-8")
instances=instance_file.readlines()
instance_file.close()
validation=args.v
classifier=args.c
arguments=args.a
if args.vocab:
    vocabulary_read=codecs.open(args.vocab,"r","utf-8")
    vocabulary=list(vocabulary_read.readlines())
    vocabulary_read.close()
else:
    vocabulary=False
classifier_args=[classifier,arguments,args.p,args.s,args.tl]

def classify(traininglines,testlines,directory=False):
    cl=Classifier(traininglines,testlines,directory,vocabulary)
    cl.classify(classifier_args)
    
    #if algorithm=="lcs":
    #    cl_dir=args.d[0]
    #    file_dir=args.d[1]
    #    cl.perform_lcs(cl_dir,file_dir,args.p,args.s,args.tl)
        
    #elif algorithm=="knn":
    #    cl.perform_knn(args.k,args.p,args.s,args.tl)
    
    #elif algorithm=="ibt":
    #    cl.informed_baseline_date(args.b)

if validation=="test":
    test_instances=codecs.open(args.t,"r","utf-8")
    classify(instances,test_instances.readlines())
    test_instance.close()

elif validation=="looe":
    params=args.l
    meta=codecs.open(params[1],"r","utf-8")
    metaread=meta.readlines()
    event_column=int(params[2])
    event_train_test=defaultdict(list)
    event_bounds=[]
    event=""
    for n,instance in enumerate(metaread):
        tokens=instance.split("\t")
        instance_event=tokens[event_column]
        if instance_event != event:
            event_bounds.append((instance_event,n))
            event=instance_event
    for i,event_bound in enumerate(event_bounds):
        event=event_bound[0]
        start=event_bound[1]
        if i==len(event_bounds)-1:
            test=[]
            for i,instance in enumerate(instances[start:]):
                test.append([instances[start+i],metaread[start+i]])
            training=[]
            for i,instance in enumerate(instances[:start]):
                training.append([instances[i],metaread[i]])
        else:
            end=eventbound[i+1][1]
            test=[]
            for i,instance in enumerate(instances[start:end]):
                test.append([instances[start+i],metaread[start+i]])
            training=[]
            for i,instance in enumerate(instances):
                training.append([instances[i],metaread[i]])
            del training[start:end]
        event_train_test[event]=[training,test]
        
    if params[0]=="regular":
        for event in event_train_test.keys():
            training=event_train_test[event][0]
            test=event_train_test[event][1]
            if re.search(" ",event):
                event="_".join(event.split(" "))
            print event
            d="/".join(args.i.split(".txt")[0].split("/")[:-1]) + "/" + args.a + "/" + event + "/all_to_one/"
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
    
    else:
        domain_events=codecs.open(params[3],"r","utf-8")
        domain_event_hash=defaultdict(list)
        for line in domain_events.readlines():
            tokens=line.strip().split("\t")
            domain_event_hash[tokens[0]].append(tokens[1])
        domain_events.close()

        if params[0]=="outer_domain":
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
                        
        elif params[0]=="inner_domain":
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

