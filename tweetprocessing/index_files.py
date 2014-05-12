
import sys
import lineconverter
import codecs
import gzip

start_index = int(sys.argv[1])
outdir = sys.argv[2]
infiles = sys.argv[3:]

for f in infiles:
    print f
    print outdir + f.split("/")[-2:]
    quit()
    if f[-2:] == "gz":
        infile = gzip.open(args.i,"rb")
        outfile = gzip.open(outdir + f.split("/")[-2:], 'wb')
    else:
        infile = codecs.open(f,"r","utf-8")
        outfile = codecs.open(outdir + f.split("/")[-2:],"w","utf-8")
    lines = infile.readlines()
    infile.close()
    lineconvert = lineconverter.Lineconverter(lines,"\t")
    lineconvert.add_id(start_id = start_index)
    start_index += len(lines)
    for line in lineconvert.lines:
        outfile.write(line + "\n")
    outfile.close()

