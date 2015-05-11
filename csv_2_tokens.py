#!/usr/bin/env 

import csv
import sys
import frog

csv.field_size_limit(sys.maxsize)
with open(sys.argv[1], 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        print(row)

# infile = open(sys.argv[1],encoding="utf-8")

# fo = frog.FrogOptions(threads=20)
# frogger = frog.Frog(fo,"/vol/customopt/uvt-ru/etc/frog/frog-twitter.cfg")



# for i,t in enumerate(self.instances):
#     print("tokenizing",i,"of",num_instances,"instances")
#     tokens = []
#     stems = []
#     poss = []
#     data = frogger.process(t.text)
#     for token in data:
#         if (punct and not token["pos"] == "LET()") or \
#             not punct:
#             tokens.append(token["text"])
#             poss.append(token["pos"])
#             stems.append(token["lemma"])
#     t.add_stem(stems)
#     t.add_pos(poss)
#     t.text = " ".join(tokens)

