#! /usr/bin/env python

from pattern.nl import parse, pprint, sentiment
import argparse
import numpy as np
from collections import defaultdict
import codecs
import re

parser = argparse.ArgumentParser(description = "")

parser.add_argument('-i', action='store', required = True, help = 'File with tweets')

args = parser.parse_args()

party_sentiment = defaultdict(lambda : defaultdict(lambda : defaultdict(list)))

infile = codecs.open(args.i,"r","utf-8")
for line in infile.readlines():
    tokens = line.strip().split("\t")
    try:
        day = tokens[0]
        party = tokens[1]
        text = tokens[2]
        senti = sentiment(text)
        party_sentiment[party][day]["reg"].append(senti)
        if not re.search(' rt ',text,re.IGNORECASE) and not re.search('^rt',text,re.IGNORECASE):
            # print text
            party_sentiment[party][day]["rt"].append(senti)            

    except IndexError:
        continue

for party in party_sentiment.keys():
    for day in sorted(party_sentiment[party].keys()):
        sentiments = party_sentiment[party][day]["reg"]
        sentiments_filt = party_sentiment[party][day]["rt"]
        # print len(sentiments),len(sentiments_filt)
        # print sentiments
        print party, day, round(sum([ float(i[0]) for i in sentiments ])/float(len(sentiments)),2), round(np.std(sentiments),2), round(sum([ float(i[0]) for i in sentiments_filt ])/float(len(sentiments_filt)),2), round(np.std(sentiments_filt),2)