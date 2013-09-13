#! /usr/bin/env python

from __future__ import division
import sys
import datetime
import re
import codecs
from collections import defaultdict
import math
import rpy2.robjects as robjects
import tweetsfeatures

events_train = sys.argv[1]
events_test = sys.argv[2]
tweets_train = sys.argv[3]
tweets_test = sys.argv[4]
outputdir = sys.argv[5] 
#min_threshold = int(sys.argv[6])

def get_datetime(date,time,setting = "eu"):
	if setting == "eu":			
		parse_date = re.compile(r"(\d{2})-(\d{2})-(\d{4})")
	elif setting == "vs":
		parse_date = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
	parse_time = re.compile(r"(\d{2}):(\d{2})")
	dateparse = parse_date.search(date).groups(1)
	timeparse = parse_time.search(time).groups(1)
	if setting == "eu":
		datetime_obj = datetime.datetime(int(dateparse[2]),int(dateparse[1]),int(dateparse[0]),int(timeparse[0]),int(timeparse[1]),0)
	elif setting == "vs":
		datetime_obj = datetime.datetime(int(dateparse[0]),int(dateparse[1]),int(dateparse[2]),int(timeparse[0]),int(timeparse[1]),0)
	
	return datetime_obj

def get_hoursbefore_sameday(date,time,setting = "eu"):
	if setting == "eu":			
		parse_date = re.compile(r"(\d{2})-(\d{2})-(\d{4})")
	elif setting == "vs":
		parse_date = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
	parse_time = re.compile(r"(\d{2}):(\d{2})")
	dateparse = parse_date.search(date).groups(1)
	timeparse = parse_time.search(time).groups(1)
	if setting == "eu":
		datetime_obj = datetime.datetime(int(dateparse[2]),int(dateparse[1]),int(dateparse[0]),int(timeparse[0]),int(timeparse[1]),0)
		zeropoint = datetime.datetime(int(dateparse[2]),int(dateparse[1]),int(dateparse[0]),0,0,0)
		return datetime_obj - zeropoint
	elif setting == "vs":
		datetime_obj = datetime.datetime(int(dateparse[0]),int(dateparse[1]),int(dateparse[2]),int(timeparse[0]),int(timeparse[1]),0)
		zeropoint = datetime.datetime(int(dateparse[0]),int(dateparse[1]),int(dateparse[2]),0,0,0)
		return datetime_obj - zeropoint
	
	return datetime_obj

def timerel(event_begin,tweet_time,timeunit):
	dif = event_begin - tweet_time
	if timeunit == "hours":
		hours = int(dif.days * 24) + int(dif.seconds / 3600)
		return hours
	elif timeunit == "minutes":
		hours = int(dif.seconds / 3600)	
		minutes = int(dif.seconds / 60) - (hours * 60)
		return minutes

#def aggregate_tweets(windowsize,tweets)

def generate_eventhash(eventfile):
	event_time = {}
	eventfile_open = open(eventfile,"r")
	for event in eventfile_open:
		tokens = event.strip().split("\t")
		eventname = tokens[0]
		eventdate_begin = tokens[1]
		eventtime_begin = tokens[2]
		eventdatetime_begin = get_datetime(eventdate_begin,eventtime_begin)
		eventdatetime_hoursbefore_sameday = get_hoursbefore_sameday(eventdate_begin,eventtime_begin)
		eventdate_end = tokens[3]
		eventtime_end = tokens[4]
		eventdatetime_end = get_datetime(eventdate_end,eventtime_end)
		event_time[eventname] = (eventdatetime_begin,eventdatetime_end,eventdatetime_hoursbefore_sameday)

	eventfile_open.close()
	return event_time

def return_timebuckets(eventhash,collect):
	tweet_event_timedif = defaultdict(list)
	for tweet in collect.tweets:
		# link to event
		try:
			tweetdatetime = get_datetime(tweet.date,tweet.time,"vs")
			eventdatetime_begin = eventhash[tweet.event][0]
			eventdatetime_end = eventhash[tweet.event][1]
			event_zeropointtime = eventhash[tweet.event][2] 
			# extract time difference in chosen unit of time
			if tweetdatetime < eventdatetime_begin:
				tweetevent_time = timerel(eventdatetime_begin,tweetdatetime,"hours")
				tweet_event_timedif[tweetevent_time].append(tweet)
		except IndexError:
			print "IE"
			print tweet.features
			continue

	return tweet_event_timedif

def return_cutoff(tweet_buckets,collect,percent):
	accumulated_frequency_buckets = defaultdict(int)
	seen_tweets = 0
	sorted_buckets = sorted(tweet_buckets.keys())
	for bucket in sorted_buckets:
		hourtweets = tweet_buckets[bucket]
		seen_tweets += len(hourtweets)
		accumulated_frequency_buckets[bucket] = seen_tweets	
	print "seen_tweets",seen_tweets
	cutoff = int(percent * seen_tweets)
	tweets_before_cutoff = (seen_tweets - cutoff) / 12
	for bucket in sorted_buckets:
		if accumulated_frequency_buckets[bucket] > cutoff:
			return (bucket,tweets_before_cutoff)

print "retrieve data"
event_time_train = generate_eventhash(events_train)
events_normal = []
for event in event_time_train.keys():
	events_normal.append(event.split("_")[0])
train = tweetsfeatures.Tweetsfeatures(tweets_train)
train.set_tweets_oneline()
train.filter_domain(event_time_train.keys())
tweet_event_timedif = return_timebuckets(event_time_train,train)
cutoff = return_cutoff(tweet_event_timedif,train,0.95)

num_tweets = 0
for bucket in tweet_event_timedif.keys():
	if bucket < cutoff[0]:
		num_tweets += len(tweet_event_timedif[bucket])

tweet_hour_sum = 0 
tweetindex = 0
for bucket in sorted(tweet_event_timedif.keys()):
	tweetindex += len(tweet_event_timedif[bucket])
	tweet_hour_sum += (len(tweet_event_timedif[bucket]) * bucket)

mean = tweet_hour_sum / tweetindex
print "mean:",mean

event_time_test = generate_eventhash(events_test)
for testevent in event_time_test.keys():
	print testevent
	outfile = open(outputdir + "mean_" + testevent + ".txt","w")
	test = tweetsfeatures.Tweetsfeatures(tweets_test)
	test.set_tweets_oneline()
	test.filter_domain(testevent)
	tweet_event_timedif_test = return_timebuckets(event_time_test,test)
	sorted_buckets_test = sorted(tweet_event_timedif_test.keys())
	hours = range(sorted_buckets_test[-1]+1)[::-1]	
	num_tweets = 0
	for bucket in hours:
		outfile.write(str(bucket) + " " + str(mean) + "\n")
		
