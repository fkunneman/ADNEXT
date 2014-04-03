#!/usr/bin/env python

import argparse
import os
import codecs

"""
Script to perform lcs classification with chosen parameters. 
The used data should be in the right format.
"""
parser = argparse.ArgumentParser(description = "Script to perform lcs classification with chosen \
    parameters. The used data should be in the right format.")
parser.add_argument('-p', action = 'store', required = True, 
    help = "partsfile with either all instances or training instances")
parser.add_argument('-t', action = 'store', required = False, 
    help = "partsfile for test data (no testfile means ten-fold cross-validation is performed)")
parser.add_argument('-d', action = 'store', required = True, 
    help = "the directory in which classification is performed")
parser.add_argument('-c', action = 'store', required = True, 
    help = "give the name of a standard config file")
parser.add_argument('-f', action = 'store', required = True, 
    help = "the directory with feature files")
parser.add_argument('--learning_curve', action = 'store_true', 
    help = "choose to classify by learning curve")

args = parser.parse_args() 

expdir = "/".join(args.p.split("/")[:-1]) + "/"

#set config
config_file = codecs.open(args.c,"r","utf-8")
config = {}
config_order = []
for line in config_file.readlines():
    tokens = line.strip().split("=")
    config[tokens[0]] = tokens[1]
    config_order.append(tokens[0])
config_file.close()
files_split = args.f.split("/")
filewrite = "/".join(files_split[:-2]) + "/./" + files_split[-2]
config["general.files"] = filewrite
config["general.data"] = args.d + "./data"
config["general.index"] = args.d + "./data/index"
#optional parametersettings

#write configfile
config_out = codecs.open(args.d + "lcs3.conf","w","utf-8")
for key in config_order:
    config_out.write(key + "=" + config[key] + "\n")

#prepare train and test
if args.t:
    os.system("cp " + args.p + " " + args.d + "/train")
    os.system("cp " + args.t + " " + args.d + "/test") 
    config_out = codecs.open(args.d + "lcs3.conf","w","utf-8")
    for key in config_order:
        config_out.write(key + "=" + config[key] + "\n")
    #classify
    os.chdir(args.d)
    os.system("lcs --verbose ")
    os.system("mv * " + expdir)

else:
    folds = []
    partsopen = open(args.p)
    instances = partsopen.readlines()
    partsopen.close()
    for i in [x+1 for x in range(10)]:
        ind = 1
        fold = []
        while i * ind < len(instances):
            fold.append(re.sub("\n","",instances[i*ind]))
            ind += 1
        folds.append(fold)
    for j,fold in enumerate(folds):
        #print "".join(fold)
        try:
            tr_folds = folds[:j] + folds[j+1:]
        except IndexError:
            tr_folds = folds[:j]
        trainout = open(args.d + "/train","w")
        for tr_fold in tr_folds:
            trainout.write("\n".join(tr_fold))
        testout = open(args.d + "/test","w")
        testout.write("\n".join(fold))
        config_out = codecs.open(args.d + "lcs3.conf","w","utf-8")
        for key in config_order:
            config_out.write(key + "=" + config[key] + "\n")
        expdir_fold = expdir + "fold_" + str(j)
        os.system("mkdir " + expdir_fold)
        os.chdir(args.d)
        os.system("lcs --verbose ")
        os.system("mv * " + expdir_fold)

    # size = len(sorted_instances)
    # for i in range(n):
    #     fold_dir = main_dir + "fold_" + str(i) + "/"
    #     os.system("mkdir " + fold_dir)
    #     print fold_dir
    #     train_test = defaultdict(list)
    #     train_test["training"] = list(sorted_instances)
    #     j = i
    #     offset = 0
    #     while j < size:
    #         train_test["test"].append(sorted_instances[j])
    #         #print i,j-offset,len(train_test["train"]),j,size,len(sorted_instances)
    #         del train_test["training"][j-offset]
    #         j + =  n
    #         offset + =  1
    #     train_test["meta"] = []
    #     classify(train_test,fold_dir)


