#!/usr/bin/env 

from __future__ import print_function, unicode_literals, division, absolute_import
import sys
import math
import colibricore

tmp = sys.argv[1]
outdir = sys.argv[2]
infiles = sys.argv[3:]

"""
script to read in x files (where x is the number of categories) with tokenized sentences, and 
return lists of words ranked by pmi per category
"""

classfile = tmp + "_pmi.colibri.cls"
textfile = tmp + "_pmi.txt"
corpusfile = tmp + "_pmi.colibri.dat"
nlines_total = 0

print("Writing all texts to temporary file" ,file=sys.stderr)
with open(textfile,'w',encoding='utf-8') as g:
    for i, infile in enumerate(infiles):
        with open(infile,encoding = "utf-8") as f:
            for l in f.readlines():
                g.write(l)
                nlines_total += 1

print("Building class encoder",file=sys.stderr)
classencoder = colibricore.ClassEncoder()
classencoder.build(textfile)
classencoder.save(classfile)

print("Encoding corpus data",file=sys.stderr)
classencoder.encodefile(textfile, corpusfile)

print("Loading class decoder",file=sys.stderr)
classdecoder = colibricore.ClassDecoder(classfile)

print("Counting per class",file=sys.stderr)
classmodels = []

for i, infile in enumerate(infiles):
    with open(infile,encoding = "utf-8") as f:
        classmodel = colibricore.UnindexedPatternModel()
        cls = infile.split("/")[-1][:-4]
        lines = f.readlines()
        clprob = len(lines)/nlines_total
        for l in lines:
            words = l.strip().split(" ")
            for i in range(3):
                if i == 0:
                    ngrams = zip(c)
                elif i == 1:
                    ngrams = zip(c, c[1:])
                elif i == 2:
                    ngrams = zip(c, c[1:], c[2:])
                for ngram in ngrams:
                    pattern = classencoder.buildpattern(" ".join(ngram))
                    classmodel.add(pattern) #(will count +1 if already exists)
    classmodels.append((cls,clprob,classmodel))

print("Calculating statistics",file=sys.stderr)
options = colibricore.PatternModelOptions(mintokens=1, maxlength=3)
for classmodel in classmodels:
    pattern_pmi = []
    class_probability = classmodel[1]
    patternmodel = colibricore.UnindexedPatternModel()
    patternmodel.train(corpusfile, options, classmodel[2]) #(last argument constrains the training to patterns only occuring in that model, i.e the intersectino of these models, saves heaps of space)
    for ngram, count in patternmodel.items():
        class_cooc = classmodel[2][ngram]
        pmi = math.log(class_cooc/((count/nlines_total) * class_probability))
        pattern_pmi.append((ngram.tostring(classdecoder),pmi))
    pattern_pmi_sorted = sorted(pattern_pmi,key = lambda k : k[1],reverse = True)
    outfile = open(outdir + classmodel[0] + "_pmi.txt","w",encoding="utf-8")
    for pp in pattern_pmi_sorted:
        outfile.write(pp + "\t" + str(round(pp[1],2)))
    outfile.close()
