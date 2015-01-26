
import sys
import codecs
from pattern.nl import sentiment

featfile = codecs.open(sys.argv[2],"r","utf-8")
feats = featfile.readlines()
featfile.close()
feats.extend(["positive sentiment\n","negative sentiment\n","subjectivity\n"])
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
    senti = sentiment(text)
    polarity = senti[0]
    if polarity < 0:
        positive = "0.0"
        negative = str(round(polarity*-1,2))
    else:
        positive = str(round(polarity,2))
        negative = "0.0"
    line = line.strip() + " " + positive + " " + negative + " " + str(round(senti[1],2)) + "\n"
    outfile.write(line)
outfile.close()