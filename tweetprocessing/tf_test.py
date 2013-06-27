#! /usr/bin/env python

from tweetsfeatures_tks import Tweetsfeatures
import sys
import codecs

tweets = sys.argv[1]
events = sys.argv[2]

test = Tweetsfeatures(tweets)
test.set_tweets(p=1,u=1)
test.set_timelabel_firstlayer(events)






