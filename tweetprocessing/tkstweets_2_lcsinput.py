#! /usr/bin/env python

import codecs
import sys
import datetime
import re
import copy
import argparse
import os

parser = argparse.ArgumentParser(description = "Generate LCS-files and parts and an additional metafile based on files with tweets.")
parser.add_argument('-i', action='store', required = True, help = 'Inputfile with tweets, in the format [id\\tid\\tdate\\ttime\\userid\\tuser\\ttest]')  
parser.add_argument('-pr', action='store', required = True, help = 'Prefix for LCS-files (could include path, like \'bg/bg\')')
parser.add_argument('-d', action='store', required = True, help = 'Directory for the generated files to be stored in')
parser.add_argument('-p', action='store', required = True, help = 'Partsfile to write references to')
parser.add_argument('-m', action='store', required = True, help = 'File to write metainformation to')
parser.add_argument('-l', action='store', required = True, help = 'Label of the tweets')
parser.add_argument('-n', action='store_true', default = True, help = 'Decide whether ngrams are generated (default = True)')
parser.add_argument('-s', action='store', default = '0', help = 'The index at which filenumbers start (default = 0)')
parser.add_argument('-ft', action='store', required = False, help = 'A word by which tweets containing it will be filtered from the output (not required)')
parser.add_argument('-fl', action='store', required = False, help = 'In case of filtered tweets, they will be assigned a chosen label other than the standard one (not required)')
parser.add_argument('-fs', action='store', required = False, help = 'A stopword that will be removed when seen (in every ngram) (not required)')
parser.add_argument('-w', action='store', required = False, help = 'A file with words/patterns to give extra weight to a tweet')

args = parser.parse_args() 
tks_tweets_file = args.i
prefix = args.pr
filesdir = args.d
classfile = open(args.p,"a")
metafile = open(args.m,"a")
label = args.l
ngrams = args.n
index = int(args.s)
filttweet = args.ft
filttweetlabel = args.fl
filtword = args.fs
weightfile = args.w
if weightfile:
	weights = []
	for line in codecs.open(weightfile,"r","utf-8"):
		weights.append(line.strip())

parse_date = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
parse_time = re.compile(r"(\d{2}):(\d{2})")
punctuation = ['.',',','?','!',';','\'','\"']

fileindex = index
tks_tweets_file_name = tks_tweets_file.split("/")[-1]
if tks_tweets_file_name[-4:] == ".txt":
	print tks_tweets_file_name[-4]
	tks_tweets_file_name = tks_tweets_file_name[:-4]
	print tks_tweets_file_name
os.system("mkdir " + filesdir + tks_tweets_file_name)
tks_tweets = codecs.open(tks_tweets_file,"r","utf-8").readlines()
#print tks_tweets_file
#print fileindex
for line in tks_tweets:
	try:		
		tokens = line.split("\t")
		text = tokens[6].strip()
		user = tokens[5]
		date = tokens[2]
		time = tokens[3]	
		dateparse = parse_date.search(date).groups()
		timeparse = parse_time.search(time).groups()
		dt = datetime.datetime(int(dateparse[0]),int(dateparse[1]),int(dateparse[2]),int(timeparse[0]),int(timeparse[1]),0)
		id_long = tokens[0]

		s_zeronum = 6-len(str(fileindex))
		i = 0
		s_filenum = str(fileindex) + ".txt"
		while i < s_zeronum:
			s_filenum = "0" + s_filenum
			i += 1
		filename = tks_tweets_file_name + "/" + prefix + s_filenum
		outfilename = filesdir + filename
		outfile = codecs.open(outfilename,"w","utf-8")

		new_text = []
		if ngrams:	
			tokens = text.split(" ")
			temp_lines = []	
			for token in tokens:
				token = re.sub("[\.,\?!;\'\":]","",token)
				if not token == "":
					if len(tokens) > 2:
						token = re.sub("[\.,\?!;\'\":]","",token)
					if not (filtword and re.search(filtword,token)):
						temp_lines.append(token)	
						if token in weights:
							new_text.append("intensifier")
						#print "intensifier: " + token + " " + outfilename
			temp_lines.append("<s>")
			temp_lines.insert(0,"<s>")
			for i,token in enumerate(temp_lines[1:len(temp_lines)-1]):
				unigram = token
				new_text.append(unigram)
			for i,token in enumerate(temp_lines[:len(temp_lines)-1]):
				bigram = token + "_" + temp_lines[i+1]
				new_text.append(bigram)
			for i,token in enumerate(temp_lines[:len(temp_lines)-2]):
				trigram = token + "_" + temp_lines[i+1] + "_" + temp_lines[i+2]
				new_text.append(trigram)

			for tt in new_text:
				outfile.write(tt + "\n")

		else:
			tokens = text.split(" ")
			for token in tokens:
				if len(tokens) > 2:
					token = re.sub("[\.,\?!;\'\":]","",token)
				if token in weights:
					outfile.write("intensifier ")
			outfile.write(text)

		outfile.close()
		if filttweet and re.search(filttweet,text):
			#print text
			classfile.write(filename + " " + filttweetlabel + "\n")
		else:
			classfile.write(filename + " " + label + "\n")
		metafile.write(filename + " " + str(id_long) + " " + str(dt) + " " + user + "\n")
		fileindex += 1
	except IndexError:
		#print str(fileindex) + " IE"
		continue

classfile.close()
metafile.close()

