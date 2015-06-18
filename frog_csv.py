#!/usr/bin/env 

import csv
import utils
import sys
import os
import codecs

infile = sys.argv[1]
tmpdir = sys.argv[2]
outfile = sys.argv[3]
lines = int(sys.argv[4])
input = sys.argv[5] #netlog,csi,genie,blogger

def frog_doc(docstring,tmpdir):
    prefrog = tmpdir + "docstring.txt"
    postfrog = tmpdir + "docstring_frogged.txt"
    prefrogfile = codecs.open(prefrog,"w","utf-8")
    prefrogfile.write(docstring)
    prefrogfile.close()
    os.system("frog -d0 --skip pn -t " + prefrog + " -c /home/kunneman/etc/frog/frog.cfg -o " + postfrog)
    postfrogfile = codecs.open(postfrog,"r","utf-8")
    frogstring = postfrogfile.read()
    postfrogfile.close()
    return frogstring

def frogged_docs(texts,tmpdir):
    frogged = []
    for doc in texts:
        frogged.append(frog_doc(doc,tmpdir))
    return frogged

config = "frog.cfg"
if input == "blogger":
    config = "frog-twitter.cfg"
    dataset = utils.load_data_pattern(filename=infile,max_n = lines)
    texts = dataset["texts"]
    dataset["frogged"] = frogged_docs(texts,tmpdir)
    fields = "user_id age gender loc_country loc_region loc_city education pers_big5 pers_mbti texts frogged".split()
    rows = []
    for i in range(len(dataset["texts"])):
        rows.append([dataset[f][i] for f in fields])

elif input == "genie":
    rows = []
    data_initial = open(infile,'r')
    reader = csv.reader((line.replace('\0','') for line in data_initial),delimiter=',')
    for row in reader:
        rows.append(row)
    froggedrows = frogged_docs([l[-1] for l in rows[:lines]],tmpdir)
    for i,r in enumerate(froggedrows):
        rows[i].append(r)

else:
    dataset = utils.load_data_pattern(filename=infile,max_n = lines)
    texts = dataset["texts"]
    dataset["frogged"] = frogged_docs(texts,tmpdir)
    fields = "user_id age gender loc_country loc_region loc_city education pers_big5 pers_mbti texts frogged".split()
    rows = []
    for i in range(len(dataset["texts"])):
        rows.append([dataset[f][i] for f in fields])

with open(outfile, 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for row in rows:
        writer.writerow([s.encode("utf-8") for s in row])
