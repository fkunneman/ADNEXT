#! /usr/bin/env python

from __future__ import division
import argparse
import codecs
from collections import defaultdict
import lineconverter
from gen_functions import has_endhashtag

parser = argparse.ArgumentParser(description = "")
parser.add_argument('-i', action = 'store', required = True, help = "the input file")  
parser.add_argument('-lc', action = 'store', required = True, help = "the column in the input file with the label")
parser.add_argument('-tc', action = 'store', required = True, help = "the column in the input file with the text")
parser.add_argument('-s', action = 'store', required = True, help = "the size of the sample")
parser.add_argument('-o', action = 'store', required = True, help = "the output file")
args = parser.parse_args()

infile = codecs.open(args.i,"r","utf-8")
lines = infile.readlines()
infile.close()
outfile = codecs.open(args.o,"w","utf-8")

label_hash = defaultdict(list)
label_column = int(args.lc)
text_column = int(args.tc)
for line in lines:
    tokens = line.split("\t")
    #print tokens
    label = tokens[label_column]
    text = tokens[text_column]
    wordsequence = text.strip().split(" ")
    if has_endhashtag(wordsequence,["#" + label]):
        label_hash[label].append(text)

sample_size = int(args.s)
num_samples = 0
for i,label in enumerate(label_hash.keys()):
    label_lines = label_hash[label]
    if i == len(label_hash.keys())-1:
        size = sample_size - num_samples
    else:
        percent = len(label_lines) / len(lines)
        size = int(round(percent*sample_size,0))
        num_samples += size
    lineconvert = lineconverter.Lineconverter(label_lines,"\t")
    extracted_lines = lineconvert.extract_sample(size)
    for line in extracted_lines:
        outfile.write(line + "\n")

outfile.close()
