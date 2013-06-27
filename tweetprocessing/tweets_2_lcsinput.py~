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

