
import sys
import gzip
import codecs

infile = gzip.open(sys.argv[1],"rb")
outfile = codecs.open(sys.argv[2],"w","utf-8")
textcol = int(sys.argv[3])

for line in infile.readlines():
    outfile.write(line.strip().split("\t")[textcol] + "\n")

infile.close()
outfile.close()