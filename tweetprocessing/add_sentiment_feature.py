
import sys
import codecs
from pattern.nl import sentiment

featfile = codecs.open(sys.argv[2],"r","utf-8")
feats = featfile.readlines()
featfile.close()
feats.extend(["polarity\n","subjectivity\n"])
featout = codecs.open(sys.argv[2],"w","utf-8")
for feat in feats:
    featout.write(feat)
featout.close()

infile = codecs.open(sys.argv[1],"r","utf-8")
lines = infile.readlines()
infile.close()
outfile = codecs.open(sys.argv[1],"w","utf-8")
for line in lines:
    tokens = line.split("\t")
    text = tokens[5]
    print(text)
    senti = sentiment(text)
    line = line.strip() + " " + str(senti[0]) + " " + str(senti[1]) + "\n"
    outfile.write(line)
outfile.close()