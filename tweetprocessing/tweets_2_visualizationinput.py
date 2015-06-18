#!/usr/bin/env 

from collections import defaultdict
import sys
import re
import csv

user_year_tweets = defaultdict(list)
user_year_mentions = defaultdict(list)

#read in tweets
infile = sys.argv[1]
lines
try:
    with open(infile, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        for line in csv_reader:
            lines.append(line)
except:
    csvfile = open(infile, 'r')
    csv_reader = csv.reader(line.replace('\0','') for line in csvfile.readlines())       
    for line in csv_reader:
        lines.append(line)

#for each tweet fill in dictionaries
field_indices = ['id', 'created', 'text', 'rtcount', 'favcount', 'user', 'mentions']
field_index = dict(zip(field_indices, range(len(field_indices))))
find_mentions = re.compile('@\w')
find_rt = re.compile('^RT')
date_time1 = re.compile(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d+) (\d{2}:\d{2}:\d{2}) \+\d+ (\d{4})")

for tweet in lines:
    fields = tweet.split('\t')
    tid = fields[field_index['id']]
    created = fields[field_index['created']]
    if date_time.search(created):
        year = date_time.search(created).groups()[-1]
    else:
        year = created[:4]
    print(tid, created, year)
    
    #user = fields[userfield]
    #text = fields[textfield]
    
    #filter 
    #mentions = find_mentions.findall(text)
    #user_tweets.append(text)








#for each dictionary key, make user fields





#sort user fields



#write to csv
