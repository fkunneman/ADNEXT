#!/usr/bin/env python

import argparse
import os
import codecs
import multiprocessing

import gen_functions

"""
Script to convert a file with tweetfeatures to the format needed for LCS Balanced Winnow classification.
"""
parser = argparse.ArgumentParser(description = "Script to convert a file with tweet features to the format needed for lcs classification.")
parser.add_argument('-i', action = 'store', required = True, help = "the input file")  
parser.add_argument('-d', action = 'store', required = True, help = "the files directory")
parser.add_argument('-w', action = 'store', required = True, help = "the directory in which to write \'parts.txt\' and \'meta.txt\'")
parser.add_argument('-l', action = 'store', required = True, help = "the label of the tweet set")

args = parser.parse_args() 

outparts = codecs.open(args.w + "parts.txt","w","utf-8")
outmeta = codecs.open(args.w + "meta.txt","w","utf-8")
infile = codecs.open(args.i,"r","utf-8")
instances = infile.readlines()
infile.close()

def lcswriter(instances,chunkindex,partsqueue=False,metaqueue=False):
    print "starting chunk",chunkindex
    i = 0
    while i < (len(instances)):
        filesdir = args.d + args.l + str(i)
        os.system("mkdir " + filesdir)
        file_index,dirsize=0,25000
        if i+dirsize < len(instances):
            subtweets=instances[i:i+d]
        else: 
            subtweets=instances[i:]
        for tweet in subtweets:
            #make filename and write contents to it
            zeros=5-len(str(file_index))
            j=0
            file_name=str(file_index) + ".txt"
            while j < zeros:
                file_name="0" + file_name
                j += 1
            outfile=codecs.open(filesdir + "/" + file_name,"w","utf-8")
            tokens = tweet.strip().split("\t")
            features = tokens[-1].split(" ")
            label = tokens[1]
            outfile.write("\n".join(features))
            outfile.close()
            #queue file name and label to the partsfile
            instanceline = file_name + " " + label + "\n"
            partsqueue.put(instanceline)
            #queue file name and meta to metafile
            metaline = file_name + "\t" + "\t".join(tokens) + "\n"
            metaqueue.put(metaline)
            file_index += 1
        i += dirsize
    print "chunk",chunkindex,"done"

q = multiprocessing.Queue()
r = multiprocessing.Queue()
tweet_chunks = gen_functions.make_chunks(instances)
for i,c in enumerate(tweet_chunks):
    p=multiprocessing.Process(target=lcswriter,args=[c,i,q,r])
    p.start()

qwrites=[]
rwrites=[]
num_instances=len(instances)

while len(qwrites) < num_instances:
    l=q.get()
    qwrites.append(l)
    outparts.write(l)
while len(rwrites) < num_instances:
    l=r.get()
    rwrites.append(l)
    outmeta.write(l)

outparts.close()
outmeta.close()
