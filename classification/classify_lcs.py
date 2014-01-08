#!/usr/bin/env python

import argparse
import os
import codecs

"""
Script to perform lcs classification with chosen parameters. The used data should be in the right format.
"""
parser = argparse.ArgumentParser(description = "Script to perform lcs classification with chosen parameters. The used data should be in the right format.")
parser.add_argument('-p', action = 'store', required = True, help = "partsfile with either all instances or training instances")
parser.add_argument('-t', action = 'store', required = False, help = "partsfile for test data (no testfile means ten-fold cross-validation is performed)")
parser.add_argument('-d', action = 'store', required = True, help = "the directory in which classification is performed")
parser.add_argument('-c', action = 'store', required = True, help = "give the name of a standard config file")
parser.add_argument('-f', action = 'store', required = True, help = "the directory with feature files")
parser.add_argument('--learning_curve', action = 'store_true', help = "choose to classify by learning curve")

args = parser.parse_args() 

expdir = "/".join(args.p.split("/")[:-1]) + "/"

#set config
config_file = codecs.open(args.config,"r","utf-8")
config = {}
config_order = []
for line in config_file.readlines():
    tokens = line.strip().split("=")
    config[tokens[0]] = tokens[1]
    config_order.append(tokens[0])
config_file.close()
files_split = args.f.split("/")
config["general.files"] = "/".join(files_split[:-1]) + "./" + files_split[-1]
config["general.data"] = args.d + "./data"
config["general.index"] = args.d + "./data/index"
#optional parametersettings

#write configfile
config_out = codecs.open(args.d + "lcs3.conf","w","utf-8")
for key in config_order:
    config_out.write(key + "=" + config[key] + "\n")

#prepare train and test
if args.t:
    os.system("cp " + args.p + " " + args.d)
    os.system("cp " + args.t + " " + args.d)

#classify
os.chdir(args.d)
os.system("lcs --verbose ")
os.system("mv * " + expdir)
