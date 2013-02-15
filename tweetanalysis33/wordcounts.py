
import sys
#sys.path.append("..")


from tweetprocessing33.tweetsfeatures import Tweetsfeatures
import codecs
import operator
import datetime
import time

# import pytz
import numpy
import pandas
import matplotlib
import math

# from pandas import *
# from numpy import *
# from datetime import *
# from pytz import *

from collections import defaultdict

from matplotlib import pyplot
from matplotlib.dates import date2num
# from datetime import datetime
from collections import Counter

from pylab import *
# from time import clock, time

#Notes:
# Create running average Graphs.
# Make it to work for particular events
# Store in a dict- word:timeseries for it
# Vector similarity measures ? How can we discover related words by these similarity.
# Create methods for Tweet based and CrossDomainWord relative frequencies.
# Let the label to be print is it before or b ?

class Event:
	"Events has an object that contains, event time, event place, used words, ..."

#Notes:
# Which tweet count should be taken to calculate the frequency ? Now: just for relevant time category tweet counts.
# Make the calculations for just one word, the one requested, think about it !
# inherit a class from Event class which can be a combination of events (list of names, places, start times)
# Some attributes or subclasses for different time in the week, and day.
# Compare just same day of the week, same hour, later extend.Like same day and hour but different week, ...
# For not accumulated ones but : delete words with the count 1, so more efficient.

	def __init__(self, e_name, e_place, e_time, label_list):

		self.name = e_name
		self.place = e_place
		self.time = e_time
		self.labels = label_list
		self.tweets = {}
		self.words = {}
		self.word_freq = {}
		self.w_tseries = {}
		self.tweet_tseries = {}
		self.normalized_w_tseries = {}
		self.smoothed_w_tseries={}
		self.w_mean_list = {}
		self.w_stdev_list = {}

		for l in label_list:
			self.tweets[l] = [] # list of tweets with this label to put the tweets of this label
			self.words[l]= Counter() # A counter of words for this label to put the count of words
			self.word_freq[l] = {} # A dictionary of words for a particular label to put their frequency
			self.w_tseries[l] = {} # A dictionary to put a word as keyterm and its timeseries array tuple.
			self.tweet_tseries[l] =[] # A timeserie list of tweets for this label
			self.normalized_w_tseries[l] = {} # A dictionary to put normalized(by tweet count) time series for each word.
			self.smoothed_w_tseries[l] = {}
			self.w_mean_list[l] = {}
			self.w_stdev_list[l] = {}


	def store_event_tweets(self, tf, label_list):
		"Store tweets in the dictionary in the relevant label list"
		for t in tf.tweets:
			if t.label in label_list: # Do it just for the labels wanted to be taken into account.
				self.tweets[t.label].append(t)

	def count_all_words(self, label_list):
		"Count and add per event and label"
		for label in label_list:
			for t in self.tweets[label]:
				for w in list(set(t.get_wordsequence())):
					self.words[t.label][w] += 1

	def count_for_word(self, label, w):
		"Count just for this list of words, in this label"
		for t in self.tweets[label]:
			if w in list(set(t.get_wordsequence())):
				self.words[label][w] += 1

	def calcFreq_all_words(self, label_list): # you can make it just for one or several words, to gain time and memory
		"if one label contain one word, interpreter makes word to char conversion, careful ! "
		for label in label_list: 
			for word, w_count in self.words[label].items():
				self.word_freq[label][word] = w_count / len(self.tweets[label])

	def calcFreq_for_word(self, w, label): # you can make it just for one or several words, to gain time and memory
		self.word_freq[label][w] = self.words[label][w] / len(self.tweets[label])

	def calc_tseries(self, w, label, minuteForFrame, dayCount):
		if len(self.tweet_tseries[label]) == 0:
			time_list_for_tweets = sorted([x.time for x in self.tweets[label]])
			#this is a tuple
			self.tweet_tseries[label] = self.calc_tseries_tweets(time_list_for_tweets, minuteForFrame,dayCount)

		time_list_for_word = [t.time for t in self.tweets[label] if w in list(set(t.get_wordsequence())) ]
		self.w_tseries[label][w] = self.calc_tseries_count_words(time_list_for_word, minuteForFrame, dayCount)

		self.normalized_w_tseries[label][w] = self.normalize_w_by_tweet_tseries(w, label)
		
		self.smoothed_w_tseries[label][w] = self.running_average(self.normalized_w_tseries[label][w])

		if w not in self.word_freq[label]:
			#print('Freq is None, calculating ...:', w)
			self.calcFreq_for_word(w, label)
		self.w_mean_list[label][w] = [self.word_freq[label][w]] * len(self.smoothed_w_tseries[label][w])
		self.w_stdev_list[label][w] = [numpy.std(self.smoothed_w_tseries[label][w])] * len(self.smoothed_w_tseries[label][w])

		# running average make the lists shorter
		#cut from back, to have a graph from the zero point of the event.
		return (self.tweet_tseries[label][0][:-2], self.smoothed_w_tseries[label][w])
		
	def calc_tseries_tweets(self, time_list_for_tweet, minuteForFrame, day_count):
		"It calculates backward from the --End of Before-- of an event, be careful for --End of other labels-- !"
		"""
		Time list should be ordered, ascending
		"""
		xlabels = []
		xvalues = []
		tweetCount = 0
		t_delta = 0

		seconds_back = 60*60*24*day_count
		timespan= self.time - datetime.timedelta(day_count)
		while t_delta < seconds_back:
			count = 0
			interval = self.time - datetime.timedelta(0, t_delta)
			before_interval = interval - datetime.timedelta(0,60*minuteForFrame)

			for t in time_list_for_tweet:#list is ordered, break the loop if t > self.time
				if t > self.time:
					break; #time list should be sorted
				else:
					if t < self.time and t > timespan:# if the date in the range of search space
						if t >= before_interval and t < interval:
							count += 1
							#Do not put break here, it does not count anything then.
			
			xvalues.append(count)
			xlabels.append(0-t_delta/3600) # Give hours before a match
			t_delta = t_delta + 60*minuteForFrame

		return (xlabels, xvalues)

	def calc_tseries_count_words(self, time_list_for_word, minuteForFrame, day_count):
		""" It calculates backward from the --End of Before-- of an event, be careful for --End of other labels-- !
		There is not any xlabels here, it is taken from the tweets time series.
		Time list should be ordered, ascending
		"""
		xvalues = []
		tweetCount = 0
		t_delta = 0

		seconds_back = 60*60*24*day_count
		timespan= self.time - datetime.timedelta(day_count)
		while t_delta < seconds_back:
			count = 0
			interval = self.time - datetime.timedelta(0, t_delta)
			before_interval = interval - datetime.timedelta(0,60*minuteForFrame)
			
			for t in time_list_for_word:#list is ordered, break the loop if t > self.time
				if t > self.time:
					break; #time list should be sorted
				else:
					if t < self.time and t > timespan:# if the date in the range of search space
						if t >= before_interval and t < interval:
							count += 1
						#Do not put break here, it does not count anything then.
			
			xvalues.append(count)
			t_delta = t_delta + 60*minuteForFrame

		return xvalues

	def normalize_w_by_tweet_tseries(self, word, label):
		"Make this more efficient with numpy array"
		if len(self.w_tseries[label][word]) == len(self.tweet_tseries[label][1]):
			return [a/b if b > 0 else 0 for a, b in zip(self.w_tseries[label][word], self.tweet_tseries[label][1]) ]
		else:
			print("Length of the word tseries and tweet time series should be equal")
			print("Word tserie length:",len(self.w_tseries), "Tweet tserie:", len(self.tweet_tseries[label][1]))
			exit()
		return False

	def running_average(self, t_series_l):
		"returned list has 2 elements less than normal one, make the change in plotting for the other list"
		"? weights should be 4 2 1 or 1 2 4 ?, is the order of current, next1 and next2 right ?"
		r_average = []
		av = 0
		divide_by = 7 # 3 elems + 1 for the weight of the middle one = 4
		for current, next1, next2 in self.neighborhood(t_series_l):
			av=math.fsum([4*current, 2*next1, next2])/divide_by
			
			r_average.append(av)

		r_average.append(math.fsum([4*t_series_l[-1], 2*t_series_l[-2], t_series_l[-3]])/divide_by)

		return r_average

	def neighborhood(self, iterable):
		iterator = iter(iterable)
		
		current = iterator.__next__()  # throws StopIteration if empty.
		next1 = iterator.__next__()
		next2 = iterator.__next__()
		for next in iterator:
			yield (current, next1, next2)
			current = next1
			next1 = next2
			next2 = next

	def print_word_counts(self):
		for label in self.labels:
			print('Event Name:',self.name)
			print('Label:', label, 'TweetCount For this label:', len(self.tweets[label]))

			for w in self.words[label].most_common():
				print(w)

	def get_tweets_from_to(self, label, from_hour, to_hour):
		"""
		1- Event time start from zero and goes back.
		2- Give hours as positive integers.

		"""
		print('into get_tweets+from_to - Object')
		tweets_in_interval = []
		from_t = self.time - datetime.timedelta(hours = min(from_hour, to_hour))
		to_t = self.time - datetime.timedelta(hours = max(from_hour, to_hour)) 

		print('from_t, to_t:', from_t, to_t)
		print('Match Time:', self.time)
		for tweet in self.tweets[label]:# list of labels
			#print(tweet.time)
			if tweet.time < from_t and tweet.time > to_t:
				tweets_in_interval.append(tweet)

		print('Min and max:', min(from_hour, to_hour), max(from_hour, to_hour))
		return [t.get_wordsequence() for t in tweets_in_interval]

	def test_for_inheritance(self):
		print('I am in the superclass ...')

class BlendEvent(Event):

	def __init__(self, events_l):
		self.events_list = events_l
		self.name = [e.name for e in events_l]
		self.place = [e.place for e in events_l]

		self.time = {e.name:e.time for e in events_l}
		self.label = [events_l[0].labels[0]] # be careful, labels should be same for all events.. Use the first label of the first event.
		l = self.label[0]
		#print('Label for this BlendObject is:',self. label)
		self.tweets = {l:[]}
		#self.tweets[l] = [self.tweets[l]+e.tweets[l] for e in events_l] # list of tweets with this label to put the tweets of this label

		for e in events_l:
			self.tweets[l] += e.tweets[l]
		
		self.words = {}
		self.words[l] = Counter() # A counter of words for this label to put the count of words

		for e in events_l:
			self.words[l] += e.words[l]
		# print(self.name)
		# print('Added Object-s word count:',e.words[self.label[0]].most_common(20), '\n---------------')
		# print('Blend Object Word count:', self.words[self.label[0]].most_common(20), '\n---------------')

		self.tweet_tseries = {l:[]} # A timeserie dict of tweets for this label, X axe same for all, take the first one
		self.tweet_tseries[l].append(events_l[0].tweet_tseries[l][0]) # X dimension
		self.tweet_tseries[l].append([0] * len(self.tweet_tseries[l][0]))
		#print('X axe for the Blend Object:',self.tweet_tseries[l])
		#print('First initialization of Blend Tweet Series:', self.tweet_tseries[l])

		for e in events_l:
			if len(self.tweet_tseries[l][1]) == len(e.tweet_tseries[l][1]):
				self.tweet_tseries[l][1] = [a+b for a, b in zip(self.tweet_tseries[l][1],e.tweet_tseries[l][1])]
				print('Added object time serie:',e.tweet_tseries[l][1])
				print('Blended time serie',self.tweet_tseries[l][1])
			else:
				print('Length of blended objects tweet time series should be at same length',len(self.tweet_tseries[l][1]), len(e.tweet_tseries[l][1]))
				exit()
	

		self.w_tseries = {l:{}} # A dictionary to put a word as keyterm and its timeseries list, tuple..or list.
		for e in events_l:
			for w, tserie in e.w_tseries[l].items():
				if w not in self.w_tseries[l]:
					self.w_tseries[l][w] = [0] * len(tserie)
				self.w_tseries[l][w] = [a+b for a, b in zip(self.w_tseries[l][w], tserie)]

		self.word_freq = {l:{}} # A dictionary of words for a particular label to put their frequency
		self.normalized_w_tseries = {l:{}}
		self.smoothed_w_tseries={l:{}}
		self.w_mean_list = {l:{}}
		self.w_stdev_list = {l:{}}

	def calc_tseries(self, w, label):

		self.normalized_w_tseries[label][w] = self.normalize_w_by_tweet_tseries(w, label)
		
		self.smoothed_w_tseries[label][w] = self.running_average(self.normalized_w_tseries[label][w])

		if w not in self.word_freq[label]:
			#print('Freq is None, calculating ...:', w)
			self.calcFreq_for_word(w, label)
			print('Calculates:', w, ' -Freq')
		self.w_mean_list[label][w] = [self.word_freq[label][w]] * len(self.smoothed_w_tseries[label][w])
		self.w_stdev_list[label][w] = [numpy.std(self.smoothed_w_tseries[label][w])] * len(self.smoothed_w_tseries[label][w])

		# running average make the lists shorter
		#cut from back, to have a graph from the zero point of the event.
		return (self.tweet_tseries[label][0][:-2], self.smoothed_w_tseries[label][w])
	

class SingleWordAnalysis():
	"Statistical analysis of Tweets"
	"""
	Currently it uses Tweetfeatures objects to calculate statistical measures of word use in different tweet classes.
	Tweets could be in different classes like before, during, after. 
	-- Later, category type and count can be done generic.
	
	example usage:
	...

	"""

	def __init__(self, frogged_file=None, event_names=None, event_times=None, event_places= None):
		"Set the file values"

		self.event_names = event_names
		self.event_times = event_times
		self.event_places = event_places
		self.tf = Tweetsfeatures(frogged_file)
		self.tf.set_tweets(u=1, ht=1, p=1) # remove urls, hashtags and punctuation

		self.relative_freq_before_dict = {}
		self.relative_freq_during_dict = {}
		self.relative_freq_after_dict = {}
		self.freq_before_dict = defaultdict(float)
		self.freq_during_dict = defaultdict(float)
		self.freq_after_dict = defaultdict(float)
		self.counter_before = Counter()
		self.counter_during = Counter()
		self.counter_after = Counter()
		self.counter_before_rest = Counter()
		self.counter_during_rest = Counter()
		self.counter_after_rest = Counter()
		self.counter_events = Counter()
		self.word_list = [] #keeps all words for iteration, list, make it counter (union)
		self.word_list_rest = Counter() # keep all words and their counts for iteration
		self.event_times = event_times
		self.before_tweets = []
		
		#counts, freqs should be done, for all. # order of these mathods should be preserved.
		# self.count_words()  self.calc_words_freq()  self.calc_words_relative_freq()

		self.events_dict = {} # event objects

	def crea_event_objs_for(self, label_list, crea_event_obj_for):
		"it handles hashtag names specific for soccer matches"
		"""
		Info: Creates a different object for each event
		Notes:
		1- Add event list to be taken into account. Events that are not in the list should not be processed.
		2- An event object for all soccer matches.
		"""
		for name in crea_event_obj_for:
			
			if len(name) == 5 and name[:2] == 'az':
				e_place = 'az'
			else:
				e_place = name[:3]
			
			self.events_dict[name] = Event(name, self.event_places[e_place], self.event_times[self.event_names.index(name)], label_list)
		
		for t in self.tf.tweets: #put tweets in the relevant places
			if t.label in label_list and t.event in crea_event_obj_for: #ignore tweets that does not have proper hashtag and label.
				self.events_dict[t.event].tweets[t.label].append(t)

		for name, event in self.events_dict.items():
			event.count_all_words(label_list)

	def find_same_time_events(self):
		found_events = []
		time_per_event = {}
		for name, event in self.events_dict.items():
			time_per_event[str(event.time)] = []

		for n, e in self.events_dict.items():
			time_per_event[str(e.time)].append(e.name)

		for t, l in time_per_event.items():
			print(t,str(l))

	def get_event_tweets_from_to(self, label, eventname, from_time, to_time):
		print('into get_event_tweets_from_to')
		return self.events_dict[eventname].get_tweets_from_to(label, from_time, to_time)

	def calc_euc_distance_w(self, w, labels, events, minuteForFrame, dayCount):
		'First event is training, the second test.Later adapt it to fist n-1 training, n. is test'
		"""
		  First label should be before for now.
		  since the X axes is same we do not take it into account

		  Error: It should take smoothed values not counts !!!

		  Questions:
		     1- Should I normalize scores for trained and test lists
		"""
		for e in events:
			for l in labels:
				event = self.events_dict[e]
				word_t_series = event.calc_tseries(w, l, minuteForFrame, dayCount)
				print(event.name, l, w)
				print('Count:', event.words[l][w])
				print('Freq:', event.word_freq[l][w])
				print('Len of tseries X and Y:',len(word_t_series[0]), len(word_t_series[1]),'Y and X dimension:\n', word_t_series[0], word_t_series[1]) # calc the time serie
				print('Len of word timeseries:',len(event.w_tseries[l][w]),'Word Time series:\n', event.w_tseries[l][w])
				print('Len of Normalized W TSeries:',len(event.normalized_w_tseries[l][w]),'Normalized Word Time series:\n', event.normalized_w_tseries[l][w])
				print('Len of smoothed_w_tseries:',len(event.smoothed_w_tseries[l][w]),'Smoothed Word Time series:\n', event.smoothed_w_tseries[l][w])
				#print()
		trained_X = self.events_dict[events[0]].tweet_tseries[labels[0]][0] # get it from tweet time series. It is same for all events.
		#trained_Y = self.events_dict[events[0]].w_tseries[labels[0]][w] # Word counts not so good results.if there is more counts, euc. distance is more
		trained_Y = self.events_dict[events[0]].smoothed_w_tseries[labels[0]][w] # this should produce more balanced results.
		trained = [(a,b) for a, b in zip(trained_X, trained_Y)]
		print('Len of trained tuples:',len(trained), 'trained tupples:\n',trained)
		print('Reversed trained tuples:\n',list(reversed(trained)))
		trained = list(reversed(trained)) # Time was reversed in the normal array. For the normal timeline with the test data.
		#trained = numpy.array([trained_X, trained_Y])
		print('Trained Y:\n',trained_Y)
		print('Reversed Training:\n',list(reversed(trained_Y)))
		test_Y = self.events_dict[events[1]].w_tseries[labels[0]][w]
		#test = numpy.array([trained_X,trained_Y])
		print( 'Len of Test:',len(test_Y),'Test:\n',test_Y)
		print('Difference between trained and test:',len(test_Y)-len(trained))
		test_Y = test_Y[:len(trained)] #test_Y, when not smoothed, is longer be careful
		print( 'After length Normalization, Len of Test:',len(test_Y),'Test:\n',test_Y)

		y_difference = [a-b for a, b in zip(trained_Y, test_Y)]
		print('y_difference:\n', y_difference)
		print('Absolue of y_difference:\n', [abs(a) for a in y_difference])

		i = 0
		test_seq = []
		euc_diff_list = []
		trained_sub_seq = []
		for test_item in reversed(test_Y):
			test_seq.append(test_item)
			print('Test Sequence:',test_seq)

			x=0
			for t in trained:
				temp_sub_seq = trained[x:x+len(test_seq)] #create subsequences of the length of observed test data
				if len(temp_sub_seq) == len(test_seq):
					trained_sub_seq.append(temp_sub_seq)
				else:
					break
				x +=1
			
			print('--Training Sequences:')
			print(*trained_sub_seq, sep='\n')

			euc_distances = []
			for temp_sub_seq in trained_sub_seq:
				#Calc euc. distance and add it as a tuple with the last time point. for this subsequence
				euc_distances.append((temp_sub_seq[-1][0],sqrt(math.fsum([(a-b[1])**2 for a, b in zip(test_seq, temp_sub_seq)]))))
			print('--Euclidian distances:')
			print(*euc_distances, sep='\n')

			#Find the smallest euc. distance
			smallest_euc = min([a[1] for a in euc_distances])
			print('Smallest Euc:', smallest_euc )
			#Choose the average of the lowest time values if there is more than one.
			matched_times = [a[0] for a in euc_distances if a[1] == smallest_euc]
		     
			print('matched times:\n', matched_times)
			print('average of matched times:',numpy.mean(matched_times))


			#start again for more observation
			trained_sub_seq = [] 
			euc_distances = []
			print('------------------------------------------------------------------')
			#euc_diff_list = [abs(trained[i]-test_item) for a in zip(trained_Y)]

		
		#test = [] # two dimensions
	def calc_euc_dist_w_list_normalized(self, w_list, labels, events, minuteForFrame, dayCount):
		'First event is training, the second test.Later adapt it to fist n-1 training, n. is test'
		"""
		  -First label should be before for now.
		  -Since the X axes is same we do not take it into account
		  -First event training second is test
		  - It takes perfect match between train and test sets. starting from the same point in time and increase one observation per day.

		  Questions:
		     1- Should I normalize scores for trained and test lists
		"""
		
		label = labels[0]
		square_err_predict_list = []
		square_err_mean_list = []
		square_err_median_list = []

		mean_sq_err_predict_l = []
		mean_sq_err_mean_l = []
		mean_sq_err_median_l = []

		for name, event in self.events_dict.items():
			for l in labels:
				for w in w_list:
					if w not in event.normalized_w_tseries[l]:
						word_t_series = event.calc_tseries(w, l, minuteForFrame, dayCount) # calc. relevant freq, t_series
						print('Word and its tserie:', w, word_t_series)

		if type(events[0]) == type(list()):
			event_trained = BlendEvent([self.events_dict[name] for name in events[0]])
			event_trained.test_for_inheritance()
			for l in labels:
				for w in w_list:
					if w not in event_trained.normalized_w_tseries[l]:
						word_t_series = event_trained.calc_tseries(w, l) # calc. relevant freq, t_series
						print('Word and its tserie:', w, word_t_series)

		else:
			event_trained = self.events_dict[events[0]]

		if type(events[1]) == type(list()):
			event_test = BlendEvent([self.events_dict[name] for name in events[1]])
			event_test.test_for_inheritance()
			for l in labels:
				for w in w_list:
					if w not in event_test.normalized_w_tseries[l]:
						word_t_series = event_test.calc_tseries(w, l) # calc. relevant freq, t_series
						print('Word and its tserie:', w, word_t_series)
		else:
			event_test = self.events_dict[events[1]]

		print('Training Event:', event_trained.name)
		print('Test event:', event_test.name)
		self.calc_mean_median()
		euc_distances = {}
		

		#Prepare trained set	
		trained_X = event_trained.tweet_tseries[label][0] # get it from tweet time series. It is same for all events.
		tweet_count_plot = event_trained.tweet_tseries[label][1]

		graph_title = 'TweetCount'+ '-Train:'+self.list_to_str(events[0])+'\nTest:'+self.list_to_str(events[1])+'\nWCount:'+str(len(w_list))+'-minutForFrame:'+str(minuteForFrame)+ '-DayCount:'+str(dayCount) + '-normalized'
		file_name = 'TweetCount'+ '-Train:'+self.list_to_str(events[0])+'\nTest:'+self.list_to_str(events[1])+'\nWCount:'+str(len(w_list))+'-minutForFrame:'+str(minuteForFrame)+ '-DayCount:'+str(dayCount)+'-normalized'
		x_label = 'Hours Before an Event'
		y_label = 'Tweet Count'
		self.plot_tserie_list(trained_X, [tweet_count_plot] , ['TweetCount'], graph_title, x_label, y_label, file_name)

		graph_title = 'Mean Abs. Err'+ '-Train:'+self.list_to_str(events[0])+'\nTest:'+self.list_to_str(events[1])+'\nWCount:'+str(len(w_list))+'-minutForFrame:'+str(minuteForFrame)+ '-DayCount:'+str(dayCount) + '-normalized'
		file_name = 'Mean Abs. Err'+ '-Train:'+self.list_to_str(events[0])+'\nTest:'+self.list_to_str(events[1])+'\nWCount:'+str(len(w_list))+'-minutForFrame:'+str(minuteForFrame)+ '-DayCount:'+str(dayCount) + '-normalized'
		x_label = 'Hours Before an Event'
		y_label = 'Root Mean Square Error'

		euc_distances_sum = []
		test_seq = []
		square_roots = []
		square_roots_mean = []
		square_roots_median = []

		for sample_count in range(1, len(trained_X)+1):
			#print('Sample Count:', sample_count)
			#print('Len Trained X:',len(trained_X))

			#len of euc_distances_sum should be same count with the sequences count at this sample size.
			euc_distances_sum = [(1111,0)] * (1+len(trained_X)-sample_count) #initialization needed for sum
			
			for w in w_list:
				trained_Y = event_trained.normalized_w_tseries[label][w] # this should produce more balanced results.
				trained = [(a,b) for a, b in zip(trained_X, trained_Y)]
				trained = list(reversed(trained)) # Time was reversed in the normal array. Therefore reverse for the normal timeline with the test data.
				#print('Len trained_Y:', len(trained_Y))
				#print('Len trained:', len(trained))
				
				x=0
				trained_sub_seq = []
				for t in trained:
					temp_sub_sq = trained[x:x+sample_count] #create subsequences of the length of observed test data
					if len(temp_sub_sq) == sample_count:
						trained_sub_seq.append(temp_sub_sq)
					else:
						break
					x +=1

				#print('Trained sub seq:')
				#print(*trained_sub_seq, sep='\n')

				test_Y = event_test.normalized_w_tseries[label][w]
				test_Y = list(reversed(test_Y[:len(trained)])) #test_Y, when not smoothed, is longer be careful
				test_seq = test_Y[:sample_count]
				euc_distance_w = [] # Go clean for the next word

				for temp_sub_seq in trained_sub_seq:
				#Calc euc. distance and add it as a tuple with the last time point of this sequence. for this subsequence
					euc_distance_w.append((temp_sub_seq[-1][0],sqrt(math.fsum([(a-b[1])**2 if a-b[1] != 0 else 0 for a, b in zip(test_seq, temp_sub_seq)]))))
					if len(test_seq) != len(temp_sub_seq):
						print('test sequence and sub sequence from the training should match in length.Now:', len(test_seq), len(temp_sub_seq))
						exit()
				# Add the euc_dist of this word at to relevant time slot by preserving relevant time.
				#print('EucDistFor:', w, ':', euc_distance_w)
				if len(euc_distance_w) != len(euc_distances_sum):
					print('euc distance_w and euc_distances_sum should be equal.Now:',len(euc_distance_w), len(euc_distances_sum))
					exit()
				euc_distances_sum = [(b[0], math.fsum([a[1],b[1]])) for a, b in zip(euc_distances_sum, euc_distance_w)] # Add current euclidian values to the sum
				#print('EucDistSum:', euc_distances_sum)
				
				
			print('--EucDistForTheseObservations:', euc_distances_sum)
			smallest_euc = min([a[1] for a in euc_distances_sum])
			print('SmallestEuc:', smallest_euc )

			matched_times = []
			for dist_tuple in euc_distances_sum:
				if numpy.allclose(dist_tuple[1], smallest_euc ):
					matched_times.append(dist_tuple[0])

			prediction = numpy.mean(matched_times)
			print('matchedTimes:', matched_times, 'AverageTime:', prediction)

			actual = trained[:sample_count][-1][0] # first element of last tuple of this tuple sequence
			print('Actual time to the event:', actual)

			square_err_predict = abs(actual - prediction)
			square_err_mean = abs(actual-self.mean_of_tweets)
			square_err_median = abs(actual - self.median_of_tweets)
			print('Error of Prediction:',square_err_predict)

			square_err_predict_list.append(square_err_predict)
			square_err_mean_list.append(square_err_mean)
			square_err_median_list.append(square_err_median)

			#print('Mean absolute percentage error:', numpy.mean(square_roots)) # right ?

			mean_square_err_predict = numpy.mean(square_err_predict_list)
			mean_square_err_mean = numpy.mean(square_err_mean_list)
			mean_square_err_median = numpy.mean(square_err_median_list)

			print('Mean square error:', mean_square_err_predict)
			print('Baseline - Mean:', mean_square_err_mean)
			print('Baseline - Median:', mean_square_err_median)

			mean_sq_err_predict_l.append(mean_square_err_predict)
			mean_sq_err_mean_l.append(mean_square_err_mean)
			mean_sq_err_median_l.append(mean_square_err_median)



			print('**-Next Obs.-**:Finished Sample Count:', sample_count)
		mean_list = [mean_sq_err_predict_l, mean_sq_err_mean_l, mean_sq_err_median_l, square_err_predict_list]
		mean_list = [list(reversed(a)) for a in mean_list]
		self.plot_tserie_list(trained_X, mean_list , ['Mean Absolute Error', 'mean', 'median','Absolute Error'], graph_title, x_label, y_label, file_name)

	def calc_euc_dist_w_list_normalized_random(self, w_list, labels, events, minuteForFrame, dayCount):
		'First event is training, the second test.Later adapt it to fist n-1 training, n. is test'
		"""
		  -First label should be before for now.
		  -Since the X axes is same we do not take it into account
		  -First event training second is test
		  -

		  Questions:
		     1- Should I normalize scores for trained and test lists
		"""
		
		label = labels[0]
		square_err_predict_list = []
		square_err_mean_list = []
		square_err_median_list = []

		mean_sq_err_predict_l = []
		mean_sq_err_mean_l = []
		mean_sq_err_median_l = []

		for name, event in self.events_dict.items():
			for l in labels:
				for w in w_list:
					if w not in event.normalized_w_tseries[l]:
						word_t_series = event.calc_tseries(w, l, minuteForFrame, dayCount) # calc. relevant freq, t_series
						#print('Word and its tserie:', w, word_t_series)

		if type(events[0]) == type(list()):
			event_trained = BlendEvent([self.events_dict[name] for name in events[0]])
			event_trained.test_for_inheritance()
			for l in labels:
				for w in w_list:
					if w not in event_trained.normalized_w_tseries[l]:
						word_t_series = event_trained.calc_tseries(w, l) # calc. relevant freq, t_series
						#print('Word and its tserie:', w, word_t_series)

		else:
			event_trained = self.events_dict[events[0]]

		if type(events[1]) == type(list()):
			event_test = BlendEvent([self.events_dict[name] for name in events[1]])
			event_test.test_for_inheritance()
			for l in labels:
				for w in w_list:
					if w not in event_test.normalized_w_tseries[l]:
						word_t_series = event_test.calc_tseries(w, l) # calc. relevant freq, t_series
						#print('Word and its tserie:', w, word_t_series)
		else:
			event_test = self.events_dict[events[1]]

		print('Training Event:', event_trained.name)
		print('Test event:', event_test.name)
		self.calc_mean_median()
		euc_distances = {}

		trained_X = event_trained.tweet_tseries[label][0] # get it from tweet time series. It is same for all events.
		# tweet_count_plot = event_trained.tweet_tseries[label][1]

		# graph_title = 'TweetCount'+ '-Trn:'+self.list_to_str(events[0])+'\nTst:'+self.list_to_str(events[1])+'\nWC:'+str(len(w_list))+'-minFrame:'+str(minuteForFrame)+ '-DayC:'+str(dayCount) + '-norm' + '-rand'
		# file_name = 'TweetCount'+ '-Trn:'+self.list_to_str(events[0])+'Tst:'+self.list_to_str(events[1])+'WC:'+str(len(w_list))+'-minFrame:'+str(minuteForFrame)+ '-DayC:'+str(dayCount)+'-norm'+'-rand'
		# x_label = 'Hours Before an Event'
		# y_label = 'Tweet Count'
		# self.plot_tserie_list(trained_X, [tweet_count_plot] , ['TweetCount'], graph_title, x_label, y_label, file_name)

		
		euc_distances_sum = []
		test_seq = []
		

		for sample_count in range(1, len(trained_X)+1):
			row_err_predict_l = []
			row_err_mean_l = []
			row_err_median_l = []
			abs_err_predict_l = []
			abs_err_mean_l = []
			abs_err_median_l = []

			for i in range(0, (1+len(trained_X)-sample_count)):
				euc_distances_sum = [(1111,0)] * (1+len(trained_X)-sample_count) #initialization needed for sum
				
				for w in w_list:
					trained_Y = event_trained.normalized_w_tseries[label][w] # this should produce more balanced results.
					trained = [(a,b) for a, b in zip(trained_X, trained_Y)]
					trained = list(reversed(trained)) # Time was reversed in the normal array. Therefore reverse for the normal timeline with the test data.
					trained_sub_seq = self.get_sub_seqeunces(sample_count, trained)
					
					test_Y = event_test.normalized_w_tseries[label][w]
					test_Y = [(a,b) for a, b in zip(trained_X, test_Y)]
					test_Y = list(reversed(test_Y[:len(trained)])) #test_Y, when not smoothed, is longer be careful
					test_sub_seq = self.get_sub_seqeunces(sample_count, test_Y)
					
					euc_distance_w = [] # Go clean for the next word
					for temp_sub_seq in trained_sub_seq:
					#Calc euc. distance and add it as a tuple with the last time point of this sequence. for this subsequence
						euc_distance_w.append((temp_sub_seq[-1][0],sqrt(math.fsum([(a[1]-b[1])**2 if not numpy.allclose(a[1], b[1]) else 0 for a, b in zip(test_sub_seq[i], temp_sub_seq)]))))
						
					euc_distances_sum = [(b[0], math.fsum([a[1],b[1]])) for a, b in zip(euc_distances_sum, euc_distance_w)] # Add current euclidian values to the sum
				

				print('--EucDistForTheseObservations:', euc_distances_sum)
				smallest_euc = min([a[1] for a in euc_distances_sum])
				print('SmallestEuc:', smallest_euc )

				matched_times = []
				for dist_tuple in euc_distances_sum:
					if numpy.allclose(dist_tuple[1], smallest_euc ):
						matched_times.append(dist_tuple[0])

				prediction = numpy.mean(matched_times)
				print('matchedTimes:', matched_times, 'AverageTime:', prediction)

				actual = test_sub_seq[i][-1][0] # first element of last tuple of this tuple sequence
				print('Actual time to the event:', actual)

			
				row_err_predict_l.append(prediction - actual)
				row_err_mean_l.append(self.mean_of_tweets - actual)
				row_err_median_l.append(self.median_of_tweets - actual)
				print('Row Error of Prediction:',row_err_predict_l[-1])


				abs_err_predict_l.append(abs(prediction-actual))
				abs_err_mean_l.append(abs(self.mean_of_tweets-actual))
				abs_err_median_l.append(abs(self.median_of_tweets-actual))
				print('Absolute Error of Prediction:',abs_err_predict_l[-1])


				print('**-Next Obs.-**:Finished Sample Count:', sample_count)
			mean_list = [row_err_predict_l, row_err_median_l, row_err_mean_l]
			mean_list = [list(reversed(a)) for a in mean_list]
			graph_title = 'Row Err'+ '-Trn:'+self.list_to_str(events[0])+'\nTst:'+self.list_to_str(events[1])+'\nWC:'+str(len(w_list))+'-minFrame:'+str(minuteForFrame)+ '-DayC:'+str(dayCount)+'-SampleC:'+str(sample_count) + '-norm'+'rand'
			file_name = 'Row Err'+ '-Trn:'+self.list_to_str(events[0])+'Tst:'+self.list_to_str(events[1])+'WC:'+str(len(w_list))+'-minFrame:'+str(minuteForFrame)+ '-DayC:'+str(dayCount) +'-SampleC:'+str(sample_count) + '-norm' + '-rand'
			x_label = 'Hours Before an Event'
			y_label = 'Row Error'
			self.plot_tserie_list(trained_X, mean_list , ['Row error', 'median', 'mean'], graph_title, x_label, y_label, file_name)

	def get_sub_seqeunces(self, sample_count, complete_list):
		x=0
		all_sub_seq = []
		for t in complete_list:
			temp_sub_seq = complete_list[x:x+sample_count]
			if len(temp_sub_seq) == sample_count:
				all_sub_seq.append(temp_sub_seq)
			else:
				break
			x += 1
		return all_sub_seq

	def list_to_str(self, list_str):
		all_str = ''
		for item in list_str:
			all_str += item+'-'
		
		return all_str

	def calc_euc_dist_w_list(self, w_list, labels, events, minuteForFrame, dayCount):
		'First event is training, the second test.Later adapt it to fist n-1 training, n. is test'
		"""
		  -First label should be before for now.
		  -Since the X axes is same we do not take it into account
		  -First event training second is test

		  Questions:
		     1- Should I normalize scores for trained and test lists
		"""
		
		label = labels[0]
		square_err_predict_list = []
		square_err_mean_list = []
		square_err_median_list = []

		mean_sq_err_predict_l = []
		mean_sq_err_mean_l = []
		mean_sq_err_median_l = []

		for name, event in self.events_dict.items():
			for l in labels:
				for w in w_list:
					if w not in event.normalized_w_tseries[l]:
						word_t_series = event.calc_tseries(w, l, minuteForFrame, dayCount) # calc. relevant freq, t_series
						print('Word and its tserie:', w, word_t_series)

		if type(events[0]) == type(list()):
			event_trained = BlendEvent([self.events_dict[name] for name in events[0]])
			event_trained.test_for_inheritance()
			for l in labels:
				for w in w_list:
					if w not in event_trained.normalized_w_tseries[l]:
						word_t_series = event_trained.calc_tseries(w, l) # calc. relevant freq, t_series
						print('Word and its tserie:', w, word_t_series)

		else:
			event_trained = self.events_dict[events[0]]

		if type(events[1]) == type(list()):
			event_test = BlendEvent([self.events_dict[name] for name in events[1]])
			event_test.test_for_inheritance()
			for l in labels:
				for w in w_list:
					if w not in event_test.normalized_w_tseries[l]:
						word_t_series = event_test.calc_tseries(w, l) # calc. relevant freq, t_series
						print('Word and its tserie:', w, word_t_series)
		else:
			event_test = self.events_dict[events[1]]

		
		print('Training Event:', event_trained.name)
		print('Test event:', event_test.name)
		self.calc_mean_median()
		euc_distances = {}
		

		#Prepare trained set	
		trained_X = event_trained.tweet_tseries[label][0][:-2] # get it from tweet time series. It is same for all events.
		tweet_count_plot = event_trained.tweet_tseries[label][1][:-2]

		graph_title = 'TweetCount'+ '-Train:'+self.list_to_str(events[0])+'\nTest:'+self.list_to_str(events[1])+'\nWCount:'+str(len(w_list))+'-minutForFrame:'+str(minuteForFrame)+ '-DayCount:'+str(dayCount)
		file_name = 'TweetCount'+ '-Train:'+self.list_to_str(events[0])+'Test:'+self.list_to_str(events[1])+'WCount:'+str(len(w_list))+'-minutForFrame:'+str(minuteForFrame)+ '-DayCount:'+str(dayCount)
		x_label = 'Hours Before an Event'
		y_label = 'Tweet Count'
		self.plot_tserie_list(trained_X, [tweet_count_plot] , ['TweetCount'], graph_title, x_label, y_label, file_name)

		graph_title = 'Mean Abs. Err'+ '-Train:'+self.list_to_str(events[0])+'\nTest:'+self.list_to_str(events[1])+'\nWCount:'+str(len(w_list))+'-minutForFrame:'+str(minuteForFrame)+ '-DayCount:'+str(dayCount)
		file_name = 'Mean Abs. Err'+ '-Train:'+self.list_to_str(events[0])+'Test:'+self.list_to_str(events[1])+'WCount:'+str(len(w_list))+'-minutForFrame:'+str(minuteForFrame)+ '-DayCount:'+str(dayCount)
		x_label = 'Hours Before an Event'
		y_label = 'Root Mean Square Error'

		euc_distances_sum = []
		test_seq = []
		square_roots = []
		square_roots_mean = []
		square_roots_median = []

		for sample_count in range(1, len(trained_X)+1):
			#print('Sample Count:', sample_count)
			#print('Len Trained X:',len(trained_X))

			#len of euc_distances_sum should be same count with the sequences count at this sample size.
			euc_distances_sum = [(1111,0)] * (1+len(trained_X)-sample_count) #initialization needed for sum
			
			for w in w_list:
				trained_Y = event_trained.smoothed_w_tseries[label][w] # this should produce more balanced results.
				trained = [(a,b) for a, b in zip(trained_X, trained_Y)]
				trained = list(reversed(trained)) # Time was reversed in the normal array. Therefore reverse for the normal timeline with the test data.
				#print('Len trained_Y:', len(trained_Y))
				#print('Len trained:', len(trained))
				
				x=0
				trained_sub_seq = []
				for t in trained:
					temp_sub_sq = trained[x:x+sample_count] #create subsequences of the length of observed test data
					if len(temp_sub_sq) == sample_count:
						trained_sub_seq.append(temp_sub_sq)
					else:
						break
					x +=1

				#print('Trained sub seq:')
				#print(*trained_sub_seq, sep='\n')

				test_Y = event_test.smoothed_w_tseries[label][w]
				test_Y = list(reversed(test_Y[:len(trained)])) #test_Y, when not smoothed, is longer be careful
				test_seq = test_Y[:sample_count]
				euc_distance_w = [] # Go clean for the next word

				for temp_sub_seq in trained_sub_seq:
				#Calc euc. distance and add it as a tuple with the last time point of this sequence. for this subsequence
					euc_distance_w.append((temp_sub_seq[-1][0],sqrt(math.fsum([(a-b[1])**2 if a-b[1] != 0 else 0 for a, b in zip(test_seq, temp_sub_seq)]))))
					if len(test_seq) != len(temp_sub_seq):
						print('test sequence and sub sequence from the training should match in length.Now:', len(test_seq), len(temp_sub_seq))
						exit()
				# Add the euc_dist of this word at to relevant time slot by preserving relevant time.
				#print('EucDistFor:', w, ':', euc_distance_w)
				if len(euc_distance_w) != len(euc_distances_sum):
					print('euc distance_w and euc_distances_sum should be equal.Now:',len(euc_distance_w), len(euc_distances_sum))
					exit()
				euc_distances_sum = [(b[0], math.fsum([a[1],b[1]])) for a, b in zip(euc_distances_sum, euc_distance_w)] # Add current euclidian values to the sum
				#print('EucDistSum:', euc_distances_sum)
				
				
			print('--EucDistForTheseObservations:', euc_distances_sum)
			smallest_euc = min([a[1] for a in euc_distances_sum])
			print('SmallestEuc:', smallest_euc )

			matched_times = []
			for dist_tuple in euc_distances_sum:
				if numpy.allclose(dist_tuple[1], smallest_euc ):
					matched_times.append(dist_tuple[0])

			prediction = numpy.mean(matched_times)
			print('matchedTimes:', matched_times, 'AverageTime:', prediction)

			actual = trained[:sample_count][-1][0] # first element of last tuple of this tuple sequence
			print('Actual time to the event:', actual)

			square_err_predict = abs(actual - prediction)
			square_err_mean = abs(actual-self.mean_of_tweets)
			square_err_median = abs(actual - self.median_of_tweets)
			print('Error of Prediction:',square_err_predict)

			square_err_predict_list.append(square_err_predict)
			square_err_mean_list.append(square_err_mean)
			square_err_median_list.append(square_err_median)

			#print('Mean absolute percentage error:', numpy.mean(square_roots)) # right ?

			mean_square_err_predict = numpy.mean(square_err_predict_list)
			mean_square_err_mean = numpy.mean(square_err_mean_list)
			mean_square_err_median = numpy.mean(square_err_median_list)

			print('Mean square error:', mean_square_err_predict)
			print('Baseline - Mean:', mean_square_err_mean)
			print('Baseline - Median:', mean_square_err_median)

			mean_sq_err_predict_l.append(mean_square_err_predict)
			mean_sq_err_mean_l.append(mean_square_err_mean)
			mean_sq_err_median_l.append(mean_square_err_median)



			print('**-Next Obs.-**:Finished Sample Count:', sample_count)
		mean_list = [mean_sq_err_predict_l, mean_sq_err_mean_l, mean_sq_err_median_l, square_err_predict_list]
		mean_list = [list(reversed(a)) for a in mean_list]
		self.plot_tserie_list(trained_X, mean_list , ['Mean Absolute Error', 'mean', 'median','Absolute Error'], graph_title, x_label, y_label, file_name)

	
	def calc_mean_median(self):
		label = 'before'
		product_sum = 0
		tweet_count = 0
		e_tserie_list = []
		e_tserie = ([],[])

		for name, event in self.events_dict.items():
			e_tserie = (event.tweet_tseries[label][0], event.tweet_tseries[label][1])
			e_tserie_list.append(e_tserie)
			
			tweet_count += sum(e_tserie[1])
			product_sum += sum([a*b for a, b in zip(e_tserie[0], e_tserie[1])])

		mean = product_sum/tweet_count
		print('Sum of products:',product_sum,'All Tweet count:', tweet_count, 'Mean:', mean )

		i = 1
		median_tweet_count = tweet_count/2
		median = 0
		sum_tweets = 0
		print(e_tserie_list)
		while sum_tweets < median_tweet_count:
			for ts_tuple in e_tserie_list:
				sum_tweets += ts_tuple[1][-i]
				median = ts_tuple[0][-i]
			i +=1

		print('median tweet count is:', median_tweet_count)
		print('sum tweet count, median taken from:', sum_tweets)
		print('median hour:', median)

		self.mean_of_tweets = mean
		self.median_of_tweets = median
		return (self.mean_of_tweets, self.median_of_tweets)

	def plot_tserie_list(self, x_axe, y_axes_list, plot_names, graphTitle, x_label, y_label, file_name ):
		line_colors=['blue', 'green','red', 'cyan', 'magenta', 'yellow', 'black', 'white']
		line_style = ['--']
		line_markers = []
		
		fig = matplotlib.pyplot.figure(figsize=(25,20)) #  fig size should vary according day*24
		matplotlib.pyplot.grid(True) # ???
		font = {'weight':'bold', 'size':22}
		matplotlib.rc('font', **font)
		matplotlib.rc('lines', lw=4)		
		matplotlib.pyplot.xlim(x_axe[-1], 0)
		
		i = 0
		for y_axe in y_axes_list:
			print('Len of X and Y axe:', len(x_axe), len(y_axe))
			print('X and Y axe:', x_axe, y_axe)
			plot(x_axe[:len(y_axe)], y_axe, color= line_colors[i], label=plot_names[i])
			i += 1
		
		legend(loc='upper right', fontsize=22)
		ylabel(y_label,fontsize = 30, fontweight='bold')
		xlabel('Hours Before Event', fontsize = 30, fontweight='bold')
		matplotlib.pyplot.title(graphTitle)
		fig.savefig('/home/ali-hurriyetoglu/Desktop/Graphs/Euc/'+file_name+'.png',format='png', facecolor='w',edgecolor='w', orientation='portrait', linewidth=50.0)

		fig.clf()


	def count_words(self):
		"Count words for each category"
		self.all_tweet_count = 0
		self.all_before_word_count = 0
		self.all_during_word_count = 0
		self.all_after_word_count = 0
		tweet_count_tweaja_before = 0 #temp
		tweet_count_tweaja_during = 0
		tweet_count_tweaja_after = 0

		for t in self.tf.tweets:

			self.all_tweet_count +=1
			self.counter_events[t.event] += 1 # count tweets for each event
			
			if t.event in self.events: #for this event

				if t.get_label() == 'before':

					self.before_tweets.append(t)

					tweet_count_tweaja_before += 1 # temp

					for w in list(set(t.get_wordsequence())): # count just one time if this word occurs in a tweet
						self.counter_before[w] += 1
						self.all_before_word_count += 1
						
				if t.get_label() == 'during':

					tweet_count_tweaja_during += 1 # temp

					for w in t.get_wordsequence():
						self.counter_during[w] += 1
						self.all_during_word_count += 1

				if t.get_label() == 'after':

					tweet_count_tweaja_after += 1 # temp

					for w in t.get_wordsequence():
						self.counter_after[w] += 1
						self.all_after_word_count += 1
	
		
		print("Twente Ajax Before, During, After, Sum Tweet Count:", tweet_count_tweaja_before, tweet_count_tweaja_during, \
		   tweet_count_tweaja_after, tweet_count_tweaja_before+tweet_count_tweaja_during+tweet_count_tweaja_after)
	
		self.all_words_counter = self.counter_before + self.counter_during + self.counter_after
		self.word_list = list(self.all_words_counter)

	def calc_words_freq(self):
		for w in self.word_list:
			if (self.counter_before[w] + self.counter_during[w] + self.counter_after[w]) > 0:

				#self.freq_before_dict[w] = self.counter_before[w]/self.all_before_word_count
				
				self.freq_before_dict[w] = self.counter_before[w]/len(self.before_tweets) # freq according tweet count.
				self.freq_during_dict[w] = self.counter_during[w]/self.all_during_word_count
				self.freq_after_dict[w] = self.counter_during[w]/self.all_after_word_count


	def calc_words_relative_freq(self): #make it generic for all categories, consider having classes for each temporal category.
		"Calculate relative frequency  of all words and store them in dictionaries separately"
		"""
			Relative frequency of Words that occur just in one category calculated as their count.
		"""

		# calculate frequency of before words and compare with other occurrence freq in other categories.
		for w in self.word_list:
		    
			if (self.freq_during_dict[w] + self.freq_after_dict[w]) > 0: # otherwise it gives division by zero error.
				self.relative_freq_before_dict[w] = self.freq_before_dict[w]/(self.freq_during_dict[w]+self.freq_after_dict[w]) 
			else :
				self.relative_freq_before_dict[w] = self.counter_before[w]/2 #if it occurs just in before category give the count divided by count of other categories

			if (self.freq_before_dict[w] + self.freq_after_dict[w]) > 0: # otherwise it gives division by zero error.
				self.relative_freq_during_dict[w] = self.freq_during_dict[w]/(self.freq_before_dict[w]+self.freq_after_dict[w]) 
			else :
				self.relative_freq_during_dict[w] = self.counter_during[w]/2 

			if (self.freq_before_dict[w] + self.freq_during_dict[w]) > 0: # otherwise it gives division by zero error.
				self.relative_freq_after_dict[w] = self.freq_after_dict[w]/(self.freq_before_dict[w] + self.freq_during_dict[w]) 
			else :
				self.relative_freq_after_dict[w] = self.counter_after[w]/2

	def get_sorted_freq(self):
		print(self.print_sorted(self.freq_before_dict, self.counter_before))
		input("Press Enter ..-----------------: End Before")

		print(self.print_sorted(self.freq_during_dict, self.counter_during))
		input("Press Enter .. ----------------: End During")
		
		print(self.print_sorted(self.freq_after_dict, self.counter_after))
		input("Press Enter .. ----------------: End After")


	def get_sorted_rel_freq(self):#adjust this method to be calleble for different dicts and different thresholds
		self.print_sorted(self.relative_freq_before_dict, self.counter_before)
		input("Press Enter ..-----------------: End Before")
		
		self.print_sorted(self.relative_freq_during_dict, self.counter_during)
		input("Press Enter .. ----------------: End During")
		
		self.print_sorted(self.relative_freq_after_dict, self.counter_after)
		input("Press Enter .. ----------------: End After")


	def sort_dict(self, d):
		return sorted(d.items(), key= operator.itemgetter(1), reverse= True) # Highest value first, descending

	def print_sorted(self, d, c): #d:dict, c:counter
		values = sorted(d.items(), key= operator.itemgetter(1), reverse= True)
		
		i = 1
		for k, v in values:
			print(k, v, c[k])
			i += 1

			if i % 50 == 0:
				input("Press Enter to Continue...")
				print('..................................')

	def print_rest_words(self, counter_rest=None):#words that do not occur in sonar, and eliminated.
		print("Count of words in Rest words in before - during - after")

		for w, c in self.word_list_rest.most_common():
			if w[0] != '@' and len(w)>1:
				print(w, "sum:", self.word_list_rest[w], "b:",self.counter_before_rest[w], "d:", self.counter_during_rest[w], "a:", self.counter_after_rest[w])

		print("End of rest words list")

	def calc_time_list_for_tweets(self):
		time_list = []
		for t in self.before_tweets:
			time_list.append(t.time)
		return time_list

	def calc_time_list_for_word(self, w): # Adapt it to do this for all events, not all tweets
		time_list = []
		for t in self.before_tweets:
			if w in t.get_wordsequence():
				time_list.append(t.time)
				#break;
		return time_list

	def calc_time_list_for_time_intervals(self, time_l_for_a_w, minForPeriod, day_count):
		xlabels = []
		xvalues = []
		tweetCount = 0
		t_delta = 0

		seconds_back = 60*60*24*day_count

		while t_delta < seconds_back:
			count = 0

			for e in self.events:
				
				match_time = self.event_times[self.events.index(e)] #+ datetime.timedelta(0, 60*60*24*day_count) # end calculation after day_count days
				print('Match and the time:', e, match_time, '--> t_delta:', t_delta)
				
				interval = match_time - datetime.timedelta(0, t_delta) # start calculation before day_count days

				before_interval = interval - datetime.timedelta(0,60*minForPeriod) # 15 min * time_interval	
				
				timespan= match_time - datetime.timedelta(seconds_back)

				for t in time_l_for_a_w:#list is ordered, break the loop if t > match_time  : implement
					if t > match_time:
						break;
					else:
						if t < match_time and t > timespan:
							if t >= before_interval and t < interval:
								count += 1
			
			xvalues.append(count)
			xlabels.append(0-t_delta/3600) # Give minutes before a match
			t_delta = t_delta + 60*minForPeriod

		return (xlabels, xvalues)
		
	def running_average(self, t_series_l):
		"returned list has 2 elements less than normal one, make the change in plotting for the other list"
		"? weights should be 4 2 1 or 1 2 4 ?, is the order of current, next1 and next2 right ?"
		print(t_series_l)

		r_average = []
		av = 0
		divide_by = 7 # 3 elems + 1 for the weight of the middle one = 4
		for current, next1, next2 in self.neighborhood(t_series_l):
			av=(4*current + 2*next1+next2)/divide_by
			print(current,'--',next1,'--',next2)
			
			r_average.append(av)

		r_average.append((4*t_series_l[-1] + 2*t_series_l[-2]+t_series_l[-3])/divide_by)

		return r_average

	def neighborhood(self, iterable):
		iterator = iter(iterable)
		print(iterator)
		
		current = iterator.__next__()  # throws StopIteration if empty.
		next1 = iterator.__next__()
		next2 = iterator.__next__()
		for next in iterator:
			yield (current, next1, next2)
			current = next1
			next1 = next2
			next2 = next

	def plot_word(self, w, minutes_for_time_period, day_back_count, withTweetCount, is_running_average): #use n to indicate number of words to make plot for
		"count, freq methods should be enabled in the constructor before this start"
		line_colors=['blue', 'green','red', 'cyan', 'magenta', 'yellow', 'black', 'white']
		line_style = ['--']
		line_markers = []
		plotted_words = w
		smoothed_str = ''

		fig = matplotlib.pyplot.figure(figsize=(25,20)) #  fig size should vary according day*24
		matplotlib.pyplot.grid(True) # ???

		font = {'weight':'bold', 'size':22}
		matplotlib.rc('font', **font)
		matplotlib.rc('lines', lw=4)

		if is_running_average:
			smoothed_str += 'Smoothed'
		else:
			smoothed_str += 'Not Smoothed'

		matplotlib.pyplot.title('The Word: '+w+', '+str(minutes_for_time_period)+' minutes time frame, '+str(day_back_count)+' days back, '+ smoothed_str)
		matplotlib.pyplot.xlim((0-24*day_back_count), 0)
		#matplotlib.pyplot.ylim(0,1)
		xticks( [-192,-168,-144,-120,-96,-72, -48,-24,0]) # write for range of days, add an element multiplied by 24.otherwise when the days changed; it will be problem.
		#yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5])
		#yticks([0, 0.05, 0.1,0.15, 0.2,0.25, 0.3,0.35, 0.4,0.45, 0.5,0.55, 0.6,0.65, 0.7,0.75, 0.8,0.85, 0.9])

		i=0
		if withTweetCount == True:
			time_list_for_tweets = self.calc_time_list_for_tweets()

			axes = self.calc_time_list_for_time_intervals(sorted(time_list_for_tweets), minutes_for_time_period, day_back_count) # product with 15 min, and for 8 days
			newTweetCount = []

			newTweetCount = axes[1]

			#plot(axes[0], newTweetCount, color= line_colors[0])
			i += 1
		
		time_list_for_a_word = self.calc_time_list_for_word(w)

		axes = self.calc_time_list_for_time_intervals(sorted(time_list_for_a_word), minutes_for_time_period, day_back_count)
		
		w_time_per_count = []
		w_time_per_count=[a/b for  a, b in zip(axes[1], newTweetCount)]

		if is_running_average == True:
			w_time_per_count = self.running_average(w_time_per_count)
			plotted_words += '-rAveraged'
			axes_0 = axes[0][:-3] # running average make the lists shorter
		else:
			axes_0 = axes[0]

		
		print('Length of axes_0 and w_time_per_count', len(axes_0), len(w_time_per_count))
		plot(axes_0, w_time_per_count, color=line_colors[i], label=w)

		w_mean_freq_list = [self.freq_before_dict[w]] * len(w_time_per_count)

		plot(axes_0, w_mean_freq_list, color=line_colors[i+1], label = 'mean of:'+w) # straight line, mean for this word.
		plotted_words += '-withMeanLine'
		print('Mean Line is:', line_colors[i+1])

		#calc. standard deviation
		w_st_power_diff = [((a-b)**2) for a, b in zip(w_mean_freq_list, w_time_per_count)]
		w_st_dev=sqrt(math.fsum(w_st_power_diff)/len(w_mean_freq_list))
		w_st_dev_list = [w_st_dev] * len(w_time_per_count)

		mean_plus_stDev = [a+b for a, b in zip(w_mean_freq_list, w_st_dev_list)]
		plot(axes_0, mean_plus_stDev, color=line_colors[0], label = 'St. Dev of:'+w) # straight line, mean for this word.
		plotted_words += '-with2StDevLine'
		print('St. Dev is:', line_colors[i])

		mean_plus_stDev_2 = [a+(2*b) for a, b in zip(w_mean_freq_list, w_st_dev_list)]
		plot(axes_0, mean_plus_stDev_2, color=line_colors[0]) # straight line, mean for this word.
		print('St. Dev is:', line_colors[0])

		legend(loc='upper right', fontsize=22)
		ylabel('Relative Frequency',fontsize = 30, fontweight='bold')
		xlabel('Hours Before Event', fontsize = 30, fontweight='bold')
		fig.savefig('/home/ali-hurriyetoglu/Desktop/Graphs/'+plotted_words+'-'+str(minutes_for_time_period)+'minPeriod'+'-'+str(day_back_count)+'daysBack'+'.png',format='png', facecolor='w',edgecolor='w', orientation='portrait', linewidth=50.0)

	def plot_word_event_based(self, word, label, event_name, minute_time_period, day_count): #use n to indicate number of words to make plot for
		"""
		"""
		line_colors=['blue', 'green','red', 'cyan', 'magenta', 'yellow', 'black', 'white']
		line_style = ['--']
		line_markers = []
		plotted_words = word

		fig = matplotlib.pyplot.figure(figsize=(25,20)) #  fig size should vary according day*24
		matplotlib.pyplot.grid(True) # ???
		font = {'weight':'bold', 'size':22}
		matplotlib.rc('font', **font)
		matplotlib.rc('lines', lw=4)		
		matplotlib.pyplot.xlim((0-24*day_count), 0)
		xticks( [a*(-24) for a in reversed(range(0, day_count+1))] ) 
		
		event_obj = self.events_dict[event_name]
		if len(event_obj.tweets[label]) == 0:
			print(event_obj.name, label, '--> Does not have any Tweet, Exit !')
			exit()
		
		event_obj.calcFreq_for_word(word, label)
		
		axes = event_obj.calc_tseries(word, label, minute_time_period, day_count)
		axes_x0 = axes[0]
		axes_y1 = axes[1]

		plot(axes_x0, axes_y1, color=line_colors[2], label=word)
		plot(axes_x0, event_obj.w_mean_list[label][word], color=line_colors[1], label = 'mean of:'+word) # straight line, mean for this word.

		mean_plus_stDev = [a+b for a, b in zip(event_obj.w_mean_list[label][word], event_obj.w_stdev_list[label][word])]
		plot(axes_x0, mean_plus_stDev, color=line_colors[0], label = 'St. Dev of:'+word) # straight line, mean for this word.
		
		mean_plus_stDev_2 = [a+(2*b) for a, b in zip(event_obj.w_mean_list[label][word], event_obj.w_stdev_list[label][word])]
		plot(axes_x0, mean_plus_stDev_2, color=line_colors[0]) # straight line, mean for this word.
		
		legend(loc='upper right', fontsize=22)
		ylabel('Relative Frequency',fontsize = 30, fontweight='bold')
		xlabel('Hours Before Event', fontsize = 30, fontweight='bold')
		matplotlib.pyplot.title('Word:'+word+',Event:' +event_name+',TweetCount:'+str(len(event_obj.tweets[label]))+','+str(minute_time_period)+':minutes time frame, '+ \
			str(day_count)+' days back')
		fig.savefig('/home/ali-hurriyetoglu/Desktop/Graphs/'+plotted_words+'-Event:' +event_name+','+str(minute_time_period)+'minPeriod'+'-'+str(day_count)+'daysBack'+'.png',format='png', facecolor='w',edgecolor='w', orientation='portrait', linewidth=50.0)

	def plot_most_common_words_of_label_of_event(self, label, event_name, minute_time_period, day_count):
		"""
		 1- label should contain one element for now.
		 2- call one time for each event
		"""
		line_colors=['blue', 'green','red', 'cyan', 'magenta', 'yellow', 'black', 'white']
		line_style = ['--']
		line_markers = []
		
		fig = matplotlib.pyplot.figure(figsize=(25,20)) #  fig size should vary according day*24
		matplotlib.pyplot.grid(True) # ???
		font = {'weight':'bold', 'size':22}
		matplotlib.rc('font', **font)
		matplotlib.rc('lines', lw=4)		
		matplotlib.pyplot.xlim((0-24*day_count), 0)
		xticks( [a*(-24) for a in reversed(range(0, day_count+1))] ) 
		
		event_obj = self.events_dict[event_name]
		if len(event_obj.tweets[label]) == 0:
			print(event_obj.name, label, '--> Does not have any Tweet, Exit !')
			exit()
		

		i = 0

		for word, count in event_obj.words[label].most_common(500):

			# limit by most_common n words(above) or words that occur n times(below) 
			# if count == 1:
			# 	break

			plotted_words = word
			event_obj.calcFreq_for_word(word, label)
			axes = event_obj.calc_tseries(word, label, minute_time_period, day_count)
			axes_x0 = axes[0]
			axes_y1 = axes[1]

			plot(axes_x0, axes_y1, color=line_colors[2], label=word)
			plot(axes_x0, event_obj.w_mean_list[label][word], color=line_colors[1], label = 'mean of:'+word) # straight line, mean for this word.

			mean_plus_stDev = [a+b for a, b in zip(event_obj.w_mean_list[label][word], event_obj.w_stdev_list[label][word])]
			plot(axes_x0, mean_plus_stDev, color=line_colors[0], label = 'St. Dev of:'+word) # straight line, mean for this word.
			
			mean_plus_stDev_2 = [a+(2*b) for a, b in zip(event_obj.w_mean_list[label][word], event_obj.w_stdev_list[label][word])]
			plot(axes_x0, mean_plus_stDev_2, color=line_colors[0]) # straight line, mean for this word.
			
			legend(loc='upper right', fontsize=22)
			ylabel('Relative Frequency',fontsize = 30, fontweight='bold')
			xlabel('Hours Before Event', fontsize = 30, fontweight='bold')
			matplotlib.pyplot.title('Word:'+word+','+str(count)+' times,'+str(i)+' most freq'+',Event:' +event_name+',TweetCount:'+str(len(event_obj.tweets[label]))+','+str(minute_time_period)+':minutes time frame, '+ \
				str(day_count)+' days back')
			fig.savefig('/home/ali-hurriyetoglu/Desktop/Graphs/'+plotted_words+'-Event:' +event_name+','+str(minute_time_period)+'minPeriod'+'-'+str(day_count)+'daysBack'+'.png',format='png', facecolor='w',edgecolor='w', orientation='portrait', linewidth=50.0)
			fig.clf()

			i += 1
			print(str(i), word, event_obj.name)

	def plot_word_list_of_label_of_event(self, w_list, label, event_name, minute_time_period, day_count):
		"""
		 1- label should contain one element for now.
		 2- call one time for each event
		"""
		line_colors=['blue', 'green','red', 'cyan', 'magenta', 'yellow', 'black', 'white']
		line_style = ['--']
		line_markers = []
		
		fig = matplotlib.pyplot.figure(figsize=(25,20)) #  fig size should vary according day*24
		matplotlib.pyplot.grid(True) # ???
		font = {'weight':'bold', 'size':22}
		matplotlib.rc('font', **font)
		matplotlib.rc('lines', lw=4)		
		matplotlib.pyplot.xlim((0-24*day_count), 0)
		xticks( [a*(-24) for a in reversed(range(0, day_count+1))] ) 
		
		event_obj = self.events_dict[event_name]
		if len(event_obj.tweets[label]) == 0:
			print(event_obj.name, label, '--> Does not have any Tweet, Exit !')
			exit()
		

		i = 0

		for word in w_list:

			plotted_words = word
			axes = event_obj.calc_tseries(word, label, minute_time_period, day_count)
			axes_x0 = axes[0]
			axes_y1 = axes[1]

			plot(axes_x0, axes_y1, color=line_colors[2], label=word)
			plot(axes_x0, event_obj.w_mean_list[label][word], color=line_colors[1], label = 'mean of:'+word) # straight line, mean for this word.

			mean_plus_stDev = [a+b for a, b in zip(event_obj.w_mean_list[label][word], event_obj.w_stdev_list[label][word])]
			plot(axes_x0, mean_plus_stDev, color=line_colors[0], label = 'St. Dev of:'+word) # straight line, mean for this word.
			
			mean_plus_stDev_2 = [a+(2*b) for a, b in zip(event_obj.w_mean_list[label][word], event_obj.w_stdev_list[label][word])]
			plot(axes_x0, mean_plus_stDev_2, color=line_colors[0]) # straight line, mean for this word.
			
			legend(loc='upper right', fontsize=22)
			ylabel('Relative Frequency',fontsize = 30, fontweight='bold')
			xlabel('Hours Before Event', fontsize = 30, fontweight='bold')
			matplotlib.pyplot.title('Word:'+word+','+str(event_obj.words[label][word])+' times,'+str(i)+' most freq'+',Event:' +event_name+',TweetCount:'+str(len(event_obj.tweets[label]))+','+str(minute_time_period)+':minutes time frame, '+ \
				str(day_count)+' days back')
			fig.savefig('/home/ali-hurriyetoglu/Desktop/Graphs/'+plotted_words+str(event_obj.words[label][word])+' times,'+str(i)+'. most freq'+'-Event:' +event_name+','+str(minute_time_period)+'minPeriod'+'-'+str(day_count)+'daysBack'+'.png',format='png', facecolor='w',edgecolor='w', orientation='portrait', linewidth=50.0)
			
			i += 1
			print(str(i), word, event_obj.name)

			fig.clf()

			


	def get_intersec_word_counts(self, n, labels, events):

		l = labels[0]

		event1 = events[0]
		event2 = events[1]

		words1 = Counter()
		words2 = Counter()

		for ename in event1:
			words1 += self.events_dict[ename].words[l]

		for ename in event2:
			words2 += self.events_dict[ename].words[l]

		w1_2 = words1 & words2
		w_list = []
		for w, c in w1_2.most_common():
			if words1[w] > n and words2[w] > n:
				w_list.append(w)
				print(w,':', words1[w],':', words2[w])

		return w_list


	def init_fig(self):
		pass



	def fast_plot_word():
		pass


	def timerel(event_begin,event_end,tweet_time):

		if (event_begin > tweet_time):
			rel = "before"
		elif event_end < tweet_time:
			rel = "after"
		else:
			rel = "during"    
		return rel


	def froggedToSet(self, frogged_file):
		"Returns a set of words from a frogged file"
		frogged_tf = Tweetsfeatures(frogged_file)
		frogged_tf.set_tweets(u=1, ht=1, p=1) # remove urls, hashtags and punctuation
		s=set()

		for t in frogged_tf:
			for w in t.get_wordsequence():
				s.add(w)

	def get_tweetCountPerEvent(self):
		print("All tweet Count:", self.all_tweet_count)
		#print(*self.counter_events.most_common(), sep='\n')
		for w, v in self.counter_events.most_common():
			print(w, v)


		input("Press Enter ..-----------------: End Before")

	

		#exit()

def words_decreasing_rel_freq():
		pass

			# else:
				# print("-----Unique in Before Category:----->", word, freq, counter_during[word], counter_after[word])

					
				# if relative_freq_before > relative_freq_during and relative_freq_during > relative_freq_after:
				# 	# Print terms which their use decline over time without a threshould.Excluding Stop words.
				# 	continue
				# 	if word not in self.stop_words:
				# 		print("......")
				# 		print(word, (self.counter_before[word] + self.counter_during[word]+ self.counter_after[word]))
				# 		print(word, relative_freq_before, freq)
				# 		print(word, relative_freq_during, self.counter_during[word])
				# 		print(word, relative_freq_after, self.counter_after[word])
						
				# elif relative_freq_before > relative_freq_after and relative_freq_after > relative_freq_during:
				# 	# Print terms that occur most in before, than print the term if it is used more in after than in during
				# 	if word not in self.stop_words:
				# 		print("------")
				# 		print(word, (self.counter_before[word] + self.counter_during[word]+ self.counter_after[word]))
				# 		print(word, relative_freq_before, freq)
				# 		print(word, relative_freq_during, self.counter_during[word])
				# 		print(word, relative_freq_after, self.counter_after[word])




# Notes : Ask Florian not to change function names or argument structure in TweetFeatures class. In case he does, can he please let me know !
# Any test implementation.
# Create temporally sorted structure of tweets
# Write a method/find a way for showing/analysing words that occur just in one category.
# Write a method to list decreasing frequency. Allow some freedom, not strict order.
# use arg parser
# class for word can be defined. It can be under category or not.
# Explain count, freq and rel_freq
# Have a data structure to store frequencies.
# How should we treat words that occur just in one category, division by one ?
# Some terms are specific for some phase of the event.
# TempCategory - Before/During/After- Word -  : Inheritance Order


# Code Samples :
# -------------------------------------------------------------
# wordfrequency = defaultdict(list)
# for word in sequence:
# 	wordfrequency[word] += 1

# vocabulary = wordfrequency.keys()
# vocabulary["zin"][1]
# --------------------------------------------------------------

# def get_sorted_rel_freq(self):#adjust this method to be calleble for different dicts and different thresholds
# 		print("I am in get rel freq")

# 		values = sorted(self.relative_freq_before_dict.items(), key=operator.itemgetter(1))
# 		i= 1
# 		print("Rel. freq. of words occur in Before, inserted/sorted/calculates as their occurrence count without any relevant frequency scoring")
# 		while  i-1 < len(values): #print descending
# 			print('B-:', values[-i][0], values[-i][1], self.counter_before[values[-i][0]])
# 			i += 1

# 			if i % 150 == 0:
# 				input("Press Enter to Continue...")
# 				print('..................................')

# 		values = sorted(self.relative_freq_during_dict.items(), key=operator.itemgetter(1))
# 		i= 1
# 		print("Rel. freq. of words occur in Before, inserted/sorted/calculates as their occurrence count without any relevant frequency scoring")
# 		while  i-1 < len(values): #print descending
# 			print('D-:',values[-i][0], values[-i][1], self.counter_during[values[-i][0]])
# 			i += 1

# 			if i % 150 == 0:
# 				input("Press Enter to Continue...")
# 				print('..................................')

# 		values = sorted(self.relative_freq_after_dict.items(), key=operator.itemgetter(1))
# 		i= 1
# 		print("Rel. freq. of words occur in Before, inserted/sorted/calculates as their occurrence count without any relevant frequency scoring")
# 		while  i-1 < len(values): #print descending
# 			print('A-:', values[-i][0], values[-i][1], self.counter_after[values[-i][0]])
# 			i += 1

# 			if i % 100 == 0:
# 				input("Press Enter to Continue...")
# 				print('..................................')
# --------------------------------------------------------------
# def calc_words_relative_freq(self): #make it generic for all categories, consider having classes for each temporal category.
# 		"Calculate relative frequency  of all words and store them in dictionaries separately"
# 		"""
# 			Relative frequency of Words that occur just in one category calculated as their count.
# 		"""

# 		i = 0 # calculate frequency of before words and compare with other occurrence freq in other categories.
# 		for word, count in self.counter_before.most_common() :

# 			#print(word, count/all_before_word_count, count)
# 			freq_in_before = count/self.all_before_word_count
# 			freq_in_during = self.counter_during[word]/self.all_during_word_count
# 			freq_in_after = self.counter_after[word]/self.all_after_word_count

# 			relative_freq_during = freq_in_during/(freq_in_before+freq_in_after)
# 			relative_freq_after = freq_in_after/(freq_in_before+freq_in_during)
		    
# 			if (freq_in_during + freq_in_after) > 0: # otherwise it gives division by zero error.
# 				relative_freq_before = freq_in_before/(freq_in_during+freq_in_after) 
# 			else :
# 				relative_freq_before = count/1 #if it occurs just in before category give just the count

			
# 			self.relative_freq_before_dict[word] = relative_freq_before # for sorting
# 			self.relative_freq_during_dict[word] = relative_freq_during
# 			self.relative_freq_after_dict[word] = relative_freq_after
# 			#print('b--:',word, self.relative_freq_before_dict[word])
# 			# print(word, relative_freq_before, freq)
# 			# print(word, relative_freq_during, counter_during[word])
# 			# print(word, relative_freq_after, counter_after[word])
# 			# print("...")

# 		# input("Press Enter to continue...")
# 		# print('..................................')
# 		for word, count in self.counter_during.most_common(): #freq_in_before is zero. ???

# 			if word not in self.relative_freq_after_dict: # if it does not occur in before category
# 				freq_in_during = count/self.all_during_word_count
# 				freq_in_after = self.counter_after[word]/self.all_after_word_count

# 				relative_freq_after = freq_in_after/freq_in_before 

# 				if freq_in_after > 0:
# 					relative_freq_during = freq_in_during/freq_in_after
# 				else:
# 					relative_freq_during = count/1
				
# 				self.relative_freq_during_dict[word] = relative_freq_during
# 				self.relative_freq_after_dict[word] = relative_freq_after
# 				#print('d--:', word, self.relative_freq_during_dict[word])

# 		# input("Press Enter to continue...")
# 		# print('..................................')
# 		for word, count in self.counter_after.most_common(): #freq_in_before is zero. ???

# 			if word not in self.relative_freq_after_dict: # if it does not occur neither in before nor in during category
# 				self.relative_freq_after_dict[word] = count/1

# 				#print('a--:', word, self.relative_freq_after_dict[word])
# # # ---------------------------------------------------------------------------------------------------------------------------------
# def plotStats(self): # not complete
# 		begintime = datetime.datetime(2012,5,19,11,0,0)
# 		endtime = datetime.datetime(2012,5,20,3,0,0)
# 		xvalues = []
# 		xvalues_geveegd = []
# 		xvalues_trefzekerder = []
# 		xlabels = []

# 		interval = begintime
# 		while interval < endtime:
# 			nextinterval = interval + datetime.timedelta(0,3600*1)
# 			#nextinterval = interval + datetime.timedelta(hours=1)
# 			count = 0
# 			for t in self.time_list:
# 				if t >= interval and t < nextinterval:
# 					count += 1
# 			xvalues.append(count)

# 			count_geveegd = 0
# 			for t in self.time_list_geveegd:
# 				if t >= interval and t < nextinterval:
# 					count_geveegd += 1
# 			xvalues_geveegd.append(count_geveegd)

# 			count_trefzekerder = 0
# 			for t in self.time_list_trefzekerder:
# 				if t >= interval and t < nextinterval:
# 					count_trefzekerder += 1
# 			xvalues_trefzekerder.append(count_trefzekerder)
# 			#print(count_trefzekerder, "-----")


# 			xlabels.append(date2num(interval))
# 			interval = nextinterval
		
# 		for x in self.time_list_trefzekerder:# important range controll
# 			pass
# 			#print(x)
# 			if x < begintime or x > endtime:
# 				pass
# 				#print("out of range")

# 		# drng = pandas.date_range(begintime, periods=218, freq='H')
# 		# print(drng[0],drng[:-1], len(drng), len(xvalues))
# 		# ts = pandas.Series(xvalues, index=drng)
# 		# ts= ts.cumsum()
# 		# ts.plot()
# 		# exit()

# 		fig = matplotlib.pyplot.figure(figsize=(15,10)) #  'module' object is not callable
# 		matplotlib.pyplot.grid(True)

# 		matplotlib.pyplot.title('Title')
# 		#matplotlib.pyplot.plot(xlabels,xvalues,"morgen",xlabels, xvalues_geveegd, "geveegd")
# 		#matplotlib.pyplot.plot(xlabels,xvalues,'r-',xlabels, xvalues_geveegd,'b-', xlabels, xvalues_trefzekerder, 'g-')
# 		plot(xlabels, xvalues, color='red')
# 		plot(xlabels, xvalues_geveegd, color='blue')
# 		plot(xlabels, xvalues_trefzekerder, color='green')

# 		#xlim(0, 45)

# 		#matplotlib.pyplot.plot(xlabels,xvalues_geveegd)
# 		fig.savefig('/home/ali-hurriyetoglu/Desktop/graph.png',format='png', facecolor='w',edgecolor='w', orientation='portrait')
# ----------------------------------------------------------------------------------------------------------------------------------

	# def running_average_1(self, t_series_l):
	# 	"first version of running_average()-middle element based"
	# 	r_average = []
	# 	av = 0
	# 	divide_by = 4 # 3 elems + 1 for the weight of the middle one = 4
	# 	for prev,item,next in self.neighborhood(t_series_l):
	# 		print (prev, item, next)

	# 		if prev == None:
	# 			pass
	# 		elif next == None:
	# 			(prev + item*2)/(divide_by-1)
	# 		else:	
	# 			av = (prev+item*2+next)/divide_by
			
	# 		r_average.append(av)

	# 	return r_average # or 4

	# def running_average_2(self, t_series_l):
	# 	"second version of running_average()-.Wrong Temporal order"
	# 	r_average = []
	# 	av = 0
	# 	divide_by = 7 # 3 elems + 1 for the weight of the middle one = 4
	# 	for prev2, prev1, current in self.neighborhood(t_series_l):
	# 		print (prev2, prev1, current)

	# 		if prev2 == None:
	# 			continue;
	# 		else:
	# 			av=(prev2 + 2*prev1 + 4*current)/divide_by
			
	# 		r_average.append(av)

	# 	return r_average # or 4
	# def neighborhood_2(self, iterable):
	# 	"2. version of neighborhood(), wrong temporal order"
	# 	iterator = iter(iterable)
	# 	prev1 = None
	# 	prev2 = None

	# 	current = iterator.__next__()  # throws StopIteration if empty.
	# 	for next in iterator:
	# 		yield (prev2, prev1, current)
	# 		prev2 = prev1
	# 		prev1 = current
	# 		current = next

	# def neighborhood_1(self, iterable):
	# 	"1. version of neighborhood()"
	# 	iterator = iter(iterable)
	# 	prev = None
	# 	item = iterator.__next__()  # throws StopIteration if empty.
	# 	for next in iterator:
	# 		yield (prev,item,next)
	# 		prev = item
	# 		item = next
	# 	yield (prev,item,None)
# ----------------------------------------------------------------------------------------------------------------------------------

#matplotlib.pyplot.ylim(0,1)
		#yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5])
		#yticks([0, 0.05, 0.1,0.15, 0.2,0.25, 0.3,0.35, 0.4,0.45, 0.5,0.55, 0.6,0.65, 0.7,0.75, 0.8,0.85, 0.9])

# ----------------------------------------------------------------------------------------------------------------------------------

# self.stop_words = [] #only if it has any element in, will taken into account.
		# if stop_words_file != None: # implement exception control
		# 	stop_words_f = codecs.open(stop_words_file,"r","utf-8")
		# 	with stop_words_f as f:
		# 		for line in f:
		# 			stop_words_tmp = line.split(', ')
		# 			for sw in stop_words_tmp:
		# 				self.stop_words.append(sw[1:-1])
		# self.dutch_words_dict = {}
		# if dutch_words_file != None:
		# 	dutch_words_f = codecs.open(dutch_words_file,"r","utf-8")
		# 	with dutch_words_f as f:
		# 		for line in f:
		# 			key, val = line.split('\t')
		# 			self.dutch_words_dict[key] = int(val)
# ----------------------------------------------------------------------------------------------------------------------------------
