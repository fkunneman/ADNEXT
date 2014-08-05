#!/usr/bin/env python

import argparse
from collections import defaultdict
import re
import codecs

import ucto

parser = argparse.ArgumentParser(description = "")

parser.add_argument('-t', action = 'store', nargs = '+', required = True, help = "the label dirs") #train tweets
parser.add_argument('-f', action='store', nargs='+',required=False, help = "good id file") #test tweets
# parser.add_argument('-c', action='store', nargs = '+', required=True, help = "the classification files") #test tweets
# parser.add_argument('-m', action='store', nargs = '+', required=True, help = "the meta files") #for emotiona category tweet ids
# parser.add_argument('-l', action='store', nargs = '+', required=True, help = "the list of emotion labels")
parser.add_argument('--id', action='store_true', help = "indicate if the id in background meta-files is correct")
parser.add_argument('-b', action='store', required=True, help = "the file with background meta") #for background tweet ids
parser.add_argument('-w', action='store', required=True, help = "dir to write results to")
parser.add_argument('--ld', action='store',required=False, help = "general expdir")
args = parser.parse_args()

# if not (len(args.t) == len(args.c) and len(args.c) == len(args.m)):
#     print "no equal sizes of label lists, exiting program"
#     quit()
# else:
#     print "label dicts of equal size, proceeding with program"
num_labels = len(args.t)
backgroundfile_tid = {}

if args.id:
    background_meta = codecs.open(args.b,"r","utf-8")
    for line in background_meta.readlines():
        tokens = line.strip().split("\t")
        backgroundfile_tid[tokens[0]] = tokens[1]
    background_meta.close()
    for i in range(num_labels):
        labeldir = args.t[i]
        label = labeldir.split("/")[-2]
        meta_file = open(labeldir + "meta.txt")
        for line in meta_file.readlines():
            tokens = line.strip().split("\t")
            backgroundfile_tid[tokens[0]] = tokens[1]
        meta_file.close()

else:
    #load background dict
    print "loading background dict"
    #backgroundfile_uid_time = defaultdict(lambda : {})
    user_time_text_tid = defaultdict(lambda : defaultdict(lambda : {}))
    #user_time_text_tid = defaultdict(lambda : defaultdict(lambda : defaultdict(list)))
    background_meta = codecs.open(args.b,"r","utf-8")
    ts = re.compile(r"\d{2}:\d{2}:\d{2}")
    for line in background_meta.readlines():
        tokens = line.strip().split("\t")
        if ts.search(tokens[5]):
            time = tokens[5]
        elif ts.search(tokens[4]):
            time = tokens[4]
        else:
            print "no time",tokens
            quit()
        if len(time) > 8:    
            print time
        #print tokens[1],",",time,",",tokens[-1]
        #print tokens[6]
        user_time_text_tid[tokens[1]][time][tokens[7]] = tokens[0]
    #    print tokens[6],time
        # if not time in backgroundfile_uid_time[tokens[6]].keys():
        #     backgroundfile_uid_time[tokens[6]][time] = tokens[0]
        # else:
        #     backgroundfile_uid_time[tokens[6]][time] = "double"
    background_meta.close()

    print "skimming through tweet files"
    ucto_settingsfile = "/vol/customopt/uvt-ru/etc/ucto/tokconfig-nl-twitter"
    tokenizer = ucto.Tokenizer(ucto_settingsfile)
    for f in args.f:
        print f
        tweetfile = codecs.open(f,"r","utf-8")
        for line in tweetfile.readlines():
            tokens = line.strip().split("\t")
            try:
                time = tokens[3]
            except IndexError:
                print "indexerror time 3",tokens
                #quit()
                continue
            # try:
    #        print tokens[5],time
            #try:
                #if not backgroundfile_uid_time[tokens[5]][time] == "double":
                #    filename = backgroundfile_uid_time[tokens[5]][time]
                # else:
            words = []
            text = unicode(tokens[6])
            tokenizer.process(text)
            for token in tokenizer:
                    #token = str(token).encode('utf-8')
                token = token.text
                if re.search("http://",token):
                    word = "URL"
                elif re.search(r"^@",token):
                    word = "USER"
                else:
                    word = token
                words.append(word)  
                #print " ".join(words)
                #     try:
            try:        
                filename = user_time_text_tid[tokens[1]][time][" ".join(words)]
                #print filename
                backgroundfile_tid[filename] = tokens[0]
            except KeyError:
                #print "keyerror"," ".join(words)
                #quit()
                continue
                    #print filename
            #except KeyError:
            #    continue


# tweetfile = open(args.f)
# for line in tweetfile.readlines():
#     tokens = line.strip().split("\t")
#     if len(tokens) > 5:
#         if ts.search(tokens[5]):
#             time = tokens[5]
#         else:
#             time = tokens[4]
#         try:
#             if not backgroundfile_uid_time[tokens[6]][time] == "double":
#                 filename = backgroundfile_uid_time[tokens[6]][time]
#             else:
#                 filename = user_time_text_tid[tokens[6]][time][tokens[7]]
#                 #print filename
#             backgroundfile_tid[filename] = tokens[0]
#         except:
#             continue
# tweetfile.close()


#for every label
print "running through labels"
if args.id:
    print "id"
else:
    for i in range(num_labels):
        labeldir = args.t[i]
        label = labeldir.split("/")[-2]
        train_file = open(labeldir + "train")
        test_file = open(labeldir + "test")
        meta_file = open(labeldir + "meta.txt")
        print i,"of",num_labels,",",label
        trainout = open(args.w + label + "_train.txt","w")
        testout = open(args.w + label + "_test.txt","w")
        #get trainids label from metafile
        for line in meta_file.readlines():
            trainout.write(line.split("\t")[1] + " " + label + "\n")
        meta_file.close()
        #obtain background train tweet ids
        print "obtaining background train tweet ids"
        for line in train_file.readlines():
            tokens = line.strip().split()
            if tokens[1] == "background":
                trainout.write(backgroundfile_tid[tokens[0]] + " background\n")
        train_file.close()
        trainout.close()
        #obtain background train tweet ids
        print "obtaining test tweet ids"
        for line in test_file.readlines():
            tokens = line.strip().split()
            testout.write(backgroundfile_tid[tokens[0]] + " " + tokens[1] + "\n")
        test_file.close()
        testout.close()
