
import sys
import codecs

import lineconverter 

notfile = codecs.open(sys.argv[1],"r","utf-8")
num_sample = int(sys.argv[2])
outfile = codecs.open(sys.argv[3],"w","utf-8")
infiles = codecs.open(sys.argv[4:],"r","utf-8")

ids = []
#obtain ids
for line in notfile.readlines():
    ids.append(line.split("\t")[1])
notfile.close()

for infile in infiles:
    print infile
    good_sample_ids = []
    good_sample = []
    lineconvert = lineconverter.Lineconverter(infile.readlines())
    size = len(lineconvert.lines) - num_sample
    while len(good_sample) < size:
        sample = lineconvert.sample(size,return_sample=True)
        for entry in sample:
            print entry
            if (entry.split("\t")[1] not in good_sample) and (entry.split("\t")[1] not in ids):
                print "yes",entry.split("\t")[1]
                good_sample.append(entry)
                good_sample_ids.append(entry.split("\t")[1])
