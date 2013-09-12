#! /usr/bin/env python

from pattern.nl import parse, pprint, sentiment
import argparse
import numpy as np

parser = argparse.ArgumentParser(description = "")

parser.add_argument('-i', action='store', required = True, help = 'File with tweets')

args = parser.parse_args()

party_sentiment = defaultdict(lambda : defaultdict(list))

infile = codecs.open(args.i,"r","utf-8")
for line in infile.readlines():
    tokens = line.strip().split("\t")
    day = tokens[0]
    party = tokens[1]
    text = tokens[2]
    sentiment = pattern.nl.sentiment(text)
    party_sentiment[party][day].append(sentiment)

for party in party_sentiment.keys():
    for day in sorted(party_sentiment[party].keys()):
        sentiments = party_sentiment[party][day]
        print party, day, np.mean(sentiments)
