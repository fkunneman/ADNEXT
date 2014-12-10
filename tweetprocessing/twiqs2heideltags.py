
import sys
import os
import codecs
import re

infile = sys.argv[1]
outdir = sys.argv[2]

filename = infile.split("/")[-1]
dct = filename[:4] + "-" + filename[4:6] + "-" + filename[6:8]

print("dct",dct,"extracting columns")
outfile = codecs.open("proper_" + filename,"w","utf-8")
infile_read = codecs.open(infile,"r","utf-8")
for line in infile_read.readlines():
    tokens = line.strip().split("\t")
    if len(tokens) >= 7:
	outfile.write("\t".join([tokens[1],tokens[7]]) + "\n")
outfile.close()
infile_read.close()

#quit()

#os.system("campyon -k 2,8 -C# " + infile + " > " + filename)
#print(filename,"cleaning tweets")
os.system("python /home/fkunneman/ADNEXT/convert_lines.py -i proper_" + filename + " -o cleaned_" + filename + " -a delete -c 1 -s RT")
print("cleaned_",filename,"tagging tweets")
os.system("java -jar /home/fkunneman/local/bin/heideltime-standalone/de.unihd.dbs.heideltime.standalone.jar cleaned_" + filename + " -l DUTCH -t NEWS -pos treetagger -vv -dct " + dct + " > tagged_" + filename)
print("done. moving tweets to",outdir)
os.system("mv tagged_" + filename + " " + outdir)
os.system("rm *" + filename + "*")
