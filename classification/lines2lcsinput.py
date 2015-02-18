
import sys
import codecs
import re

infile = codecs.open(sys.argv[1],"r","utf-8")
outfile = codecs.open(sys.argv[2],"w","utf-8")
filesdir = sys.argv[3]

for i,line in enumerate(infile.readlines()):
    tokens = line.strip().split()
    for j,token in enumerate(tokens):
        if token[0] == "@":
            tokens[j] = "USER"
        if re.search(r"^http",token):
            tokens[j] == "URL"
    tokens_n = ["<s>"] + tokens + ["<s>"]
    ngrams = tokens + ["_".join(x) for x in zip(tokens_n, tokens_n[1:])] + ["_".join(x) for x in zip(tokens_n, tokens_n[1:], tokens_n[2:])]
    of = codecs.open(filesdir + str(i) + ".txt","w","utf-8")
    of.write("\n".join(ngrams))
    of.close()
    outfile.write(str(i) + ".txt sarcasme\n")

outfile.close()
