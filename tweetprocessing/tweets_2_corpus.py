
import sys
import gzip
import codecs

infile = codecs.open(sys.argv[1],"r","utf-8")
outfile = codecs.open(sys.argv[2],"w","utf-8")
textcol = int(sys.argv[3])
dutchfilter = int(sys.argv[4])

for line in infile.readlines():
    if not dutchfilter or (dutchfilter and line.strip().split("\t")[0] == "dutch"):
        outfile.write(line.strip().split("\t")[textcol] + "\n")

infile.close()
outfile.close()
