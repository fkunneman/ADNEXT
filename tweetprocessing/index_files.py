
import sys
import lineconverter
import codecs
import gzip

start_index = int(sys.argv[1])
outdir = sys.argv[2]
infiles = sys.argv[3:]

for f in infiles:
    print f
    print outdir + "/".join(f.split("/")[-2:])
    if f[-2:] == "gz":
        infile = gzip.open(f,"rb")
        outfile = gzip.open(outdir + "/".join(f.split("/")[-2:]), 'wb')
    else:
        infile = codecs.open(f,"r","utf-8")
        outfile = codecs.open(outdir + "/".join(f.split("/")[-2:]),"w","utf-8")
    lines = infile.readlines()
    infile.close()
    lineconvert = lineconverter.Lineconverter(lines," ")
    lineconvert.add_id(start_id = start_index)
    start_index += len(lines)
    for line in lineconvert.lines:
        outfile.write("\t".join(line.split(" ")[:5]) + "\t" + " ".join(line.split(" ")[5:]))
    outfile.close()
