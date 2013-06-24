
import sys
#sys.path.append("..")

from tweetprocessing33.tweetsfeatures import Tweetsfeatures
import codecs
import operator
import datetime
import time

# import pytz
import numpy
#import pandas
import matplotlib
matplotlib.use('Agg') # for server xdisplay problem.
import math
from joblib import Parallel, delayed

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
#from joblib import Parallel, delayed
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
		self.normalized_w_byhighest={}
		self.w_mean_list = {}
		self.w_stdev_list = {}
		self.user_tweet_count = {}

		for l in label_list:
			self.tweets[l] = [] # list of tweets with this label to put the tweets of this label
			self.words[l]= Counter() # A counter of words for this label to put the count of words
			self.word_freq[l] = {} # A dictionary of words for a particular label to put their frequency
			self.w_tseries[l] = {} # A dictionary to put a word as keyterm and its timeseries array tuple.
			self.tweet_tseries[l] =[] # A timeserie list of tweets for this label
			self.normalized_w_tseries[l] = {} # A dictionary to put normalized(by tweet count) time series for each word.
			self.smoothed_w_tseries[l] = {}
			self.normalized_w_byhighest[l] = {}
			self.w_mean_list[l] = {}
			self.w_stdev_list[l] = {}
			self.user_tweet_count[l] = Counter() # This will count users tweet counts. maybe a list as a time serie, tweet count per time frame.


	def store_event_tweets(self, tf, label_list):
		"Store tweets in the dictionary in the relevant label list"
		for t in tf.tweets:
			if t.label in label_list: # Do it just for the labels wanted to be taken into account.
				self.tweets[label_list[0]].append(t)

	def count_all_words(self, label_list):
		"Count and add per event and label"
		for label in label_list:
			for t in self.tweets[label]:
				twseq = t.get_wordsequence()
				for w in list(set(twseq)):
					wchange = '' # keep new form
					worg = '' #keep old form of a word
					if '@' in w:
						self.words[label]['username'] += 1
						worg = w
						wchange = 'username'
					elif w in ['ajax','az','psv','vvv', 'feyenoord']:
						self.words[label]['teamname'] += 1
						worg = w
						wchange = 'teamname'
					elif w == 'retweet':
						self.words[label]['rt'] += 1
						worg = w
						wchange = 'rt'
					else:
						self.words[label][w] += 1
						continue # not to do remove-insert for normal words
					
					if wchange != '':
						for i in range(0, len(twseq)): #change all occurences
						
							if twseq[i] == worg:
								twseq[i] = wchange
								# if i > 0:
								# 	print('twchange:w_ind:',i,w, ':to:',wchange,':rslt:', twseq[i-1:i+2])
								# else:
								#  	print('twchange',i,w, ':to:',wchange,':rslt:', twseq[i:i+2])
					else:
						print('wchange Should not be empty!!..Exit()')
						exit()
				if 'retweet' in twseq:
					print('retweet in it:',twseq)		


	def count_all_bigrams(self, label_list):
		"Count and add per event and label"
		for label in label_list:
			for t in self.tweets[label]:
				twseq = t.get_wordsequence()
				for bigram in self.get_bigrams(twseq):
					self.words[label][bigram] += 1
					twseq.append(bigram) # add this new feature to the tweet.
					#print('bigram:', twseq[-2:])



	def get_bigrams(self, tweet):
		bigrams = []

		if len(tweet) > 1:
			for i in range(0, len(tweet)-1):

				if ('@' not in tweet[i]+tweet[i+1]) or (tweet[i]+'_'+tweet[i+1] not in ['fc_twente', 'fc_utrecht', 'fc_groningen', 'afc_ajax', 'afc_teamname']) :
					bigrams.append(tweet[i]+'_'+tweet[i+1])

				elif '@' in tweet[i] and '@' in tweet[i+1]:
					bigrams.append('username'+'_'+'username')

				elif ('@' in tweet[i]) and ('@' not in tweet[i+1]):
					bigrams.append('username'+'_'+ tweet[i+1])

				elif ('@' not in tweet[i]) and ('@' in tweet[i+1]):
					bigrams.append(tweet[i] + '_' + 'username')

				elif (tweet[i]+'_'+tweet[i+1]) in ['fc_twente', 'fc_utrecht', 'fc_groningen', 'afc_ajax']:
					tweet[i] = 'teamname'
					tweet.remove(tweet[i+1])
					bigrams.append('teamname'+'_'+tweet[i+1])
					#print('fc_ norm & new bigram', 'teamname'+'_'+tweet[i+1])

					
					
		return bigrams



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
		#print('Name of the event for calc:',self.name)
		#print('corresponding label:', label)
		self.word_freq[label][w] = self.words[label][w] / len(self.tweets[label])

	def calc_tseries(self, w, label, minuteForFrame, dayCount):
		# print('In calc Tserie Method, The word:', w)
		if len(self.tweet_tseries[label]) == 0:
			time_list_for_tweets = sorted([x.time for x in self.tweets[label]])
			#this is a tuple
			self.tweet_tseries[label] = self.calc_tseries_tweets(time_list_for_tweets, minuteForFrame,dayCount)
			#print('Tseries:',self.tweet_tseries[label])

		time_list_for_word = [t.time for t in self.tweets[label] if w in list(set(t.get_wordsequence())) ]
		self.w_tseries[label][w] = self.calc_tseries_count_words(time_list_for_word, minuteForFrame, dayCount)
		len_wtserie = len(self.w_tseries[label][w])
		#print('W_serie of the word:', self.w_tseries[label][w])

		if len(time_list_for_word) == 0: # in the test most of the training words does not exist therefore assign 0 directly
			print('No tweet for it!!!:',w)
			self.normalized_w_tseries[label][w] = [0] * len_wtserie
			self.smoothed_w_tseries[label][w] =  [0] * (len_wtserie-2)
			self.normalized_w_byhighest[label][w] = [0] * (len_wtserie-2)
			self.word_freq[label][w] = 0

			self.w_mean_list[label][w] = [0] * (len_wtserie-2)
			self.w_stdev_list[label][w] = [0] * (len_wtserie-2)

		else:
			self.normalized_w_tseries[label][w] = self.normalize_tserie_by_tserie(self.w_tseries[label][w], self.tweet_tseries[label][1])
			# print('E. Name&w.:', self.name, w)
			# print('Tserie:', self.w_tseries[label][w])
			#print('Normalized w tserie:', self.normalized_w_tseries[label][w])

			self.smoothed_w_tseries[label][w] = self.running_average(self.normalized_w_tseries[label][w])
			#print('Smoothed w tserie:', self.smoothed_w_tseries[label][w])
		
			self.normalized_w_byhighest[label][w] = self.normalize_by_highest(w, self.smoothed_w_tseries[label][w])#w is just to know which word tserie is in calculation
			#print('Normalized by highest value in a tserie:', self.normalized_w_byhighest[label][w])
			#print('...............................................................')

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

	def normalize_tserie_by_tserie(self, to_normalize, normalizer):
		"Make this more efficient with numpy array"
		if len(to_normalize) == len(normalizer):
			return [a/b if b > 0 else 0 for a, b in zip(to_normalize, normalizer) ]
		else:
			print("Length of the word tseries and tweet time series should be equal, Exit..")
			print("Word tserie length:",len(to_normalize), "Tweet tserie:", len(normalizer))
			exit()
			return False

	def normalize_by_highest(self, w, t_serie):
		max_val = max(t_serie)
		
		#print('..Max value for this tserie:',max_val)
		#print('Tserie before Normalization - Smoothed:\n', t_serie)
		tmp_tserie = []
		for elem in t_serie:
			if max_val == 0:
				tmp_tserie.append(0)
			else:
				tmp_tserie.append(elem/max_val)
		#print('Tserie after normalization:', tmp_tserie)

		return tmp_tserie


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
		print('ev. name:',self.name)
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
				#print('Added object time serie:',e.tweet_tseries[l][1])
				#print('Blended time serie',self.tweet_tseries[l][1])
			else:
				print('Length of blended objects tweet time series should be at same length',len(self.tweet_tseries[l][1]), len(e.tweet_tseries[l][1]))
				exit()
	

		self.w_tseries = {l:{}} # A dictionary to put a word as keyterm and its timeseries list, tuple..or list.
		for e in events_l:
			for w, tserie in e.w_tseries[l].items():
				if w not in self.w_tseries[l]:
					self.w_tseries[l][w] = [0] * len(tserie)
					print('Blend tserie created for:', w, self.words[l][w])
				self.w_tseries[l][w] = [a+b for a, b in zip(self.w_tseries[l][w], tserie)]
				

		self.word_freq = {l:{}} # A dictionary of words for a particular label to put their frequency
		self.normalized_w_tseries = {l:{}}
		self.smoothed_w_tseries={l:{}}
		self.normalized_w_byhighest={l:{}}
		self.w_mean_list = {l:{}}
		self.w_stdev_list = {l:{}}

	def calc_tseries(self, w, label):

		if w not in self.w_tseries[label]:
			print('Not in self.w_tseries[label]', w)

		try:
			self.normalized_w_tseries[label][w] = self.normalize_tserie_by_tserie(self.w_tseries[label][w], self.tweet_tseries[label][1])
			# print('E. Name&w.:', self.name, w)
			# print('Tserie:', self.w_tseries[label][w])
			# print('Normalized w tserie:', self.normalized_w_tseries[label][w])
			self.smoothed_w_tseries[label][w] = self.running_average(self.normalized_w_tseries[label][w])
			
			# print('Smoothed w tserie:', self.smoothed_w_tseries[label][w])
			self.normalized_w_byhighest[label][w] = self.normalize_by_highest(w, self.smoothed_w_tseries[label][w])#w is just to know which word tserie is in calculation
			# print('Normalized by highest value in a tserie:', self.normalized_w_byhighest[label][w])
			# print('...............................................................')

			if w not in self.word_freq[label]:
				#print('Freq is None, calculating ...:', w)
				self.calcFreq_for_word(w, label)
				#print('Calculates:', w, ' -Freq')
			self.w_mean_list[label][w] = [self.word_freq[label][w]] * len(self.smoothed_w_tseries[label][w])
			self.w_stdev_list[label][w] = [numpy.std(self.smoothed_w_tseries[label][w])] * len(self.smoothed_w_tseries[label][w])
		except:
			pass

		# running average make the lists shorter
		#cut from back, to have a graph from the zero point of the event.
		#return (self.tweet_tseries[label][0][:-2], self.smoothed_w_tseries[label][w])
	

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
		#self.tf.set_tweets(u=1, ht=1, p=1) # remove urls, hashtags and punctuation
		self.tf.set_tweets_oneline(u=1, ht=1) # new data, 2011, 2012 data
		# self.tf.add_ngrams(n=2)
		# self.tf.add_ngrams(n=3)


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
		
		self.prediction_results = {}
		#counts, freqs should be done, for all. # order of these mathods should be preserved.
		# self.count_words()  self.calc_words_freq()  self.calc_words_relative_freq()

		self.events_dict = {}

	
		
	def crea_event_objs_for(self, label_list, crea_event_obj_for):
		"it handles hashtag names specific for soccer matches"
		"""
		Info: Creates a different object for each event
		Notes:
		1- Add event list to be taken into account. Events that are not in the list should not be processed.
		2- An event object for all soccer matches.
		"""

		print('Create Event objects for:')
		for name in crea_event_obj_for:
			
			if len(name) == 9 and name[:2] == 'az':
				e_place = 'az'
			else:
				e_place = name[:3]
			
			if name not in self.events_dict:
				self.events_dict[name] = Event(name, self.event_places[e_place], self.event_times[self.event_names.index(name)], label_list)
				print(name, end = ', ')
			else:
				print('Same name object can not be created !! Exit ..')
				exit()


		off_tweet_count = 0
		in_tweet_count = 0
		# for t in self.tf.tweets: #put tweets in the relevant places
		# 	if t.label in label_list and t.event in crea_event_obj_for: #ignore tweets that does not have proper hashtag and label.
		# 		self.events_dict[t.event].tweets[t.label].append(t)
		for t in self.tf.tweets: #put tweets in the relevant places
			if t.event in crea_event_obj_for:
				if t.time < self.events_dict[t.event].time: #ignore tweets that does not have proper hashtag and label.
					self.events_dict[t.event].tweets[label_list[0]].append(t)
					#print(label_list[0])
					if t.time < (self.events_dict[t.event].time - datetime.timedelta(8)) and (t.event[-2:] == '11'):
						off_tweet_count += 1
					else:
						in_tweet_count += 1

		print('\n\n** Off and in Tweet counts are:', off_tweet_count, in_tweet_count)
					


		tweet_count_train = 0
		tweet_count_test = 0
		print('Event Name & Tweet count:')
		for name, event in self.events_dict.items():
			if name[-2:] == '11':
				tweet_count_train += len(event.tweets[label_list[0]])
			else:
				tweet_count_test += len(event.tweets[label_list[0]])
			print(name+':'+str(len(event.tweets[label_list[0]])), end = ', ')
			event.count_all_words(label_list)
			event.count_all_bigrams(label_list)

		print('\n\nAll tweet count:(Test, Train)', tweet_count_test, tweet_count_train)

	def get_ngrams(self):
		'''
		Print ngrams that are added to Tweet Features by:
		self.tf.add_ngrams(n=2)
		self.tf.add_ngrams(n=3)

		'''
		print(*self.tf.get_features(), sep='\n')


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
		'''
		def get_tweets_of_timeframe():
			for i in range(0,170):
				print('\n----------------------range is:', i, i+1)
				print(*swa.get_event_tweets_from_to('before', all_events_list[indexno][0], i+1, i), sep='\n')
		'''

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

		event_trained, event_test = self.structure_train_test_events(events[0], events[1])
		print('Training & Test Events:', event_trained.name, '...', event_test.name)

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

		event_trained, event_test = self.structure_train_test_events(events[0], events[1])
		print('Training & Test Events:', event_trained.name, '...', event_test.name)

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

	def calc_euc_dist_w_list_random(self, w_list, labels, events, minuteForFrame, dayCount, s_count):
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
					if w not in event.smoothed_w_tseries[l]:
						word_t_series = event.calc_tseries(w, l, minuteForFrame, dayCount) # calc. relevant freq, t_series
						#print('Word and its tserie:', w, word_t_series)

		event_trained, event_test = self.structure_train_test_events(events[0], events[1])
		print('Training & Test Events:', event_trained.name, '...', event_test.name)

		self.calc_mean_median(events[0])
		
		euc_distances = {}

		trained_X = event_trained.tweet_tseries[label][0][:-2] # get it from tweet time series. It is same for all events.
		# tweet_count_plot = event_trained.tweet_tseries[label][1][:-2]

		# graph_title = 'TweetCount'+ '-Trn:'+self.list_to_str(events[0])+'\nTst:'+self.list_to_str(events[1])+'\nWC:'+str(len(w_list))+'-minFrame:'+str(minuteForFrame)+ '-DayC:'+str(dayCount) + '-norm' + '-rand'
		# file_name = 'TweetCount'+ '-Trn:'+self.list_to_str(events[0])+'Tst:'+self.list_to_str(events[1])+'WC:'+str(len(w_list))+'-minFrame:'+str(minuteForFrame)+ '-DayC:'+str(dayCount)+'-norm'+'-rand'
		# x_label = 'Hours Before an Event'
		# y_label = 'Tweet Count'
		# self.plot_tserie_list(trained_X, [tweet_count_plot] , ['TweetCount'], graph_title, x_label, y_label, file_name)
		
		euc_distances_sum = []
		test_seq = []
		

		for sample_count in range(s_count, s_count+1): #range(1, len(trained_X)+1):
			row_err_predict_l = []
			row_err_mean_l = []
			row_err_median_l = []
			abs_err_predict_l = []
			abs_err_mean_l = []
			abs_err_median_l = []

			for i in range(0, (1+len(trained_X)-sample_count)):#(1+len(trained_X)-sample_count)):

				#print('count of Seq:',1+len(trained_X)-sample_count)
				euc_distances_sum = [(1111,0)] * (1+len(trained_X)-sample_count) #initialization needed for sum
				
				for w in w_list:
					trained_Y = event_trained.smoothed_w_tseries[label][w] # this should produce more balanced results.
					trained = [(a,b) for a, b in zip(trained_X, trained_Y)]
					trained = list(reversed(trained)) # Time was reversed in the normal array. Therefore reverse for the normal timeline with the test data.
					trained_sub_seq = self.get_sub_seqeunces(sample_count, trained)
					
					test_Y = event_test.smoothed_w_tseries[label][w]
					test_Y = [(a,b) for a, b in zip(trained_X, test_Y)]
					test_Y = list(reversed(test_Y[:len(trained)])) #test_Y, when not smoothed, is longer be careful
					test_sub_seq = self.get_sub_seqeunces(sample_count, test_Y)

					#print('Len of test sub seq:', len(test_sub_seq))
					
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
			graph_title = 'Row Err'+ '-Trn:'+self.list_to_str(events[0])+'\nTst:'+self.list_to_str(events[1])+'\nWC:'+str(len(w_list))+'-minFrame:'+str(minuteForFrame)+ '-DayC:'+str(dayCount)+'-SampleC:'+str(sample_count) +'rand'
			file_name = 'Row Err'+ '-Trn:'+self.list_to_str(events[0])+'Tst:'+self.list_to_str(events[1])+'WC:'+str(len(w_list))+'-minFrame:'+str(minuteForFrame)+ '-DayC:'+str(dayCount) +'-SampleC:'+str(sample_count) + '-rand'
			x_label = 'Hours Before an Event'
			y_label = 'Row Error'
			self.plot_tserie_list(trained_X, mean_list , ['Row error', 'median', 'mean'], graph_title, x_label, y_label, file_name)

	def calc_euc_dist_w_list_random_fast(self, w_list, labels, events, minuteForFrame, dayCount):
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
		all_1_euc_dist = []
		square_err_predict_list = []
		square_err_mean_list = []
		square_err_median_list = []

		mean_sq_err_predict_l = []
		mean_sq_err_mean_l = []
		mean_sq_err_median_l = []

		for name, event in self.events_dict.items():
			for l in labels:
				for w in w_list:
					if w not in event.smoothed_w_tseries[l]:
						word_t_series = event.calc_tseries(w, l, minuteForFrame, dayCount) # calc. relevant freq, t_series
						#print('Word and its tserie:', w, word_t_series)

		event_trained, event_test = self.structure_train_test_events(events[0], events[1], labels)
		print('Training & Test Events:', event_trained.name, '...', event_test.name)

		self.calc_mean_median(events[0])
		
		euc_distances = {}

		trained_X = event_trained.tweet_tseries[label][0][:-2] # get it from tweet time series. It is same for all events.
		tweet_tserie_hours = list(reversed(event_test.tweet_tseries[label][0][:-2]))
		tweet_tserie_count = list(reversed(event_test.tweet_tseries[label][1][:-2]))
		# tweet_count_plot = event_trained.tweet_tseries[label][1][:-2]

		# graph_title = 'TweetCount'+ '-Trn:'+self.list_to_str(events[0])+'\nTst:'+self.list_to_str(events[1])+'\nWC:'+str(len(w_list))+'-minFrame:'+str(minuteForFrame)+ '-DayC:'+str(dayCount) + '-norm' + '-rand'
		# file_name = 'TweetCount'+ '-Trn:'+self.list_to_str(events[0])+'Tst:'+self.list_to_str(events[1])+'WC:'+str(len(w_list))+'-minFrame:'+str(minuteForFrame)+ '-DayC:'+str(dayCount)+'-norm'+'-rand'
		# x_label = 'Hours Before an Event'
		# y_label = 'Tweet Count'
		# self.plot_tserie_list(trained_X, [tweet_count_plot] , ['TweetCount'], graph_title, x_label, y_label, file_name)
		
		euc_distances_sum = []
		test_seq = []
		
		row_err_predict_l = []
		row_err_mean_l = []
		row_err_median_l = []
		abs_err_predict_l = []
		abs_err_mean_l = []
		abs_err_median_l = []

		sum_square_errors = 0

		for i in range(0, (1+len(trained_X)-1)):#(1+len(trained_X)-sample_count)):

			euc_distances_sum = [(1111,0)] * (1+len(trained_X)-1) #initialization needed for sum
			
			for w in w_list:
				trained_Y = event_trained.smoothed_w_tseries[label][w] # this should produce more balanced results.
				trained = [(a,b) for a, b in zip(trained_X, trained_Y)]
				trained = list(reversed(trained)) # Time was reversed in the normal array. Therefore reverse for the normal timeline with the test data.
				trained_sub_seq = self.get_sub_sequences(1, trained)
				
				test_Y = event_test.smoothed_w_tseries[label][w]
				test_Y = [(a,b) for a, b in zip(trained_X, test_Y)]
				test_Y = list(reversed(test_Y[:len(trained)])) #test_Y, when not smoothed, is longer be careful
				test_sub_seq = self.get_sub_sequences(1, test_Y)

				#print('Len of test sub seq:', len(test_sub_seq))
				
				euc_distance_w = [] # Go clean for the next word
				for j in range(0, len(trained_sub_seq)):
				#Calc euc. distance and add it as a tuple with the last time point of this sequence. for this subsequence
					#euc_distance_w.append((trained_sub_seq[j][-1][0],sqrt(math.fsum([(a[1]-b[1])**2 if not numpy.allclose(a[1], b[1]) else 0 for a, b in zip(test_sub_seq[i], trained_sub_seq[j])])))) # Euc distance
					euc_distance_w.append((trained_sub_seq[j][-1][0],sqrt(math.fsum([(a[1]*b[1]) for a, b in zip(test_sub_seq[i], trained_sub_seq[j])])))) # dot product

				euc_distances_sum = [(b[0], math.fsum([a[1],b[1]])) for a, b in zip(euc_distances_sum, euc_distance_w)] # Add current euclidian values to the sum
			
			#print('Euc Distances for the observation number:',i,'-is:\n',euc_distances_sum)
			actual = test_sub_seq[i][-1][0] # first element of last tuple of this tuple sequence
			#print('Actual time to the event:', actual)
			all_1_euc_dist.append((actual, euc_distances_sum)) #Put all 1 step euc differences
			#print('Euc Distances for all observations up to now is:',all_1_euc_dist)

			#print('--EucDistForTheseObservations:', euc_distances_sum)
			#smallest_euc = min([a[1] for a in euc_distances_sum]) # smallest for euc
			smallest_euc = max([a[1] for a in euc_distances_sum]) # smallest for dot product
			#print('SmallestEuc:', smallest_euc )

			matched_times = []
			for dist_tuple in euc_distances_sum:
				if numpy.allclose(dist_tuple[1], smallest_euc ):
					matched_times.append(dist_tuple[0])

			prediction = numpy.mean(matched_times)
		
			row_err_predict_l.append(prediction - actual)
			row_err_mean_l.append(self.mean_of_tweets - actual)
			row_err_median_l.append(self.median_of_tweets - actual)

			abs_err_predict_l.append(abs(prediction-actual))
			abs_err_mean_l.append(abs(self.mean_of_tweets-actual))
			abs_err_median_l.append(abs(self.median_of_tweets-actual))
			#print('Absolute Error of Prediction:',abs_err_predict_l[-1])

			#sum_square_errors += (prediction - actual)**2 * tweet_tserie_count[tweet_tserie_hours.index(actual)]


		# One time frame calculation.
		# print('.........................................................................')
		# print('X axe and Y axe for time and Absolute Error:')
		# print('Training Event and test Event:', self.list_to_str(events[0]), self.list_to_str(events[1]))
		# temp_row_err_predict_l = list(reversed(row_err_predict_l))
		# temp_abs_err_predict_l = list(reversed(abs_err_predict_l))
		# for i in range(0, len(trained_X)):
		# 	print(trained_X[i],temp_row_err_predict_l[i])



		# print('Mean absolute error:', numpy.mean(temp_abs_err_predict_l))
		# print('RMSE:',sqrt(sum_square_errors/sum(tweet_tserie_count)))
		# print('.........................................................................')

		#------------------------------------------------------------
		mean_list = [row_err_predict_l, row_err_median_l, row_err_mean_l]
		mean_list = [list(reversed(a)) for a in mean_list]
		# Do not forget to change the sample count to something different than zero.
		graph_title = 'Row Err'+ '-Trn:'+self.list_to_str(events[0])+'\nTst:'+self.list_to_str(events[1])+'\nWC:'+str(len(w_list))+'-minFrame:'+str(minuteForFrame)+ '-DayC:'+str(dayCount)+'-SampleC:'+str(0) +'rand'
		file_name = 'Row Err'+ '-Trn:'+self.list_to_str(events[0])+'Tst:'+self.list_to_str(events[1])+'WC:'+str(len(w_list))+'-minFrame:'+str(minuteForFrame)+ '-DayC:'+str(dayCount) +'-SampleC:'+str(0) + '-rand'
		#x_label = 'Hours Before an Event'
		y_label = 'Row Error'

		temp_euc_dist = []
		temp_all_dist = []

		mean_row_err_predict_l = []
		mean_row_err_mean_l = []
		mean_row_err_median_l = []
		mean_abs_err_predict_l = []
		mean_abs_err_mean_l = []
		mean_abs_err_median_l = []
		sample_count_l = []
		root_mean_sq_err = []
		
		sum_of_tweet_counts = math.fsum(tweet_tserie_count)
		print('Sum of tweet counts for this event:', sum_of_tweet_counts)

		for sample_count in range(0, len(all_1_euc_dist)):
			
			prediction_l = []
			row_err_predict_l = []
			row_err_mean_l = []
			row_err_median_l = []
			abs_err_predict_l = []
			abs_err_mean_l = []
			abs_err_median_l = []

			sum_of_sq_err = 0
			frame_tweet_count = 0

			for x in range(0, len(all_1_euc_dist)):
				temp_euc_dist = []
				
				frame_tweet_count = sum(tweet_tserie_count[x:x+sample_count+1])

				if x+sample_count < len(all_1_euc_dist):

					for y in range(0, len(all_1_euc_dist[0][1])):

						if y + sample_count < len(all_1_euc_dist[0][1]):
							tmp_sum = 0
							tmp_time = -999

							for j in range(0, sample_count+1):
								
						 		tmp_sum += all_1_euc_dist[x+j][1][y+j][1]
						 		tmp_time = all_1_euc_dist[x+j][1][y+j][0]
						 		
						else:
							break;
					
						#print('Time and sum:',tmp_time, tmp_sum)
						temp_euc_dist.append((tmp_time, tmp_sum))

					actual = all_1_euc_dist[x+sample_count][0]
				if len(temp_euc_dist) == 0:
					break
				
				smallest_euc = min([a[1] for a in temp_euc_dist])
				
				matched_times = []
				prediction = 0
				for dist_tuple in temp_euc_dist:
					if numpy.allclose(dist_tuple[1], smallest_euc ):
						matched_times.append(dist_tuple[0])
				#print('Matched Times:', matched_times)
				prediction = numpy.mean(matched_times)

				prediction_l.append(prediction)
				row_err_predict_l.append(prediction - actual)
				row_err_mean_l.append(self.mean_of_tweets - actual)
				row_err_median_l.append(self.median_of_tweets - actual)
				#print('Row Error of Prediction:',row_err_predict_l[-1])

				abs_err_predict_l.append(abs(prediction-actual))
				abs_err_mean_l.append(abs(self.mean_of_tweets-actual))
				abs_err_median_l.append(abs(self.median_of_tweets-actual))
				# #print('Absolute Error of Prediction:',abs_err_predict_l[-1])
		
				sum_of_sq_err += (prediction - actual)**2 * frame_tweet_count			

			root_mean_sq_err.append(sqrt(sum_of_sq_err/sum_of_tweet_counts))
			print('Event and Frame Length:', self.list_to_str(events[1]),sample_count+1)
			print('List of root mean Sq. Err per Frame Length:',root_mean_sq_err)

			mean_list = [prediction_l, row_err_predict_l, row_err_median_l, row_err_mean_l]
			mean_list = [list(reversed(a)) for a in mean_list]

			# Do not forget to change the sample count to something different than zero.
			graph_title = 'Row Err'+ '-Trn:'+self.list_to_str(events[0])+'\nTst:'+self.list_to_str(events[1])+'\nWC:'+str(len(w_list))+'-minFrame:'+str(minuteForFrame)+ '-DayC:'+str(dayCount)+'-SampleC:'+str(sample_count+1) +'rand'
			file_name = 'Row Err'+ '-Trn:'+self.list_to_str(events[0])+'Tst:'+self.list_to_str(events[1])+'WC:'+str(len(w_list))+'-minFrame:'+str(minuteForFrame)+ '-DayC:'+str(dayCount) +'-SampleC:'+str(sample_count+1) + '-rand'
			x_label = 'Hours Before an Event'
			y_label = 'Row Error'
			self.plot_tserie_list(trained_X, mean_list , ['Prediction','Row error', 'median', 'mean'], graph_title, x_label, y_label, file_name, False)

			mean_abs_err_predict_l.append(numpy.mean(abs_err_predict_l))
			mean_abs_err_mean_l.append(numpy.mean(abs_err_mean_l))
			mean_abs_err_median_l.append(numpy.mean(abs_err_median_l))
			sample_count_l.append(sample_count+1)

			len_mean_errs = len(mean_abs_err_predict_l) - 1
	
			#print('Predict, mean, median: Mean Absolute Errors Per sample count:', mean_abs_err_predict_l[len_mean_errs], mean_abs_err_mean_l[len_mean_errs], mean_abs_err_median_l[len_mean_errs])

			if sample_count == 48:
				break;
		#print('Predict, mean, median: Mean Absolute Errors per sample counts:', mean_abs_err_predict_l,'\n', mean_abs_err_mean_l,'\n', mean_abs_err_median_l,'\n')
		mean_list = [mean_abs_err_predict_l, mean_abs_err_median_l, mean_abs_err_mean_l]

		graph_title = 'Mean Abs. Err Per sample count:'+ '-Trn:'+self.list_to_str(events[0])+'\nTst:'+self.list_to_str(events[1])+'\nWC:'+str(len(w_list))+'-minFrame:'+str(minuteForFrame)+ '-DayC:'+str(dayCount) +'rand'
		file_name = 'Mean Abs. Err Per sample count:'+ '-Trn:'+self.list_to_str(events[0])+'Tst:'+self.list_to_str(events[1])+'WC:'+str(len(w_list))+'-minFrame:'+str(minuteForFrame)+ '-DayC:'+str(dayCount) + '-rand'
		x_label = 'Sequence Length as frame count'
		y_label = 'Mean Absolute Error'
		self.plot_tserie_list(sample_count_l, mean_list , ['Mean Abs. Err', 'Median Baseline', 'Mean Baseline'], graph_title, x_label, y_label, file_name, True)#sample count - graph True
		print('**-Next Obs.-**:Finished Sample Count:', sample_count+1)

		graph_title = 'Root Mean Square Error Per Sample Count:'+ '-Trn:'+self.list_to_str(events[0])+'\nTst:'+self.list_to_str(events[1])+'\nWC:'+str(len(w_list))+'-minFrame:'+str(minuteForFrame)+ '-DayC:'+str(dayCount) +'rand'
		file_name = 'Root Mean Square Error Per Sample Count:'+ '-Trn:'+self.list_to_str(events[0])+'Tst:'+self.list_to_str(events[1])+'WC:'+str(len(w_list))+'-minFrame:'+str(minuteForFrame)+ '-DayC:'+str(dayCount) + '-rand'
		x_label = 'Sequence Length as frame count'
		y_label = 'Root Mean Square Error'
		self.plot_tserie_list(sample_count_l, [root_mean_sq_err],['Root Mean Square Error'], graph_title, x_label, y_label,file_name, True)

	def calc_euc_dist_w_list_random_fast_normalizedByHighest_t_serie(self, w_list, labels, events, minuteForFrame, dayCount, tserie_type='normalized_w_byhighest'):
		'First event is training, the second test.Later adapt it to fist n-1 training, n. is test'
		"""
		  -First label should be before for now.
		  -Since the X axes is same we do not take it into account
		  -First event training second is test
		  -

		  Questions:
		     1- Should I normalize scores for trained and test lists
		     2- In dot product should we add the similarities as we were doing for euclidean distance ?
		     3- The train set is smoothed, normalized, etc. But should we do the same for the test, how more realistic ? 

		  To Do:
		  	1- Make the cumulative distance/similarity calculation a seperate function.
		  	2- Make the error calculations in a seperate function.
		  	3- Try by deleting user names
		  	4- user based analysis ? threat or any other feature can be identified by looking to the textual history of user as well.
		  	   - Classify users according the quality, continuity of the information they give. When try to predict,
		  	     you can identify this users(type) relevance.
		  	   - use most informative users, measure their affect
		  	5- Spelling correction can be one according the user as well.
		  	6- use all events as training except 1, and use it as test, some sort of 10 fold cross validation.
		  	7- Change the w_list, it should come from the test set.
		  	8- delete non-informative ones, rt, @ : maybe informative but are we sure about information ?
		  	9- Train and test set should allow to have different days back.
		  	10- Differentiate between similarity and distance metrics. similarity accept max, distance accepts min of the scores. 
		"""
		# tserie_type = 'smoothed_w_tseries'
		tserie_type = 'normalized_w_tseries'
		label = labels[0]
		all_1_euc_dist = []
		
		for name, event in self.events_dict.items():
			for l in labels:
				for w in w_list:
					if w not in getattr(event, tserie_type)[l]:
						word_t_series = event.calc_tseries(w, l, minuteForFrame, dayCount) # calc. relevant freq, t_series
					else:
						pass

		event_trained, event_test = self.structure_train_test_events(events[0], events[1], tserie_type, labels, w_list)
		print('Training & Test Events:', event_trained.name, '...', event_test.name)

		len_tserie_X_trained = len(getattr(event_trained, tserie_type)[l][w_list[0]])
		len_tserie_X_test = len(getattr(event_test, tserie_type)[l][w_list[0]])
		trained_X = event_trained.tweet_tseries[label][0][:len_tserie_X_trained] # get it from tweet time series. It is same for all events.
		test_X = event_test.tweet_tseries[label][0][:len_tserie_X_test]
		
		self.calc_mean_median(events[0])

		print('\nNormalized, smoothed and normalized_by_highest:\n')
		# w_list1 = self.get_train_words_above2std(w_list, event_trained.normalized_w_tseries[label])
		# w_list2 = self.get_train_words_above2std(w_list, event_trained.smoothed_w_tseries[label])
		# w_list3 = self.get_train_words_above2std(w_list, event_trained.normalized_w_byhighest[label])
		w_list = w_list

		all_1_euc_dist = []
		
		for i in range(0, len(test_X)):
			temp_euc_dist = 0
			euc_dist_l = []
			
			occ_w_in_this_frame_test = self.get_available_words(event_test, tserie_type, label, w_list, i)


			print('test point:',i, '\nWords:', occ_w_in_this_frame_test)
		
			if len(occ_w_in_this_frame_test) == 0: # No words in this frame, simply euc_dist are zero.
				euc_dist_l = [0] * len(trained_X)
				all_1_euc_dist.append(euc_dist_l)
				continue

			for y in range(0, len(trained_X)):

				occ_w_in_this_frame_train = self.get_available_words(event_trained, tserie_type, label, w_list, y)


				#train_vector, test_vector = self.crea_vectors(getattr(event_trained, tserie_type)[label], occ_w_in_this_frame_train, y, getattr(event_test, tserie_type)[label], occ_w_in_this_frame_test,i)
				#print('Length of train words in this frame, and vectors lengths, train, test', len(occ_w_in_this_frame_train), len(train_vector), len(test_vector))
				#print('Train and tst vectors', train_vector, '\n',test_vector)

				tr_ts_val_tuple_l = []
				
				for w in occ_w_in_this_frame_test:

					trained_Y_w_value = getattr(event_trained, tserie_type)[label][w][y] #value of w in current train
					test_Y_w_value = getattr(event_test, tserie_type)[label][w][i] #value of w in current test
					tr_ts_val_tuple_l.append((trained_Y_w_value, test_Y_w_value))
				print('Train and tst tuples:', tr_ts_val_tuple_l)
				temp_euc_dist = self.euc_dist(tr_ts_val_tuple_l)
				
				euc_dist_l.append(temp_euc_dist)
				temp_euc_dist = 0

			all_1_euc_dist.append(euc_dist_l)			

		for seq_len in range(0, len(test_X)): #for all frame lengths

			# m x n matrix became (m-1)x(n-1)
			euc_dist_matrix = self.calc_dist_for_seq(all_1_euc_dist, seq_len) # calc. euc. dist. from one-to-one distances.
			

			if seq_len not in self.prediction_results:
					self.prediction_results[seq_len] = []

			for tst_i in range(0, len(test_X[seq_len:])):
				predictions = self.get_predictions_dist(euc_dist_matrix[tst_i], trained_X[seq_len:])
				
				if len(predictions) != 0:
					actual = test_X[seq_len:][tst_i]
					self.prediction_results[seq_len].append((actual, predictions))
					#print('Actual:',actual, 'predictions:', predictions, 'raw_errors:', raw_errors)
				else:
					print('No Tweets to predict anything ! Seq. len & actual:', seq_len, actual)

		self.print_dict(self.prediction_results)
		self.print_dict(self.calc_rmse(self.prediction_results))

	def calc_by_vectors(self, w_list, labels, events, minuteForFrame, dayCount, tserie_type, k=1):
		'First event is training, the second test.Later adapt it to fist n-1 training, n. is test'
		"""
		  -First label should be before for now.
		  -Since the X axes is same we do not take it into account
		  -First event training second is test
		  -

		  Questions:
		     1- Should I normalize scores for trained and test lists
		     2- In dot product should we add the similarities as we were doing for euclidean distance ?
		     3- The train set is smoothed, normalized, etc. But should we do the same for the test, how more realistic ? 

		  To Do:
		  	1- Make the cumulative distance/similarity calculation a seperate function.
		  	2- Make the error calculations in a seperate function.
		  	3- Try by deleting user names
		  	4- user based analysis ? threat or any other feature can be identified by looking to the textual history of user as well.
		  	   - Classify users according the quality, continuity of the information they give. When try to predict,
		  	     you can identify this users(type) relevance.
		  	   - use most informative users, measure their affect
		  	5- Spelling correction can be one according the user as well.
		  	6- use all events as training except 1, and use it as test, some sort of 10 fold cross validation.
		  	7- Change the w_list, it should come from the test set.
		  	8- delete non-informative ones, rt, @ : maybe informative but are we sure about information ?
		  	9- Train and test set should allow to have different days back.
		  	10- Differentiate between similarity and distance metrics. similarity accept max, distance accepts min of the scores. 
		"""
		#tserie_type = 'smoothed_w_tseries'
		#tserie_type = 'normalized_w_tseries'
		#tserie_type='normalized_w_byhighest'
		label = labels[0]
		all_1_euc_dist = []
		
		for name, event in self.events_dict.items():
			for l in labels:
				for w in w_list:
					if (w in event.words[l]) and (w not in getattr(event, tserie_type)[l]):
						word_t_series = event.calc_tseries(w, l, minuteForFrame, dayCount) # calc. relevant freq, t_series
					else:
						pass

		event_trained, event_test = self.structure_train_test_events(events[0], events[1], tserie_type, labels, w_list)
		print('Training & Test Events:', event_trained.name, '...', event_test.name)

		len_tserie_X_trained = len(getattr(event_trained, tserie_type)[l][w_list[0]])
		len_tserie_X_test = len(getattr(event_test, tserie_type)[l][w_list[0]])
		trained_X = event_trained.tweet_tseries[label][0][:len_tserie_X_trained] # get it from tweet time series. It is same for all events.
		test_X = event_test.tweet_tseries[label][0][:len_tserie_X_test]
		
		self.calc_mean_median(events[0])

		#print('\nNormalized, smoothed and normalized_by_highest:\n')
		# w_list1 = self.get_train_words_above2std(w_list, event_trained.normalized_w_tseries[label])
		# w_list2 = self.get_train_words_above2std(w_list, event_trained.smoothed_w_tseries[label])
		# w_list3 = self.get_train_words_above2std(w_list, event_trained.normalized_w_byhighest[label])
		#w_list = w_list

		# find similar words(spelling, syntax, semantics) from their behaviour in time!
		# simlist = []
		# for w in w_list:
		# 	if w in simlist: # if you find x, y do not check for y,x
		# 		continue
		# 	similars = self.find_similar_tserie(w, w_list, getattr(event_trained,tserie_type)[l])
		# 	print('--similar to:', w,':',similars)
		# 	simlist.append(similars[0][0])


		all_1_euc_dist = []

		print('Vector Matrix for Train:')
		trn_vector_matrix = []
		for y in range(0, len(trained_X)):
			trn_vector_matrix.append(self.crea_vectors_01(getattr(event_trained, tserie_type)[label], w_list, y))
		#print(*trn_vector_matrix, sep='\n')

		trn_vector_matrix = numpy.array(trn_vector_matrix)

		print('\nVector Matrix for Test:')
		tst_vector_matrix = []
		for y in range(0, len(test_X)):
			tst_vector_matrix.append(self.crea_vectors_01(getattr(event_test, tserie_type)[label], w_list, y))
		#print(*tst_vector_matrix, sep='\n')
		tst_vector_matrix = numpy.array(tst_vector_matrix)

		

		trn_dot_prod = self.get_dot_prod_array(trn_vector_matrix)
		#print('Calc dot products beforehand, trn:',trn_dot_prod)

		trn_elem_sum = [np.sum(v) for v in trn_vector_matrix]
		#print('Calc sum of the elements beforehand, trn:', trn_elem_sum)

		tst_dot_prod = self.get_dot_prod_array(tst_vector_matrix)
		#print('Calc dot products beforehand, tst:', tst_dot_prod)


		tst_elem_sum = [np.sum(v) for v in tst_vector_matrix]
		#print('Calc sum of the elements beforehand, tst:', tst_elem_sum)
		
		for i in range(0, len(test_X)):
			
			euc_dist_l = []
			tst_vector_matrix_i = tst_vector_matrix[i]
			tst_dot_prod_i = tst_dot_prod[i]
			tst_elem_sum_i = tst_elem_sum[i]

			for y in range(0, len(trained_X)):

				euc_dist_l.append(self.cos_dist2(trn_vector_matrix[y], trn_dot_prod[y], trn_elem_sum[y],  tst_vector_matrix_i, tst_dot_prod_i, tst_elem_sum_i))

			all_1_euc_dist.append(euc_dist_l)


		print('k is:', k)
		for k_index in range(1,k):
			print('k is:', k)
			print('Len of Test_X:', len(test_X))
			for seq_len in range(0, len(test_X)): #for all frame lengths

				# m x n matrix became (m-1)x(n-1)
				print('Cos Sim. Matrix for length:', seq_len)
				
				euc_dist_matrix = self.calc_dist_for_seq(all_1_euc_dist, seq_len) # calc. euc. dist. from one-to-one distances.
				#print('Distances for sequences:', euc_dist_matrix, sep='\n')
				

				if seq_len not in self.prediction_results:
						self.prediction_results[seq_len] = []

				for tst_i in range(0, len(test_X[seq_len:])):
					predictions = self.get_predictions_sim(euc_dist_matrix[tst_i], trained_X[seq_len:], k_index)
					
					if len(predictions) != 0:
						actual = test_X[seq_len:][tst_i]

						self.prediction_results[seq_len].append((actual, self.weighted_pred(predictions)))

						#self.prediction_results[seq_len].append((actual, numpy.mean(predictions)))
						#print('Actual:',actual, 'predictions:', predictions, 'raw_errors:', raw_errors)
					else:
						print('No Tweets to predict anything ! Seq. len & actual:', seq_len, test_X[seq_len:][tst_i])

			#print('Tf-IDF Prediction Results(tserie_type, k):', tserie_type, k)
			self.print_dict(self.prediction_results, 'trn01_'+ tserie_type+'-k'+str(k_index))
			print('Trn01 Calc RMSE:', tserie_type)
			self.print_dict(self.calc_rmse(self.prediction_results), 'trn01_'+ tserie_type+'k:'+str(k_index))
			self.prediction_results = {}

	def calc_by_vectors2(self, w_lists, labels, events, minuteForFrame, dayCount, tserie_type, k=1): # this use
		'First event is training, the second test.Later adapt it to fist n-1 training, n. is test'
		"""
		  -First label should be before for now.
		  -Since the X axes is same we do not take it into account
		  -First event training second is test
		  -

		  Questions:
		     1- Should I normalize scores for trained and test lists
		     2- In dot product should we add the similarities as we were doing for euclidean distance ?
		     3- The train set is smoothed, normalized, etc. But should we do the same for the test, how more realistic ? 

		  To Do:
		  	1- Make the cumulative distance/similarity calculation a seperate function.
		  	2- Make the error calculations in a seperate function.
		  	3- Try by deleting user names
		  	4- user based analysis ? threat or any other feature can be identified by looking to the textual history of user as well.
		  	   - Classify users according the quality, continuity of the information they give. When try to predict,
		  	     you can identify this users(type) relevance.
		  	   - use most informative users, measure their affect
		  	5- Spelling correction can be one according the user as well.
		  	6- use all events as training except 1, and use it as test, some sort of 10 fold cross validation.
		  	7- Change the w_list, it should come from the test set.
		  	8- delete non-informative ones, rt, @ : maybe informative but are we sure about information ?
		  	9- Train and test set should allow to have different days back.
		  	10- Differentiate between similarity and distance metrics. similarity accept max, distance accepts min of the scores. 
		"""
		#tserie_type = 'smoothed_w_tseries'
		#tserie_type = 'normalized_w_tseries'
		#tserie_type='normalized_w_byhighest'
		label = labels[0]
		all_1_euc_dist = []
		
		wlist_trn = w_lists[0] # just to use to calculate - a part of the cosine similarity
		wlist_trntst = w_lists[1]

		for name, event in self.events_dict.items():
			for l in labels:
				for w in wlist_trn:
					if (w in event.words[l]) and (w not in getattr(event, tserie_type)[l]):
						word_t_series = event.calc_tseries(w, l, minuteForFrame, dayCount) # calc. relevant freq, t_series
					else:
						pass

		event_trained, event_test = self.structure_train_test_events(events[0], events[1], tserie_type, labels, wlist_trn)
		print('Training & Test Events:', event_trained.name, '...', event_test.name)

		len_tserie_X_trained = len(getattr(event_trained, tserie_type)[l][wlist_trn[0]])
		len_tserie_X_test = len(getattr(event_test, tserie_type)[l][wlist_trn[0]])
		trained_X = event_trained.tweet_tseries[label][0][:len_tserie_X_trained] # get it from tweet time series. It is same for all events.
		test_X = event_test.tweet_tseries[label][0][:len_tserie_X_test]
		
		self.calc_mean_median(events[0])

		#print('\nNormalized, smoothed and normalized_by_highest:\n')
		# w_list1 = self.get_train_words_above2std(w_list, event_trained.normalized_w_tseries[label])
		# w_list2 = self.get_train_words_above2std(w_list, event_trained.smoothed_w_tseries[label])
		# w_list3 = self.get_train_words_above2std(w_list, event_trained.normalized_w_byhighest[label])
		#w_list = w_list2

		# find similar words(spelling, syntax, semantics) from their behaviour in time!
		# simlist = []
		# for w in w_list:
		# 	if w in simlist: # if you find x, y do not check for y,x
		# 		continue
		# 	similars = self.find_similar_tserie(w, w_list, getattr(event_trained,tserie_type)[l])
		# 	print('--similar to:', w,':',similars)
		# 	simlist.append(similars[0][0])

	
		all_1_euc_dist = []

		print('Trn matrix for just to calc. part/denom of the cosine similarity')
		trn_vector_matrix_big = []
		for y in range(0, len(trained_X)):
			trn_vector_matrix_big.append(self.crea_vectors_01(getattr(event_trained, tserie_type)[label], wlist_trn , y))
		#print(*trn_vector_matrix_big, sep='\n')

		trn_vector_matrix_big = numpy.array(trn_vector_matrix_big)

		print('Vector Matrix for Train:')
		trn_vector_matrix = []
		for y in range(0, len(trained_X)):
			trn_vector_matrix.append(self.crea_vectors_01(getattr(event_trained, tserie_type)[label], wlist_trntst , y))
		#print(*trn_vector_matrix, sep='\n')

		trn_vector_matrix = numpy.array(trn_vector_matrix)


		print('\nVector Matrix for Test:')
		tst_vector_matrix = []
		for y in range(0, len(test_X)):
			tst_vector_matrix.append(self.crea_vectors_01(getattr(event_test, tserie_type)[label], wlist_trntst, y))
		#print(*tst_vector_matrix, sep='\n')
		tst_vector_matrix = numpy.array(tst_vector_matrix)

		

		trn_dot_prod = self.get_dot_prod_array(trn_vector_matrix_big)
		#print('Calc dot products beforehand, trn:',trn_dot_prod)
		trn_vector_matrix_big = None #it was too big, free memory !!!

		trn_elem_sum = [np.sum(v) for v in trn_vector_matrix]
		#print('Calc sum of the elements beforehand, trn:', trn_elem_sum)

		tst_dot_prod = self.get_dot_prod_array(tst_vector_matrix)
		#print('Calc dot products beforehand, tst:', tst_dot_prod)


		tst_elem_sum = [np.sum(v) for v in tst_vector_matrix]
		#print('Calc sum of the elements beforehand, tst:', tst_elem_sum)
		
		for i in range(0, len(test_X)):
			
			euc_dist_l = []
			tst_vector_matrix_i = tst_vector_matrix[i]
			tst_dot_prod_i = tst_dot_prod[i]
			tst_elem_sum_i = tst_elem_sum[i]

			for y in range(0, len(trained_X)):

				euc_dist_l.append(self.cos_dist2(trn_vector_matrix[y], trn_dot_prod[y], trn_elem_sum[y],  tst_vector_matrix_i, tst_dot_prod_i, tst_elem_sum_i))

			all_1_euc_dist.append(euc_dist_l)


		print('k is:', k)
		for k_index in range(1,k):
			print('k is:', k)
			print('Len of Test_X:', len(test_X))
			for seq_len in range(0, len(test_X)): #for all frame lengths

				# m x n matrix became (m-1)x(n-1)
				print('Cos Sim. Matrix for length:', seq_len)
				
				euc_dist_matrix = self.calc_dist_for_seq(all_1_euc_dist, seq_len) # calc. euc. dist. from one-to-one distances.
				#print('Distances for sequences:', euc_dist_matrix, sep='\n')
				

				if seq_len not in self.prediction_results:
						self.prediction_results[seq_len] = []

				for tst_i in range(0, len(test_X[seq_len:])):
					predictions = self.get_predictions_sim(euc_dist_matrix[tst_i], trained_X[seq_len:], k_index)
					
					if len(predictions) != 0:
						actual = test_X[seq_len:][tst_i]

						self.prediction_results[seq_len].append((actual, self.weighted_pred(predictions)))

						#self.prediction_results[seq_len].append((actual, numpy.mean(predictions)))
						#print('Actual:',actual, 'predictions:', predictions, 'raw_errors:', raw_errors)
					else:
						print('No Tweets to predict anything ! Seq. len & actual:', seq_len, test_X[seq_len:][tst_i])

			#print('Tf-IDF Prediction Results(tserie_type, k):', tserie_type, k)
			self.print_dict(self.prediction_results, 'trn01_'+ tserie_type+'-k'+str(k_index))
			print('Trn01 Calc RMSE:', tserie_type)
			self.print_dict(self.calc_rmse(self.prediction_results), 'trn01_'+ tserie_type+'k:'+str(k_index))
			self.prediction_results = {}

	def find_similar_tserie(self, w, wlist, tserie_dict):
		'''
		Return most similar tserie of w based on word time series

		'''

		mostcossim = 0
		leastcossim = 1
		mostcandw = ''
		mincandw = ''
		wtserie = numpy.array(tserie_dict[w])
		print('wtserie:',w,':',tserie_dict[w])
		for k_w, ctserie in tserie_dict.items():
			if w != k_w:
				tempcossim = self.cos_sim(wtserie,np.array(ctserie))
				if tempcossim > mostcossim:
					mostcossim = tempcossim
					mostcandw = k_w
					print('more similar:',k_w,':', mostcossim,':',ctserie)

				if tempcossim < leastcossim:
					leastcossim = tempcossim
					mincandw = k_w
					print('less similar:', k_w,':', leastcossim,':', ctserie)



		return [(mostcandw, mostcossim), (mincandw,leastcossim)]




	def calc_by_vectors_tfidf(self, w_list, labels, events, minuteForFrame, dayCount, tserie_type, k=1, std_elim=0):
		'First event is training, the second test.Later adapt it to fist n-1 training, n. is test'
		"""
		  -First label should be before for now.
		  -Since the X axes is same we do not take it into account
		  -First event list is training second event list is test
		  -

		  Questions:
		     1- Should I normalize scores for trained and test lists
		     2- In dot product should we add the similarities as we were doing for euclidean distance ?
		     3- The train set is smoothed, normalized, etc. But should we do the same for the test, how more realistic ? 

		  To Do:
		  	1- Make the cumulative distance/similarity calculation a seperate function.
		  	2- Make the error calculations in a seperate function.
		  	3- Try by deleting user names
		  	4- user based analysis ? threat or any other feature can be identified by looking to the textual history of user as well.
		  	   - Classify users according the quality, continuity of the information they give. When try to predict,
		  	     you can identify this users(type) relevance.
		  	   - use most informative users, measure their affect
		  	5- Spelling correction can be one according the user as well.
		  	6- use all events as training except 1, and use it as test, some sort of 10 fold cross validation.
		  	7- Change the w_list, it should come from the test set.
		  	8- delete non-informative ones, rt, @ : maybe informative but are we sure about information ?
		  	9- Train and test set should allow to have different days back.
		  	10- Differentiate between similarity and distance metrics. similarity accept max, distance accepts min of the scores. 
		"""
		#tserie_type = 'smoothed_w_tseries'
		#tserie_type = 'normalized_w_tseries'
		#tserie_type = 'normalized_w_byhighest'
		label = labels[0]
		all_1_euc_dist = []
		
		for name, event in self.events_dict.items():
			for l in labels:
				for w in w_list:
					if (w in event.words[l]) and (w not in getattr(event, tserie_type)[l]):
						word_t_series = event.calc_tseries(w, l, minuteForFrame, dayCount) # calc. relevant freq, t_series
					else:
						pass

		event_trained, event_test = self.structure_train_test_events(events[0], events[1], tserie_type, labels, w_list)
		print('Training & Test Events:', event_trained.name, '...', event_test.name)

		len_tserie_X_trained = len(getattr(event_trained, tserie_type)[l][w_list[0]])
		len_tserie_X_test = len(getattr(event_test, tserie_type)[l][w_list[0]])
		trained_X = event_trained.tweet_tseries[label][0][:len_tserie_X_trained] # get it from tweet time series. It is same for all events.
		test_X = event_test.tweet_tseries[label][0][:len_tserie_X_test]
		
		self.calc_mean_median(events[0])
		
		# if std_elim > 0:
		# 	w_list = self.get_train_words_aboveNstd(w_list, event_trained.normalized_w_tseries[label], std_elim) #get_train_words_aboveNstd
		
		#w_list = w_list
		# return
		# exit()

		t0 = time.time() #measure run time!


		all_1_euc_dist = []

		trn_vector_matrix = []
		for y in range(0, len(trained_X)):
			trn_vector_matrix.append(self.crea_vectors_value(getattr(event_trained, tserie_type)[label], w_list, y))
		#print('Ten Raw Matrix:', trn_vector_matrix)
		
		trn_vector_matrix = numpy.array(trn_vector_matrix)
		trn_vector_matrix, approx_idf_array = self.calc_tfidf_from_matrix(trn_vector_matrix)
		#print('Tf-Idf Matrix for Train:',trn_vector_matrix)
		#print('approx_idf_array:', approx_idf_array)

		
		tst_vector_matrix = []
		for y in range(0, len(test_X)):
			tst_vector_matrix.append(self.crea_vectors_value(getattr(event_test, tserie_type)[label], w_list, y))
		#print('\nVector Matrix for Test, tfidf:', tst_vector_matrix)
		tst_vector_matrix = numpy.array(tst_vector_matrix)
		tst_vector_matrix = self.calc_tfidf_from_matrix_test(tst_vector_matrix, approx_idf_array)
		#print('Tf-Idf Matrix for Test, tfidf:', tst_vector_matrix)

		
		trn_dot_prod = self.get_dot_prod_array(trn_vector_matrix)
		#print('Calc dot products beforehand, trn:',trn_dot_prod)

		trn_elem_sum = [np.sum(v) for v in trn_vector_matrix]
		#print('Calc sum of the elements beforehand, trn:', trn_elem_sum)

		tst_dot_prod = self.get_dot_prod_array(tst_vector_matrix)
		#print('Calc dot products beforehand, tst:', tst_dot_prod)


		tst_elem_sum = [np.sum(v) for v in tst_vector_matrix]
		#print('Calc sum of the elements beforehand, tst:', tst_elem_sum)
		
		for i in range(0, len(test_X)):
			
			euc_dist_l = []
			tst_vector_matrix_i = tst_vector_matrix[i]
			tst_dot_prod_i = tst_dot_prod[i]
			tst_elem_sum_i = tst_elem_sum[i]

			for y in range(0, len(trained_X)):

				euc_dist_l.append(self.cos_dist2(trn_vector_matrix[y], trn_dot_prod[y], trn_elem_sum[y],  tst_vector_matrix_i, tst_dot_prod_i, tst_elem_sum_i))

			all_1_euc_dist.append(euc_dist_l)			

		for k_index in range(1,k):
			for seq_len in range(0, len(test_X)): #for all frame lengths

				# m x n matrix became (m-1)x(n-1)
				#print('Cos Sim. Matrix for length:', seq_len)
				
				euc_dist_matrix = self.calc_dist_for_seq(all_1_euc_dist, seq_len) # calc. euc. dist. from one-to-one distances.
				#print('Distances for sequences:', euc_dist_matrix, sep='\n')
				

				if seq_len not in self.prediction_results:
						self.prediction_results[seq_len] = []

				for tst_i in range(0, len(test_X[seq_len:])):
					predictions = self.get_predictions_sim(euc_dist_matrix[tst_i], trained_X[seq_len:], k_index)
					
					if len(predictions) != 0:
						actual = test_X[seq_len:][tst_i]

						self.prediction_results[seq_len].append((actual, self.weighted_pred(predictions)))

						#self.prediction_results[seq_len].append((actual, numpy.mean(predictions)))
						#print('Actual:',actual, 'predictions:', predictions, 'raw_errors:', raw_errors)
					else:
						print('No Tweets to predict anything ! Seq. len & actual:', seq_len, test_X[seq_len:][tst_i])

			print('Tf-IDF Prediction Results(tserie_type, k):', tserie_type, k)
			self.print_dict(self.prediction_results, 'tfidf_'+ tserie_type+'-k'+str(k_index))
			print('Tf-IDF Calc RMSE:', tserie_type)
			self.print_dict(self.calc_rmse(self.prediction_results), 'tfidf_'+ tserie_type+'k:'+str(k_index))
			self.prediction_results = {}

		print('inside run time of calc_by_vectors_tfidf:', t0-time.time())

	def calc_by_vectors_tfidf2(self, w_lists, labels, events, minuteForFrame, dayCount, tserie_type, k=1, std_elim=0):
		'First event is training, the second test.Later adapt it to fist n-1 training, n. is test'
		"""
		  -First label should be before for now.
		  -Since the X axes is same we do not take it into account
		  -First event list is training second event list is test
		  -

		  Questions:
		     1- Should I normalize scores for trained and test lists
		     2- In dot product should we add the similarities as we were doing for euclidean distance ?
		     3- The train set is smoothed, normalized, etc. But should we do the same for the test, how more realistic ? 

		  To Do:
		  	1- Make the cumulative distance/similarity calculation a seperate function.
		  	2- Make the error calculations in a seperate function.
		  	3- Try by deleting user names
		  	4- user based analysis ? threat or any other feature can be identified by looking to the textual history of user as well.
		  	   - Classify users according the quality, continuity of the information they give. When try to predict,
		  	     you can identify this users(type) relevance.
		  	   - use most informative users, measure their affect
		  	5- Spelling correction can be one according the user as well.
		  	6- use all events as training except 1, and use it as test, some sort of 10 fold cross validation.
		  	7- Change the w_list, it should come from the test set.
		  	8- delete non-informative ones, rt, @ : maybe informative but are we sure about information ?
		  	9- Train and test set should allow to have different days back.
		  	10- Differentiate between similarity and distance metrics. similarity accept max, distance accepts min of the scores. 
		"""
		#tserie_type = 'smoothed_w_tseries'
		#tserie_type = 'normalized_w_tseries'
		#tserie_type = 'normalized_w_byhighest'
		label = labels[0]
		all_1_euc_dist = []

		wlist_trn = w_lists[0] # just to use to calculate - a part of the cosine similarity
		wlist_trntst = w_lists[1]
		
		for name, event in self.events_dict.items():
			for l in labels:
				for w in wlist_trn:
					if (w in event.words[l]) and (w not in getattr(event, tserie_type)[l]):
						word_t_series = event.calc_tseries(w, l, minuteForFrame, dayCount) # calc. relevant freq, t_series
					else:
						pass

		event_trained, event_test = self.structure_train_test_events(events[0], events[1], tserie_type, labels, wlist_trn)
		print('Training & Test Events:', event_trained.name, '...', event_test.name)

		len_tserie_X_trained = len(getattr(event_trained, tserie_type)[l][wlist_trn[0]]) 
		len_tserie_X_test = len(getattr(event_test, tserie_type)[l][wlist_trn[0]])
		trained_X = event_trained.tweet_tseries[label][0][:len_tserie_X_trained] # get it from tweet time series. It is same for all events.
		test_X = event_test.tweet_tseries[label][0][:len_tserie_X_test]
		
		self.calc_mean_median(events[0])

		print('\nNormalized, smoothed and normalized_by_highest:\n')
		
		# if std_elim > 0:
		# 	w_list = self.get_train_words_aboveNstd(w_list, event_trained.normalized_w_tseries[label], std_elim) #get_train_words_aboveNstd
		
		#w_list = w_list
		# return
		# exit()
		t0 = time.time() # calc method run time
		all_1_euc_dist = []

		# print('Trn matrix for just to calc. part/denom of the cosine similarity')
		# trn_vector_matrix_big = []
		# for y in range(0, len(trained_X)):
		# 	trn_vector_matrix_big.append(self.crea_vectors_01(getattr(event_trained, tserie_type)[label], wlist_trn , y))
		# #print(*trn_vector_matrix_big, sep='\n')

		# trn_vector_matrix_big = numpy.array(trn_vector_matrix_big)

		trn_vector_matrix = []
		for y in range(0, len(trained_X)):
			trn_vector_matrix.append(self.crea_vectors_value(getattr(event_trained, tserie_type)[label], wlist_trn, y))
		#print('Ten Raw Matrix:', trn_vector_matrix)
		
		trn_vector_matrix = numpy.array(trn_vector_matrix)
		trn_vector_matrix, approx_idf_array = self.calc_tfidf_from_matrix(trn_vector_matrix)
		#print('Tf-Idf Matrix for Train:',trn_vector_matrix)
		#print('approx_idf_array:', approx_idf_array)

		print('Shape trn_vector_matrix:', trn_vector_matrix.shape)
		print('Len of wlist_train & approx_idf_array(equal?):', len(wlist_trn), len(approx_idf_array))
		small_approx_idf_array = []
		w_occ = []
		for i in range(0, len(wlist_trn)):
			if wlist_trn[i] in wlist_trntst:
				small_approx_idf_array.append(approx_idf_array[i])
				w_occ.append(1)
			else:
				w_occ.append(0)
		print('\nLen of wlist_trntst & small_approx_idf_array(equal?):', len(wlist_trntst), len(small_approx_idf_array))
		print('\nLen(should be same as trntst words) & W_occ list(1 occ, 0 not occ.):',len(w_occ), w_occ)
		
		
		tst_vector_matrix = []
		for y in range(0, len(test_X)):
			tst_vector_matrix.append(self.crea_vectors_value(getattr(event_test, tserie_type)[label], wlist_trntst, y))
		#print('\nVector Matrix for Test, tfidf:', tst_vector_matrix)
		tst_vector_matrix = numpy.array(tst_vector_matrix)
		tst_vector_matrix = self.calc_tfidf_from_matrix_test(tst_vector_matrix, small_approx_idf_array)
		#print('Tf-Idf Matrix for Test, tfidf:', tst_vector_matrix)

		
		trn_dot_prod = self.get_dot_prod_array(trn_vector_matrix)
		#print('Calc dot products beforehand, trn:',trn_dot_prod)

		trn_elem_sum = [np.sum(v) for v in trn_vector_matrix]
		#print('Calc sum of the elements beforehand, trn:', trn_elem_sum)

		w_occ_np = numpy.array(w_occ)
		w_occ_npbool = numpy.array(w_occ_np, dtype=bool)
		small_trn_vector_matrix = trn_vector_matrix[:,w_occ_npbool]
		print('Shape of small_trn_vector_matrix:', small_trn_vector_matrix.shape)
		trn_vector_matrix = None # free the space!

		tst_dot_prod = self.get_dot_prod_array(tst_vector_matrix)
		#print('Calc dot products beforehand, tst:', tst_dot_prod)


		tst_elem_sum = [np.sum(v) for v in tst_vector_matrix]
		#print('Calc sum of the elements beforehand, tst:', tst_elem_sum)
		


		for i in range(0, len(test_X)):
			
			euc_dist_l = []
			tst_vector_matrix_i = tst_vector_matrix[i]
			tst_dot_prod_i = tst_dot_prod[i]
			tst_elem_sum_i = tst_elem_sum[i]

			for y in range(0, len(trained_X)):

				euc_dist_l.append(self.cos_dist2(small_trn_vector_matrix[y], trn_dot_prod[y], trn_elem_sum[y],  tst_vector_matrix_i, tst_dot_prod_i, tst_elem_sum_i))

			all_1_euc_dist.append(euc_dist_l)			

		for k_index in range(1,k):
			for seq_len in range(0, len(test_X)): #for all frame lengths

				# m x n matrix became (m-1)x(n-1)
				#print('Cos Sim. Matrix for length:', seq_len)
				
				euc_dist_matrix = self.calc_dist_for_seq(all_1_euc_dist, seq_len) # calc. euc. dist. from one-to-one distances.
				#print('Distances for sequences:', euc_dist_matrix, sep='\n')
				

				if seq_len not in self.prediction_results:
						self.prediction_results[seq_len] = []

				for tst_i in range(0, len(test_X[seq_len:])):
					predictions = self.get_predictions_sim(euc_dist_matrix[tst_i], trained_X[seq_len:], k_index)
					
					if len(predictions) != 0:
						actual = test_X[seq_len:][tst_i]

						self.prediction_results[seq_len].append((actual, self.weighted_pred(predictions)))

						#self.prediction_results[seq_len].append((actual, numpy.mean(predictions)))
						#print('Actual:',actual, 'predictions:', predictions, 'raw_errors:', raw_errors)
					else:
						print('No Tweets to predict anything ! Seq. len & actual:', seq_len, test_X[seq_len:][tst_i])

			print('Tf-IDF Prediction Results(tserie_type, k):', tserie_type, k)
			self.print_dict(self.prediction_results, 'tfidf_'+ tserie_type+'-k'+str(k_index))
			print('Tf-IDF Calc RMSE:', tserie_type)
			self.print_dict(self.calc_rmse(self.prediction_results), 'tfidf_'+ tserie_type+'k:'+str(k_index))
			self.prediction_results = {}
		print('inside run time of calc_by_vectors_tfidf2:', t0-time.time())

	def weighted_pred(self, predictions):

		actual = predictions[0]

		weight_pred = 0.0
		sum_weights = 0.0
		for pred_tuple in predictions:
			weight_pred = math.fsum([weight_pred, pred_tuple[0] * pred_tuple[1]])
			sum_weights += pred_tuple[1]

		return	weight_pred/sum_weights

	def get_dot_prod_array(self, mtrx):
		'''

		Returns dot product of each vector in the matrix as an array.

		'''
		dot_prdct = []
		for m in mtrx:
			dot_prdct.append(np.sqrt(np.dot(m,m)))

		return dot_prdct

	def calc_tfidf_from_matrix_test(self, mtrx, approx_idf):
		'''

		Return tf-idf matrix in same dimensions

		Precondition: each matrix row contain a time frame, 0th, 1th, etc. elem in the matrix.
					  each row contains a vector of word occurrence values.

		'''

		doc_count_in_w_occ = self.calc_word_occ_per_doc(mtrx)
		print('doc counts in which words occur:')
		print(*doc_count_in_w_occ, sep='\n')
		all_doc_count = len(mtrx) # every row represent a doc
		print('all doc count:', all_doc_count)
		idf_array = approx_idf
		print('Idf values:', idf_array)

		#idf_array = numpy.array([idf if idf > 0 else 0.00001 for idf in idf_array])
		print('matrix in tf:', mtrx)
		for t in range(len(mtrx)):
			mtrx[t] = mtrx[t]*idf_array #product every line of the matrix with the idf array

		print('Test matrix after division tfidf:', *mtrx, sep='\n')
			# for w in range(len(mtrx[0])):
			# 	mtrx[t][w] = mtrx[t][w] * idf_array[w]

		return mtrx




	def calc_tfidf_from_matrix(self, mtrx):
		'''

		Return tf-idf matrix in same dimensions

		Precondition: each matrix row contain a time frame, 0th, 1th, etc. elem in the matrix.
					  each row contains a vector of word occurrence values.

		'''

		doc_count_in_w_occ = self.calc_word_occ_per_doc(mtrx)
		print('doc counts in which words occur:')
		print(*doc_count_in_w_occ, sep='\n')
		all_doc_count = len(mtrx) # every row represent a doc
		print('all doc count:', all_doc_count)
		idf_array = self.calc_w_idf(all_doc_count, doc_count_in_w_occ)
		print('Idf values:', *idf_array, end=', ')

		#idf_array = numpy.array([idf if idf > 0 else 0.00001 for idf in idf_array])
		print('\nLen & matrix in tf:', mtrx.shape, mtrx)
		for t in range(len(mtrx)):
			mtrx[t] = mtrx[t]*idf_array #product every line of the matrix with the idf array

		print('Train matrix after division tfidf:', *mtrx, sep='\n')
			# for w in range(len(mtrx[0])):
			# 	mtrx[t][w] = mtrx[t][w] * idf_array[w]

		return mtrx, idf_array

	def calc_w_idf(self, total_docs, doc_count_in_w_occ_array):
		'''
			Return idf values for each word from the occ_in_doc_count array.

		'''

		doc_count_in_w_occ_array_sm = numpy.array([c if c > 0 else 1 for c in doc_count_in_w_occ_array])
		return numpy.log(total_docs*(1/doc_count_in_w_occ_array_sm))
		# idf_array = numpy.array([0.0]*len(doc_count_in_w_occ_array))

		# for occ_count_index in range(len(doc_count_in_w_occ_array)):
		# 	idf_array[occ_count_index] = math.log(total_docs/doc_count_in_w_occ_array[occ_count_index])

		# return idf_array


	def calc_word_occ_per_doc(self, mtrx):
		'''

		Return l' that have for every word document counts in which this word occur.
		The order of the words remain as it is in the matrix columns.

		Precondition: each matrix row contain a time frame, 0th, 1th, etc. elem in the matrix.
					  each row contains a vector of word occurrence values/freq.

		'''
		doc_count_in_w_occ = [0.0]* len(mtrx[0])

		for w_value in range(len(mtrx[0])):

			for t in range(len(mtrx)):
				if mtrx[t][w_value] > 0:
					doc_count_in_w_occ[w_value] += 1

		return doc_count_in_w_occ



	def crea_vectors_value(self, event_words_dict, words, index):
		'''(dict, list, dict, list) -> list, list

			Returns two vectors on the basis of trn_words. Value of each word added to the same index in two vectors.

			>>> crea_vectors({'a':[3,4,2,5], 'b':[1,3,7,2], 'c':[4,5,8,0]}, ['a','b'], 3,{'a':[3,4,2,5], 'b':[1,3,7,2], 'd':[4,5,8,0]}, ['b', 'd'], 2)
			[5,2],[2,7]

		'''
		vector = []

		for w in words:
			
			if w in event_words_dict:
					vector.append(event_words_dict[w][index])
			else:
				vector.append(0)

		return vector


	def cos_sim(self, vtrn, vtst):
		'''() ->

		Return Cosine distance between vectors

		'''
		#print('In the method, len of vectors:', len(vtrn), len(vtst))
		#print('Sum of elements, trn, tst:', sum(vtrn), sum(vtst))
		if isinstance(vtrn, numpy.ndarray) and isinstance(vtst, numpy.ndarray):
			if np.sum(vtrn) == 0 or np.sum(vtst) == 0:
				return 0
			cossim = np.dot(vtrn, vtst) / (np.sqrt(np.dot(vtrn, vtrn)) * np.sqrt(np.dot(vtst, vtst)))
		else:
			if sum(vtrn) == 0 or sum(vtst) == 0:
				return 0
			cossim = sum([a*b for a, b in zip(vtrn, vtst)]) / (math.sqrt(sum([a*b for a, b in zip(vtrn, vtrn)])) * math.sqrt(sum([a*b for a, b in zip(vtst, vtst)]))) 

		return cossim

	def cos_dist2(self, vtrn, vtrn_dotted_sqrted, vtrn_summed, vtst, vtst_dotted_sqrted, vtst_summed):
		''' () ->

		optimized version of cos_dist. It uses beforehand calculated dot product and square rooted trained vectors

		Return Cosine distance between vtrn and vtst

		'''
		#print('In the method, len of vectors:', len(vtrn), len(vtst))
		#print('Sum of elements, trn, tst:', sum(vtrn), sum(vtst))
		if vtst_summed == 0 or vtrn_summed == 0:
			return 0
		cos_sim = np.dot(vtrn, vtst) / (vtrn_dotted_sqrted * vtst_dotted_sqrted) 
		#print('cos sim:', cos_sim)
		return cos_sim


	def crea_vectors_org(self, trn_event_dict, trn_words, trn_index, tst_event_dict, tst_word, tst_index):
		'''(dict, list, dict, list) -> list, list

			Returns two vectors on the basis of trn_words. Value of each word added to the same index in two vectors.

			>>> crea_vectors({'a':[3,4,2,5], 'b':[1,3,7,2], 'c':[4,5,8,0]}, ['a','b'], 3,{'a':[3,4,2,5], 'b':[1,3,7,2], 'd':[4,5,8,0]}, ['b', 'd'], 2)
			[5,2],[2,7]
		'''
		trn_vector = []
		tst_vector = []

		for w in trn_words:
			trn_vector.append(trn_event_dict[w][trn_index])
			if w in tst_event_dict:
				tst_vector.append(tst_event_dict[w][tst_index])
			else:
				tst_vector.append(0)

		return trn_vector, tst_vector



	def crea_vectors_01(self, event_words_dict, words, index):
		'''(dict, list, dict, list) -> list, list

			Returns two vectors on the basis of trn_words. Value of each word added to the same index in two vectors.

			>>> crea_vectors({'a':[3,4,2,5], 'b':[1,3,7,2], 'c':[4,5,8,0]}, ['a','b'], 3,{'a':[3,4,2,5], 'b':[1,3,7,2], 'd':[4,5,8,0]}, ['b', 'd'], 2)
			[5,2],[2,7]

		'''
		vector = []

		for w in words:
			
			if w in event_words_dict:
				if event_words_dict[w][index] > 0:
					vector.append(1)
				else:
					vector.append(0)
			else:
				vector.append(0)

		return vector

	def calc_rmse0(self, dict_err_per_seq):
		'''(dict) -> (dict)

		Returns a dict with rmse(root mean square error) calculated for each key-value pair of dict_err_per_seq.

		precondition: value in dict_err_per_seq is a list of (float, list) tuples.

		>>>calc_rmse({1:[(3,[5]),(2,[6]),(5,7)], 2:[(4,[4]),(5,[0]),(2,[3]),(3,[2]),(9,[10])]})
		{1: 2.8284271247461903, 2: 2.7202941017470885}
		'''
		rmse_dict = {}
		for k, v in dict_err_per_seq.items():
			if len(v) > 0:
				rmse_dict[k] = math.sqrt(math.fsum([(a[0]-a[1][0])**2 for a in v])/len(v)) #should be a[0]-a[1][0] in case predictions were given as a list
			else:
				print('There is not any prediction for the length:', k)

		return rmse_dict


	def calc_rmse(self, dict_err_per_seq):
		'''(dict) -> (dict)

		Returns a dict with rmse(root mean square error) calculated for each key-value pair of dict_err_per_seq.

		precondition: value in dict_err_per_seq is a list of (float, list) tuples.

		>>>calc_rmse({1:[(3,[5]),(2,[6]),(5,7)], 2:[(4,[4]),(5,[0]),(2,[3]),(3,[2]),(9,[10])]})
		{1: 2.8284271247461903, 2: 2.7202941017470885}
		'''
		rmse_dict = {}
		for k, v in dict_err_per_seq.items():
			if len(v) > 0:
				rmse_dict[k] = math.sqrt(math.fsum([(a[0]-a[1])**2 for a in v])/len(v)) #should be a[0]-a[1][0] in case predictions were given as a list
			else:
				print('There is not any prediction for the length:', k)

		return rmse_dict

		
	def print_dict(self, pr_dict, dictinfo):

		print('Errors per seq. length:')
		for k, v in pr_dict.items():
			print(dictinfo, k,':',v)
			
	def get_predictions_dist(self, dist_list, trained_indexes):
		if sum(dist_list) == 0:
			return []
		else:
			prediction_indexes = [i for i, x in enumerate(dist_list) if numpy.allclose(x,min(dist_list))]
			predictions = [trained_indexes[pred] for pred in prediction_indexes]
			return predictions

	def get_predictions_sim0(self, dist_list, trained_indexes):
		'''

		Return the index of the max

		'''
		if sum(dist_list) == 0:
			return []
		else:
			prediction_indexes = [i for i, x in enumerate(dist_list) if numpy.allclose(x,max(dist_list))]
			predictions = [trained_indexes[pred] for pred in prediction_indexes]
			return predictions

	def get_predictions_sim(self, dist_list, trained_indexes, k = 1):
		'''

		Returns index of the elements biggest k elements

		'''
		if sum(dist_list) == 0:
			return []
		else:
			if k+1 <= len(dist_list):#not to get index error, you can set k up to length of the prediction candidates length
				neg = k + 1
			else:
				neg= len(dist_list)


			prediction_indexes = [(i, x) for i, x in enumerate(dist_list) if x > sorted(dist_list)[-neg]] #have the index if it is in k biggest values.
			predictions = [(trained_indexes[pred[0]], pred[1]) for pred in prediction_indexes]
			return predictions
		
		

	def adjust_for_frame_count(self, adjust_list, seq_len):

		new_list = [];

		for elem_index in range(0, len(adjust_list)):
			if (elem_index+seq_len) == len(adjust_list):
				print('Before break, elem_index, seq_len, sum:', elem_index, seq_len, elem_index+seq_len)
				break
			else:
				new_list.append(elem_index+seq_len)
				print('Added elem_index, seq_len, sum, len(adjust_list):', elem_index, seq_len, elem_index+seq_len, len(adjust_list))

		return new_list

	def calc_dist_for_seq(self, distances, sample_count):

		len_test_instances = len(distances)
		len_train_instances = len(distances[0])
		all_new_distances = []
		actual_times = []

		for x in range(0, len_test_instances):
			temp_dist = []

			if x+sample_count < len_test_instances:

				for y in range(0, len_train_instances):

					if y + sample_count < len_train_instances:
						tmp_sum = 0
						
						for j in range(0, sample_count+1):
							
					 		tmp_sum += distances[x+j][y+j]      #[x+j][1][y+j][1]	
					else:
						break;
				
					temp_dist.append(tmp_sum)
				
			if len(temp_dist) == 0:
				break
			all_new_distances.append(temp_dist)

		return all_new_distances


	def get_available_words(self,event, tserie_type, label, word_list, segment_no):
		'''

		Return available words that occur at this segment_no frame of this event. Check the tserie type for selection.

		'''
		ok_words = []
		no_words = []
		for w in word_list:
			if getattr(event, tserie_type)[label][w][segment_no] == 0:
				no_words.append(w)
			else:
				ok_words.append(w)

		return ok_words

	def euc_dist(self, tr_ts_val_tuple_l):

		return math.sqrt(math.fsum([(a[0]-a[1])**2 for a in tr_ts_val_tuple_l]))

	def structure_w_tseries(self, event_trained, event_test, trained_X, tserie_type, label, w, y):

		trained_Y = getattr(event_trained, tserie_type)[label][w] # this should produce more balanced results.
		trained = [(a,b) for a, b in zip(trained_X, trained_Y)]
		trained = list(reversed(trained)) # Time was reversed in the normal array. Therefore reverse for the normal timeline with the test data.
		
		test_Y = getattr(event_test, tserie_type)[label][w]
		test_Y = [(a,b) for a, b in zip(trained_X, test_Y)]
		test_Y = list(reversed(test_Y[:len(trained)])) #test_Y, when not smoothed, is longer be careful

		return trained, test_Y

	def structure_train_test_events(self, train, test, tserie_type, labels, w_list):
		'Call time serie calculation methods according to single or blend events'
		if type(train) == type(list()) and len(train) > 1:
			event_trained = BlendEvent([self.events_dict[name] for name in train])
			
			for l in labels:
				for w in w_list:
					if w not in getattr(event_trained, tserie_type)[l]:
						word_t_series = event_trained.calc_tseries(w, l) # calc. relevant freq, t_series
						#print('Word and its tserie:', w, word_t_series)
		elif type(train) == type(list()) and len(train) == 1:
			event_trained = self.events_dict[train[0]]

		else:
			event_trained = self.events_dict[train]

		if type(test) == type(list()) and len(test) > 1:
			event_test = BlendEvent([self.events_dict[name] for name in test])
			
			for l in labels:
				for w in w_list:
					if w not in getattr(event_test, tserie_type)[l]:
						word_t_series = event_test.calc_tseries(w, l) # calc. relevant freq, t_series
						#print('Word and its tserie:', w, word_t_series)

		elif type(test) == type(list()) and len(test) == 1:
			event_test = self.events_dict[test[0]]

		else:
			event_test = self.events_dict[test]

		return event_trained, event_test

	
	def calc_euc_dist(self, test_seq, trained_seq):
		return (trained_seq[-1][0],sqrt(math.fsum([(a[1]-b[1])**2 if not numpy.allclose(a[1], b[1]) else 0 for a, b in zip(test_seq, trained_seq)])))


	def get_sub_sequences(self, sample_count, complete_list):
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

	
	def calc_mean_median(self, train_events):
		label = 'before'
		product_sum = 0
		tweet_count = 0
		e_tserie_list = []
		e_tserie = ([],[])

		print('Event name in Median Calc:')
		for name in train_events:
			print(name, end=', ')
			e = self.events_dict[name]
			e_tserie = (e.tweet_tseries[label][0], e.tweet_tseries[label][1])

			e_tserie_list.append(e_tserie)
			
			tweet_count += sum(e_tserie[1])
			product_sum += sum([a*b for a, b in zip(e_tserie[0], e_tserie[1])])

		mean = product_sum/tweet_count
		print('\n\nSum of products:',product_sum,'All Tweet count:', tweet_count, 'Mean:', mean )

		i = 1
		median_tweet_count = tweet_count/2
		median = 0
		sum_tweets = 0

		while sum_tweets < median_tweet_count:
			for ts_tuple in e_tserie_list:
				#print(ts_tuple[1])
				sum_tweets += ts_tuple[1][-i]
			median = ts_tuple[0][-i]
			#print('Median Temp:', median)
			i +=1

		print('median tweet count is:', median_tweet_count)
		print('sum tweet count, median taken from:', sum_tweets)
		print('median hour:', median)

		self.mean_of_tweets = mean
		self.median_of_tweets = median
		return (self.mean_of_tweets, self.median_of_tweets)

	def plot_tserie_list(self, x_axe, y_axes_list, plot_names, graphTitle, x_label, y_label, file_name, sample_count_based_error ):
		line_colors=['blue', 'green','red', 'cyan', 'magenta', 'yellow', 'black', 'white']
		line_style = ['--']
		line_markers = []
		
		fig = matplotlib.pyplot.figure(figsize=(25,20)) #  fig size should vary according day*24
		matplotlib.pyplot.grid(True) # ???
		font = {'weight':'bold', 'size':22}
		matplotlib.rc('font', **font)
		matplotlib.rc('lines', lw=4)
		if sample_count_based_error:
			matplotlib.pyplot.xlim(0, x_axe[-1])
		else:
			matplotlib.pyplot.xlim(x_axe[-1], 0)
		
		i = 0
		for y_axe in y_axes_list:
			#print('Len of X and Y axe:', len(x_axe), len(y_axe))
			#print('X and Y axe:', x_axe, y_axe)
			plot(x_axe[:len(y_axe)], y_axe, color= line_colors[i], label=plot_names[i])
			i += 1
		
		print('X axe and its Prediction:')
		for i in range(0,len(y_axes_list[0])):
			print(x_axe[i], y_axes_list[0][i]) # Enable this to get the print of plotted tserie.

		legend(loc='upper right', fontsize=22)
		ylabel(y_label,fontsize = 30, fontweight='bold')
		xlabel(x_label, fontsize = 30, fontweight='bold')
		matplotlib.pyplot.title(graphTitle)
		#fig.savefig('/home/hurrial/Desktop/Graphs/Euc/'+file_name+'.png',format='png', facecolor='w',edgecolor='w', orientation='portrait', linewidth=50.0)

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

			


	def get_train_test_word_counts(self, n, labels, events):
		'Make use up to that time known word counts of both train and test events'

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
		for w, c in words1.most_common():
			if words1[w] > n and words2[w] > n: # Take just the train set to identify most used words.
				w_list.append(w)
				print(w,':', words1[w], words2[w])

		return w_list

	def get_train_words(self, n, labels, events):
		'''

		Return words that occur in the training events, and print their counts

		'''
		l = labels[0]
		words1 = Counter()
		for ename in events:
			words1 += self.events_dict[ename].words[l]

		wlist = []
		for w, c in words1.most_common():
			if words1[w] > n:
				wlist.append(w)
				#print(w+':'+str(words1[w]))

		print('\n')
		return wlist

	def get_TrnTstIntersect_words(self, n, labels, train_events, test_events):
		'''

		least_wc is applicable just for train words!
		'''

		l = labels[0]
		words1 = Counter()
		words2 = Counter()

		for ename in train_events:
			words1 += self.events_dict[ename].words[l]

		for ename in test_events:
			words2 += self.events_dict[ename].words[l]

		wlist = []
		for w, c in words1.most_common():
			if words1[w] > n and words2[w] > 0:
				wlist.append(w)
				#print(w+':'+str(words1[w]))

		print('\n')
		return wlist
		

	def get_train_words_aboveNstd(self, w_list, w_tseries_dict, n):
		
		w_take = []
		w_ignore = []

		for w in w_list:
			if max(w_tseries_dict[w]) > (numpy.mean(w_tseries_dict[w]) + n*numpy.std(w_tseries_dict[w])):
				w_take.append(w)
			else:
				w_ignore.append(w)

		print('.........Nstd is:', n)
		print('W_take:\n', w_take, '\nW_ignore\n:',w_ignore)
		return w_take

	



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


# Crafting Code:
#def 