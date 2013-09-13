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
min_prune = int(sys.argv[6])

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
	tweet_event_timedif = defaultdict(lambda : defaultdict(list))
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
				tweetevent_time_minute = timerel(eventdatetime_begin,tweetdatetime,"minutes")
				tweet_event_timedif[tweetevent_time][tweetevent_time_minute].append(tweet)
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
		for minutetweet in hourtweets: 
			seen_tweets += len(hourtweets[minutetweet])
		accumulated_frequency_buckets[bucket] = seen_tweets	
	print "seen_tweets",seen_tweets
	cutoff = int(percent * seen_tweets)
	tweets_before_cutoff = (seen_tweets - cutoff) / 12
	for bucket in sorted_buckets:
		if accumulated_frequency_buckets[bucket] > cutoff:
			return (bucket,tweets_before_cutoff)

def generate_sparse(doc,label_hour,features):
	index_values = defaultdict(int)
	for feature in doc:
		try:
			index = feature_index[feature]
			index_values[index] += 1
		except KeyError:
			continue
	indexes = sorted(index_values.keys())
	datastring = ""
	if len(indexes) > 0:
		for i in indexes:
			datastring = datastring + str(i) + ","
		datastring = datastring + str(label_hour) + "\n"
		return datastring
	else:
		return None

print "retrieve data"
event_time_train = generate_eventhash(events_train)
events_normal = []
for event in event_time_train.keys():
	events_normal.append(event.split("_")[0])
train = tweetsfeatures.Tweetsfeatures(tweets_train)
train.set_tweets_oneline()
train.filter_domain(event_time_train.keys())
train.remove_eventmention(events_normal)
train.add_ngrams(n=1)
train.prune_ngrams(min_prune)
tweet_event_timedif = return_timebuckets(event_time_train,train)

cutoff = return_cutoff(tweet_event_timedif,train,0.95)
print cutoff

num_tweets = 0
for bucket in tweet_event_timedif.keys():
	if bucket <= cutoff[0]:
		for subbucket in tweet_event_timedif[bucket].keys():
			num_tweets += len(tweet_event_timedif[bucket][subbucket])

print "making featurelist..."
feature_freq = defaultdict(int)		
feature_index = {}
for bucket in tweet_event_timedif.keys():
	hourtweets = tweet_event_timedif[bucket]
	for minutetweets in hourtweets.keys():	
		for tweet in hourtweets[minutetweets]:
			for feature in tweet.features:
				feature_freq[feature] += 1

print "num_features: " + str(len(feature_freq.keys()))
outfile_features = codecs.open(outputdir + "features.txt","w","utf-8")
i = 0
for feature in feature_freq.keys():
	feature_index[feature] = i
	outfile_features.write(str(i) + " " + feature + "\n") 
	i += 1

print "preparing hash"
regressionhash = defaultdict(list)
num_features = len(feature_index.keys())
print "no. of tweets " + str(num_tweets)
print "no. of terms " + str(num_features)

tweetindex = 0
print "aggregating eventhours and creating hash..."
sorted_buckets_train = sorted(tweet_event_timedif.keys())
for bucket in sorted_buckets_train:
	if bucket <= cutoff[0]:	
		print bucket
		hourtweets = tweet_event_timedif[bucket]
		minutes = sorted(tweet_event_timedif[bucket].keys())
		try:
			hourtweets_next = tweet_event_timedif[bucket+1]
			hourtweets_next_minutes = sorted(tweet_event_timedif[bucket+1].keys())
		except IndexError:
			hourtweets_next = None
		for i,minutetweets in enumerate(minutes):
			tweets_aggregate = defaultdict(lambda : defaultdict(int))
			for minute in minutes[i:]:
				for tweet in hourtweets[minute]:		
					for feature in tweet.features:
						tweets_aggregate[tweet.event][feature_index[feature]] += 1
					
			if hourtweets_next:
				for minutetweets_next in hourtweets_next_minutes:
					if int(minutetweets_next) <= int(minutetweets):
						for tweet in hourtweets_next[minutetweets_next]:
							for feature in tweet.features:
								tweets_aggregate[tweet.event][feature_index[feature]] += 1
			for event in tweets_aggregate.keys():	
				regressionhash["y"].append(bucket)
				for i in range(num_features):
					regressionhash[i].append(0)
				for ind in tweets_aggregate[event].keys():
					regressionhash[ind][tweetindex] = tweets_aggregate[event][ind]
				tweetindex += 1

print "num_instances:",len(regressionhash[0])

exit()

print "R modeling"
time_to_event = robjects.vectors.FloatVector(regressionhash["y"])
for i in range(num_features):
	robjects.globalenv['x' + str(i)] = robjects.vectors.FloatVector(regressionhash[i])

robjects.globalenv['y'] = time_to_event
modelstring = "y ~ x0"
for i in range(num_features)[1:]:
	modelstring = modelstring + " + x" + str(i)
	
model = robjects.r.lm(modelstring)

outfile_features = codecs.open(outputdir + "features.txt","w","utf-8")
for a,b in sorted(feature_index.iteritems(), key=lambda x: (x[1], x[0])):
   outfile_features.write(a + "\n")

outfile_model = outputdir + "model.txt"
robjects.r.sink(file = outfile_model) 
print robjects.r.summary(model)
robjects.r.sink() 

print "testing"
event_time_test = generate_eventhash(events_test)
for testevent in event_time_test.keys():
	print testevent
	test = tweetsfeatures.Tweetsfeatures(tweets_test)
	test.set_tweets_oneline()
	test.filter_domain(testevent)
	test.add_ngrams(n=1)
	tweet_event_timedif_test = return_timebuckets(event_time_test,test)
	sorted_buckets_test = sorted(tweet_event_timedif_test.keys())

	regressionhash_test = defaultdict(list)
	hour_to_event_hash = defaultdict(list)
	tweetindex = 0
	for bucket in sorted_buckets_test:
		hourtweets = tweet_event_timedif_test[bucket]
		minutes = sorted(tweet_event_timedif_test[bucket].keys())
		try:
			hourtweets_next = tweet_event_timedif_test[bucket+1]
			hourtweets_next_minutes = sorted(tweet_event_timedif_test[bucket+1].keys())
		except IndexError:
			hourtweets_next = None
		for i,minutetweets in enumerate(minutes):
			tweets_aggregate = defaultdict(int)
			for minute in minutes[i:]:
				for tweet in hourtweets[minute]:		
					for feature in tweet.features:
						try:
							tweets_aggregate[feature_index[feature]] += 1
						except KeyError:
							continue
			if hourtweets_next:
				for minutetweets_next in hourtweets_next_minutes:
					if int(minutetweets_next) <= int(minutetweets):
						for tweet in hourtweets_next[minutetweets_next]:
							for feature in tweet.features:
								try:
									tweets_aggregate[feature_index[feature]] += 1
								except KeyError:
									continue
			
			regressionhash_test["y"].append(bucket)
			hour_to_event_hash[bucket].append(tweetindex)
			for i in range(num_features):
				regressionhash_test[i].append(0)
			for ind in tweets_aggregate.keys():
				regressionhash_test[ind][tweetindex] = tweets_aggregate[ind]
			tweetindex += 1

	print "R formatting"	
	actual_time_to_event = robjects.vectors.FloatVector(regressionhash_test["y"])
	test = {}
	for i in range(num_features): 
		test['x' + str(i)] = robjects.vectors.FloatVector(regressionhash_test[i])

	print "apply test"
	dataf = robjects.DataFrame(test)
	pr = robjects.r.predict(model,dataf,interval = 'confidence')

	outfile_results = open(outputdir + "results_" + testevent + ".txt", "w")
	outfile_coordinates = open(outputdir + "coordinates_" + testevent + ".txt","w")

	tweet_prediction = {}
	summed_up_squared = 0
	for testlabel in sorted(hour_to_event_hash.keys()):
		#print testlabel
		testtweets = hour_to_event_hash[testlabel]	
		for testtweet in testtweets:
			prediction = pr[testtweet]
			if prediction < 0:
				prediction = 0
			outfile_coordinates.write(str(testlabel) + " " + str(prediction) + "\n")
		#prediction_summed = 0
		#for testtweet in testtweets:
		#	prediction_summed += pr[testtweet]
		#prediction = prediction_summed / len(testtweets)
		#dif = prediction - testlabel
		#print prediction,testlabel
		#sqdif = dif*dif
		#summed_up_squared += sqdif		
		#outfile_results.write(str(i) + " " + str(prediction) + " " + str(testlabel) + " " + str(sqdif) + "\n")
		#tweet_prediction[testlabel] = prediction

	#root_mean_square_error = math.sqrt(summed_up_squared/len(hour_to_event_hash.keys()))
	#outfile_results.write("\n\n" + "root_mean_squared_error = " + str(root_mean_square_error) + "\n\n") 

	outfile_results.close()
	outfile_coordinates.close()

