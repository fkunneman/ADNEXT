#!/usr/bin/env python

import argparse
from classifier import Classifier
from collections import defaultdict
import codecs
import itertools

"""

"""
parser=argparse.ArgumentParser(description="")
parser.add_argument('-i', action='store', nargs='+', required=True, help="the files with tweets per event")
parser.add_argument('-d', action='store', help="the directory in which to write classification files")
parser.add_argument('-c', action='store', required=True, choices=["svm","lcs","knn","ibt","dist","random","majority"], help="the classifier")
parser.add_argument('-p', action='store', required=False, type=int, help="[OPTIONAL] to prune features, give a minimum frequency threshold")
parser.add_argument('-s', action='store', required=False, type=int, help="[OPTIONAL] to select features based on their infogain, specify the number of features to select") 
parser.add_argument('-f', action='store', required=False, type=int, help="[OPTIONAL] to select features based on frequency, specify the top n features in terms of frequency.")
parser.add_argument('--depth', action='store', default=1, type=int, help="[OPTIONAL] specify the depth of file characterizations (default = 1)")
parser.add_argument('--parralel', action='store_true', required=False, help="choose whether distinct train and test sets are ran in parrallel")

args=parser.parse_args() 

if len(args.i) <= 1:
    print "not enough event files, exiting program..."
    exit()

event_instances = defaultdict(list)
for ef in args.i:
    instance_file=codecs.open(ef,"r","utf-8")
    instances_raw=instance_file.readlines()
    instance_file.close()
    depth = args.depth * -1
    event = "/".join(ef.split("/")[depth:])
    for instance in instances_raw:    
        values = instance.strip().split("\t")
        event_instances[event].append({"features":(values[-1].split(" ")),"label":values[1],"meta":values[:-1]})

events = event_instances.keys()
for i,event in enumerate(events):
    try:
        train_events = events[:i] + events[i+1:]
    except IndexError:
        train_events = events[:i]
    train = list(itertools.chain(event_instances[x] for x in train_events))
    test = event_instances[event]
    cl = classifier.Classifier(train,test)
    cl.perform_svm(args.f)

# elif validation=="looe":
#     print "generating train-test"
#     meta_parameters = args.m
#     meta=codecs.open(meta_parameters[0],"r","utf-8")
#     metaread=meta.readlines()
#     event_column=int(meta_parameters[1])
#     event_train_test=defaultdict(lambda : defaultdict(list))
#     event_instances = defaultdict(list)
#     event=""
#     meta=[]
#     eventcount = 0
#     for i,record in enumerate(metaread):
#         tokens=instance.split("\t")
#         instance_event=tokens[event_column]
#         if instance_event != event:
#             eventcount = 0
#             if not event == "":
#                 event_train_test[event]["test"] = event_instances
#                 event_train_test[event]["meta"] = meta
#             event=instance_event
#             event_instances = []
#             meta = []
#             test = []
#         eventcount += 1 
#         meta.append(record)
#         test.append(instances[i])

#     if classifier == "ibt":
#         d="/".join(meta_parameters[0].split("/")[:-1]) + "/" + "baseline/"
#         os.system("mkdir " + d)
#         for event in event_train_test.keys():
#             # print event
#             event_write = event
#             if re.search(" ",event_write):
#                 event_write="_".join(event_write.split(" "))
#             d_event = d + event_write + "/"
#             os.system("mkdir " + d_event)
#             meta = event_train_test[event]["meta"]
#             informed_baseline_time.ibt(meta,d_event,arguments)

#     else:
#         parameters = args.l
#         for i in range(len(metaread)):
#             meta_values = metaread[i].strip().split("\t")
#             instances[i]["meta"] = meta_values
#         for i,event_bound in enumerate(event_bounds):
#             event=event_bound[0]
#             start=event_bound[1]
#             if i==len(event_bounds)-1:
#                 test = instances[start:]
#                 training = instances[:start]
#             else:
#                 end=event_bounds[i+1][1]
#                 test = instances[start+i]
#                 training = list(instances)
#                 del training[start:end]
#             event_train_test[event]["training"] = training
#             event_train_test[event]["test"] = test
            
#         if parameters[0]=="regular":
#             #events_done = ["utrfey_s11","ajaaz_f11","ajautr_f12","psvutr_f11","utraz_s11","ajaaz_f12","tweaja_s12","utraz_s12","ajafey_s11","azpsv_f11","psvfey_f12","twefey_f12","utrpsv_f12","ajapsv_s12","feypsv_f11","psvtwe_f12","utraja_f11"]
#             print "classification"
#             for event in event_train_test.keys():
#                 # if not event in events_done:
#                 print event
#                 # if event == "azfey_f11":
#                 #     print event
#                 event_write = event
#                 if re.search(" ",event_write):
#                     event_write="_".join(event_write.split(" "))
#                 d="/".join(args.i.split(".txt")[0].split("/")[:-1]) + "/" + event_write + "/all_to_one/"
#                 print d
#                 if not os.path.exists(d):
#                     if not os.path.exists("/".join(d.split("/")[:-1])):
#                         if not os.path.exists("/".join(d.split("/")[:-2])):
#                             print "mkdir " + "/".join(d.split("/")[:-2])
#                             os.system("mkdir " + "/".join(d.split("/")[:-2]))
#                         print "mkdir " + "/".join(d.split("/")[:-1])
#                         os.system("mkdir " + "/".join(d.split("/")[:-1]))
#                     os.system("mkdir " + d)
#                 if args.parralel:
#                     # print event
#                     # print len(event_train_test[event]["meta"])
#                     #try:
#                     p=multiprocessing.Process(target=classify,args=[event_train_test[event],d])
#                     p.start()
#                     #except OSError:
#                     #    classify(event_train_test[event],d)
#                 else:
#                     classify(event_train_test[event],d)
