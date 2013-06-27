#! /usr/bin/env python

from __future__ import division
import datetime
import re
import codecs
from collections import defaultdict
import argparse
import math
import rpy2.robjects as robjects
import tweetsfeatures

parser = argparse.ArgumentParser(description = "Prepare a regression experiment based on time to event per tweet.")
parser.add_argument('-etr', action='store', required = True, help = 'File with eventtags for trainingdata, begin date and time and end date and time, divided by a tab (for example \'grorod	15-04-2012	12:30	15-04-2012	14:30\'')
parser.add_argument('-ete', action='store', required = True, help = 'File with eventtags for testdata, begin date and time and end date and time, divided by a tab (for example \'grorod	15-04-2012	12:30	15-04-2012	14:30\'')
parser.add_argument('-tr', action='store', required = True, help = 'File with lines of frogged tweets for training and testing')
parser.add_argument('-te', action='store', required = True, help = 'File with lines of frogged tweets for testing')
parser.add_argument('-u', action='store', default = 'day', choices = ['day','hour','minute'], help = 'The unit of time by which the buckets will be generated (one of \'day\', \'hour\' or \'minute\'')
parser.add_argument('-p', action='store', default = 50, help = 'Pruning threshold for minimum frequency pruning of features (default = 50)')
parser.add_argument('-o', action='store', required = True, help = 'Outputdirectory to write results to')
#parser.add_argument('-b', action='store', required = True, help = 'File to write bucketfrequencies to')

args = parser.parse_args() 
eventfile_train = args.etr
eventfile_test = args.ete
tweets_train = args.tr
tweets_test = args.te
unit = args.u
prune = int(args.p)
outputdir = args.o
#bucketfreqs = open(args.b,"w")

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
	if unit == "day":
		return dif.days
	elif unit == "hour":
		hours = int(dif.days * 24) + int(dif.seconds / 3600)
		return hours
	elif unit == "minute":
		minutes = int(dif.days * 1440) + int(dif.seconds / 60)
		return minutes	

def return_buckets(eventfile,tweets,p = 10):

	event_time = {}
	tweet_event_timedif = defaultdict(list)
	# generate event-time hash
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

	"collecting tweets"
	collect = tweetsfeatures.Tweetsfeatures(tweets)
	collect.set_tweets(p=1)
	#print len(collect.tweets)
	collect.filter_domain(event_time.keys())
	collect.filter_label("before")
	#print len(collect.tweets)
	collect.remove_eventmention(event_time.keys())
	collect.add_ngrams(n=1)
	collect.add_ngrams(n=2)
	collect.add_ngrams()
	collect.prune_ngrams(p)

	# for each tweet
	#print len(collect.tweets)
	for tweet in collect.tweets:
		# link to event
		try:
			tweetdatetime = get_datetime(tweet.time.split(" ")[0],tweet.time.split(" ")[1],"vs")
			eventdatetime_begin = event_time[tweet.event][0]
			eventdatetime_end = event_time[tweet.event][1]
			event_zeropointtime = event_time[tweet.event][2] 
			# extract timedifference in chosen unit of time
			if tweetdatetime < eventdatetime_begin:
				if unit == "day":
					if (eventdatetime_begin - tweetdatetime) < event_zeropointtime:
						tweet_event_timedif[0].append(filename)
					else:
						eventdatetime_begin = (eventdatetime_begin - event_zeropointtime) + datetime.timedelta(days = 1) 
						tweetevent_time = timerel(eventdatetime_begin,tweetdatetime,unit)
						tweet_event_timedif[tweetevent_time].append(filename)
				else:
					tweetevent_time = timerel(eventdatetime_begin,tweetdatetime,unit)
					tweet_event_timedif[tweetevent_time].append(tweet)
		except IndexError:
			print "IE"
			continue

	return tweet_event_timedif

print "retrieve trainingdata"
tweet_event_timedif_train = return_buckets(eventfile_train,tweets_train,prune)
print "retrieve testdata"
tweet_event_timedif_test = return_buckets(eventfile_test,tweets_test)

term_index = {}
term_freq = defaultdict(int)

print "training"
# sort keys dictionary
sorted_buckets_train = sorted(tweet_event_timedif_train.keys())
num_tweets = 0
for bucket in sorted_buckets_train:
	#print str(bucket) + " " + str(len(tweet_event_timedif[bucket]))
	for tweet in tweet_event_timedif_train[bucket]:
		num_tweets += 1
		for term in tweet.features:
			term_freq[term] += 1

for i,term in enumerate(term_freq.keys()):
	term_index[term] = i

print "preparing hash"
regressionhash = defaultdict(list)
num_terms = len(term_index.keys())
print "no. of tweets " + str(num_tweets)
print "no. of terms " + str(num_terms)
for i in range(num_terms):
	for j in range(num_tweets):
		regressionhash[i].append(0)

for j in range(num_tweets):
	regressionhash["y"].append(0)

#print "la " + str(len(regressionhash[1]))

print "creating hash"
tweetindex = 0
for bucket in sorted_buckets_train:
	for tweet in tweet_event_timedif_train[bucket]:
		regressionhash["y"][tweetindex] = bucket
		for feature in tweet.features:
			featureindex = term_index[feature]
			regressionhash[featureindex][tweetindex] += 1
		tweetindex += 1

#print regressionhash

print "R modeling"
time_to_event = robjects.vectors.FloatVector(regressionhash["y"])
for i in range(num_terms):
	robjects.globalenv['x' + str(i)] = robjects.vectors.FloatVector(regressionhash[i])

robjects.globalenv['y'] = time_to_event
modelstring = "y ~ x0"
for i in range(num_terms)[1:]:
	modelstring = modelstring + " + x" + str(i)
	
model = robjects.r.lm(modelstring)

outfile_features = codecs.open(outputdir + "features.txt","w","utf-8")
for a,b in sorted(term_index.iteritems(), key=lambda x: (x[1], x[0])):
   outfile_features.write(a + "\n")

outfile_model = outputdir + "model.txt"
robjects.r.sink(file = outfile_model) 
print robjects.r.summary(model)
robjects.r.sink() 

print "testing"

outfile_results = open(outputdir + "results.txt", "w")
outfile_results.close()
outfile_coordinates = open(outputdir + "coordinates.txt","w")
outfile_coordinates.close()

testevents = [["heefey"],["adogra"],["excpsv"],["azagro","azgro"],["rjcfcu","rodfcu","rjcutr","rodutr"],["nacrkc"],["vitaja"],["vvvtwe"]]
eventtweets = defaultdict(lambda : defaultdict(list))
eventfreq = defaultdict(int)

sorted_buckets_test = sorted(tweet_event_timedif_test.keys())
event_bucket_freq = defaultdict(lambda : defaultdict(int))

for bucket in sorted_buckets_test:
	if bucket < 191:
		for tweet in tweet_event_timedif_test[bucket]:
		 	for i,testevent in enumerate(testevents):
				if tweet.event in testevent:
					eventfreq[i] += 1
					eventtweets[i][bucket].append(tweet)
					event_bucket_freq[i][bucket] += 1
	
regressionhash_test = defaultdict(lambda : defaultdict(list))
#print "no. of tweets " + str(num_tweets)
for i in range(num_terms):
	for j in range(len(testevents)):
		num_tweets = eventfreq[j]
		for k in range(num_tweets):
			regressionhash_test["y"][j].append(0)
			regressionhash_test[i][j].append(0)

#print regressionhash_test

#print "creating hash"
for event in eventtweets:
	tweet_index = 0
	for bucket in eventtweets[event]:
		#bucketfreq = len(tweet_event_timedif_test[bucket])
		#bucketfreqs.write(str(bucket) + " " + str(bucketfreq) + "\n")	
		for tweet in eventtweets[event][bucket]:
			regressionhash_test["y"][event][tweet_index] = bucket
			for feature in tweet.features:
				try:
					#print tweet_index
					#print "len " + str(len(regressionhash_test[featureindex][event]))
					featureindex = term_index[feature]
					regressionhash_test[featureindex][event][tweet_index] = 1
				except KeyError:
					continue
			tweet_index += 1

print "R formatting"
for event in eventtweets:
	print testevents[event]
	actual_time_to_event = robjects.vectors.FloatVector(regressionhash_test["y"][event])
	test = {}
	for i in range(num_terms): 
		test['x' + str(i)] = robjects.vectors.FloatVector(regressionhash_test[i][event])

#robjects.globalenv['y'] = actual_time_to_event
#teststring = "t0"
#for i in range(num_terms)[1:]:
#	teststring = teststring + " + t" + str(i)
	
#assign("dat",,envir=.GlobalEnv)

#print "apply test"
#robjects.r.predict(model,teststring)


#robjects.globalenv['y'] = actual_time_to_event
#teststring = "t0"
#for i in range(num_terms)[1:]:
#	teststring = teststring + " + t" + str(i)
	
#assign("dat",,envir=.GlobalEnv)

	print "apply test"
	dataf = robjects.DataFrame(test)
	pr = robjects.r.predict(model,dataf,interval = 'confidence')
	#pr = robjects.r.predict(model)
	#print pr
	
	outfile_results = open(outputdir + "results.txt", "a")
	outfile_results.write(testevents[event][0] + ":\n\n")
	outfile_coordinates = open(outputdir + "coordinates.txt","a")
	outfile_coordinates.write(testevents[event][0] + ":\n\n")

	tweet_prediction = defaultdict(list)
	summed_up_squared = 0
	for i in range(eventfreq[event]):
		dif = pr[i] - regressionhash_test["y"][event][i]
		sqdif = dif*dif
		summed_up_squared += sqdif
		outfile_results.write(str(i) + " " + str(pr[i]) + " " + str(regressionhash_test["y"][event][i]) + " " + str(sqdif) + "\n")
		tweet_prediction[regressionhash_test["y"][event][i]].append(pr[i])

	#print tweet_prediction

	num_tweets = 0
	summed_up_squared_cutoff = 0
	for actual_tte in sorted(tweet_prediction.keys()):
		absolute_error_total = 0
		for prediction in tweet_prediction[actual_tte]:
			error = prediction - actual_tte
			absolute_error = error			
			if error < 0:
				absolute_error = error * -1	   
			absolute_error_total += absolute_error
		#average_prediction = sum(tweet_prediction[actual_tte]) / len(tweet_prediction[actual_tte])
		#raw_error = average_prediction - actual_tte
		absolute_error_average = absolute_error_total / len(tweet_prediction[actual_tte])		
		outfile_coordinates.write(str(actual_tte * -1) + " " + str(absolute_error_average) + "\n")
		for prediction in tweet_prediction[actual_tte]:
			num_tweets += 1
			dif = prediction - actual_tte
			sqdif = dif*dif
			summed_up_squared_cutoff += sqdif

	#root_mean_square_error_cutoff = math.sqrt(summed_up_squared/num_tweets)
	#print root_mean_square_error_cutoff

	root_mean_square_error = math.sqrt(summed_up_squared/eventfreq[event])
	outfile_results.write("\n\n" + "root_mean_squared_error = " + str(root_mean_square_error) + "\n\n") 

	outfile_results.close()
	outfile_coordinates.close()

for i,testevent in enumerate(testevents):
	outfile_bucketfreq_event = open(outputdir + "time_frequency_" + testevent[0] + ".txt","w")
	for time in sorted(event_bucket_freq[i].keys()):
		outfile_bucketfreq_event.write(str(time) + " " + str(event_bucket_freq[i][time]) + "\n")
#print pr
#print robjects.r.summary(pr)

#linear_model = r.lm(model, data = d)
#print r.summary(linear_model)	

#print term_freq.keys()
#print sorted(term_freq.items(), key=lambda x: x[1],reverse=True)[:250]
#print term_freq


#> model2 = update(model1, .~.-Area)
#> step(model1, direction="backward")
