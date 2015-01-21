
import sys
import os
import codecs
import re

infile = sys.argv[1]
#outdir = sys.argv[2]

filename = infile.split("/")[-1]
dct = filename[:4] + "-" + filename[4:6] + "-" + filename[6:8]

print("dct",dct,"extracting columns")
infile_read = codecs.open(infile,"r","utf-8")
for i,line in enumerate(infile_read.readlines()):
    tokens = line.strip().split("\t")
    outstr = str(i) + "_proper_" + filename
    outfile = codecs.open(outstr,"w","utf-8")
    if len(tokens) >= 7:
        outfile.write("\t".join([tokens[1],tokens[7]]) + "\n")
    outfile.close()
    outstr2 = str(i) + "cleaned_" + filename
    os.system("python /home/fkunneman/ADNEXT/convert_lines.py -i " + outstr + " -o " + outstr2 + " -a delete -c 1 -s RT")
    print(outstr2,"tagging tweets")
    os.system("java -jar /home/fkunneman/local/bin/heideltime-standalone/de.unihd.dbs.heideltime.standalone.jar " + outstr2 + " -l DUTCH -t NEWS -pos treetagger -dct " + dct + " > " + str(i) + "_tagged_" + filename)
    tagged_file = codecs.open(str(i) + "_tagged_" + filename)
    if re.search(r"xml version=",tagged_file.read()):
        os.system("rm " + str(i) + "*")
    else:
        print("bug found at line",str(i))
        quit()
infile_read.close()

#quit()

#os.system("campyon -k 2,8 -C# " + infile + " > " + filename)
#print(filename,"cleaning tweets")


# os.system("java -jar /home/fkunneman/local/bin/heideltime-standalone/de.unihd.dbs.heideltime.standalone.jar cleaned_" + filename + " -l DUTCH -t NEWS -pos treetagger -vv -dct " + dct + " > tagged_" + filename)
# print("done. moving tweets to",outdir)
# os.system("mv tagged_" + filename + " " + outdir)
# os.system("rm *" + filename + "*")
