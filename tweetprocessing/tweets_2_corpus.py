
import sys
import gzip
import codecs

infile = codecs.open(sys.argv[1],"r","utf-8")
outfile = codecs.open(sys.argv[2],"w","utf-8")
textcol = int(sys.argv[3])

for line in infile.readlines():
    outfile.write(line.strip().split("\t")[textcol] + "\n")

infile.close()
outfile.close()