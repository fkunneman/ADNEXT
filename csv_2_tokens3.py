#!/usr/bin/env 

import csv
import sys
import frog
import ucto
import re

fo = frog.FrogOptions(threads=25)
#frogger = frog.Frog(fo,"/vol/customopt/uvt-ru/etc/frog/frog-twitter.cfg")
frogger = frog.Frog(fo,"/home/fkunneman/netlogconf/frog-netlog.cfg")
csv.field_size_limit(sys.maxsize)

#ucto_settingsfile = "/home/fkunneman/netlogconf/tokconfig-nl-netlog"
#tokenizer = ucto.Tokenizer(ucto_settingsfile)

filename = sys.argv[1][:-4]

lines = []
metalist = []
tokenslist = []
stemslist = []
poslist = []

url = re.compile(r"(\[url=http[^\]]+\][^\[]+\[\/url\])")
photo = re.compile(r"(\[photo\][^\]]+\[\/photo\])")
video = re.compile(r"(\[video\][^\[\]]+\[\/video\])")

print("reading in file")
with open(sys.argv[1], 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        lines.append(row)

print("frogging")
lines = lines[:30]
le = len(lines)
for i,line in enumerate(lines):
    print("line",i,"of",le)
    #tokenizer = ucto.Tokenizer(ucto_settingsfile)
    #tokenizer.process(line[-1])
    #print(line)
    #for x in tokenizer:
    #    print(x.text,x.role,x.type())   
    tokens = []
    stems = []
    pos = []
    metalist.append(line[:-1])
    txt = line[-1]
    cats = txt.split("\n")
    new_cats = []
    for text in cats:
        #print(text)
        if re.search(url,text): #replace with dummy
            #print("YES",text)
            l = ""
            regexPattern = '|'.join(map(re.escape, url.findall(text)))
            urls = ', '.join(url.findall(text))
            output = [re.split(regexPattern, text),urls]
            for x in output[0]:
                if len(x) > 0:
                    l = l + x + " URL "
            text = l
            #print(text)
            #print("END",text)
        if re.search(photo,text): #replace with dummy
            #print("YES",text)
            l = ""
            regexPattern = '|'.join(map(re.escape, photo.findall(text)))
            photos = ', '.join(photo.findall(text))
            output = [re.split(regexPattern, text),photos]
            for x in output[0]:
                l = l + x + " PHOTO "
            text = l
            #print("END",text)
        if re.search(video,text): #replace with dummy
            #print("YES",text)
            l = ""
            regexPattern = '|'.join(map(re.escape, video.findall(text)))
            videos = ', '.join(video.findall(text))
            output = [re.split(regexPattern, text),videos]
            for x in output[0]:
                l = l + x + " VIDEO "
            text = l
            #print("END",text)
        new_cats.append(text)
    txt = "\n".join(new_cats)
    data = frogger.process(txt)
    for token in data:
        tokens.append(token["text"])
        pos.append(token["pos"])
        stems.append(token["lemma"])
    tokenslist.append(tokens)
    poslist.append(pos)
    stemslist.append(stems)

with open(filename + "_tokenized.csv", 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for i,tokens in enumerate(tokenslist):
        writer.writerow(metalist[i] + [" ".join(tokens)])

with open(filename + "_postags.csv", 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for i,pos in enumerate(poslist):
        writer.writerow(metalist[i] + [" ".join(pos)])

with open(filename + "_lemmatized.csv", 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for i,stems in enumerate(stemslist):
        writer.writerow(metalist[i] + [" ".join(stems)])

#     t.add_stem(stems)
#     t.add_pos(poss)
#     t.text = " ".join(tokens)




# infile = open(sys.argv[1],encoding="utf-8")