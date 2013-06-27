#! /usr/bin/env python

from __future__ import division
import codecs
import re
import nltk
import sys
from collections import defaultdict
import tweetsfeatures

frogged_tweets = sys.argv[1]
path = sys.argv[2]
prefix = sys.argv[3]
classfile = sys.argv[4]
metafile = sys.argv[5]

collect = tweetsfeatures.Tweetsfeatures(frogged_tweets)
collect.set_tweets(p=1)
collect.tweets_2_lcsinput(path,prefix,classfile,metafile)

filenum = 0
		outclass = codecs.open(classfile,"a","utf-8")
		outmeta = codecs.open(metafile,"a","utf-8")
		for t in self.tweets:
			s_zeronum = 5-len(str(filenum))
			i = 0
			s_filenum = str(filenum) + ".txt"
			while i < s_zeronum:
				s_filenum = "0" + s_filenum
				i += 1
			print s_filenum
			filename = prefix + s_filenum
			outfilename = path + filename
			outfile = codecs.open(outfilename,"w","utf-8")
			words = t.wordsequence
			text = " ".join(words)
			label = t.label
			user = t.user
			time = t.time
			event = t.event
			outfile.write(text)
			outclass.write(filename + " " + label + "\n")
			outmeta.write(filename + " " + event + 
				" " + time + " " + user + "\n")
			filenum += 1


