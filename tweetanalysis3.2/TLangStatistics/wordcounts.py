
import tweetsfeatures
import codecs
import operator
import datetime

# import pytz
import numpy
import pandas
import matplotlib

# from pandas import *
# from numpy import *
# from datetime import *
# from pytz import *

from collections import defaultdict

from matplotlib import pyplot
from matplotlib.dates import date2num
# from datetime import datetime
from tweetsfeatures import Tweetsfeatures #Do not use '*' , you loose track of classes. It brings everything, system may be confused.
from collections import Counter

from pylab import *
# from time import clock, time


class SingleWordAnalysis():
	"Statistical analysis of Tweets"
	"""
	Currently it uses Tweetfeatures objects to calculate statistical measures of word use in different tweet classes.
	Tweets could be in different classes like before, during, after. 
	-- Later, category type and count can be done generic.
	
	example usage:
	...

	"""

	def __init__(self, frogged_file, dutch_words_file=None, stop_words_file=None):
		"Set the file values"

		tweet_file = frogged_file

		self.tf = Tweetsfeatures(tweet_file)
		self.tf.set_tweets(u=1, ht=1, p=1) # remove urls, hashtags and punctuation

		self.stop_words = [] #only if it has any element in, will taken into account.

		if stop_words_file != None: # implement exception control
			stop_words_f = codecs.open(stop_words_file,"r","utf-8")
		
			with stop_words_f as f:
				for line in f:
					stop_words_tmp = line.split(', ')
					for sw in stop_words_tmp:
						self.stop_words.append(sw[1:-1])

		self.dutch_words_dict = {}
		if dutch_words_file != None:
			dutch_words_f = codecs.open(dutch_words_file,"r","utf-8")

			with dutch_words_f as f:
				for line in f:
					key, val = line.split('\t')
					self.dutch_words_dict[key] = int(val)

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
		self.word_list = [] #keeps all words for iteration, list, make it counter (union)
		self.word_list_rest = Counter() # keep all words and their counts for iteration
		#self.t_before_smallest = datetime.datetime("2013","01","01","00",minute,second)
		# self.t_before_smallest = datetime.datetime.now()
		# self.t_before_biggest = datetime.datetime.now() - datetime.timedelta(days=3*365)
		self.ht = "psvv"
		# print("Initial Smallest:", self.t_before_smallest)
		# print("Initial Biggest:", self.t_before_biggest)
		#print(dutch_words_file, stop_words_file, frogged_file)
		self.time_series = None
		self.time_list = []

		self.time_list_geveegd = []
		self.time_list_trefzekerder = []


	def count_words(self):
		"Count words for each category"
		i = 0
		for t in self.tf.tweets:
			if t.get_label() == 'before':
				for w in t.get_wordsequence():
					if w in self.dutch_words_dict:#this can be coded just once for all categories.
						self.counter_before[w] += 1
						self.word_list.append(w)
					else:
						self.counter_before_rest[w] += 1

					# if t.event == self.ht: #put all times in a list and sort them and print them.
					if w == 'morgen':
						self.time_list.append(t.time)

					if w == 'schiet':
						self.time_list_geveegd.append(t.time)

					if w == 'trefzekerder':
						self.time_list_trefzekerder.append(t.time)
					# if t.time < self.t_before_smallest:
					# 	self.t_before_smallest = t.time
					# 	print("smaller:", self.t_before_smallest)
					# elif t.time > self.t_before_biggest:
					# 	self.t_before_biggest = t.time
					# 	i += 1
					# 	if (i % 3) == 0:
					# 		print("bigger:", self.t_before_biggest)


			if t.get_label() == 'during':
				for w in t.get_wordsequence():
					if w in self.dutch_words_dict:
						self.counter_during[w] += 1
					else:
						self.counter_during_rest[w] += 1

					# if t.event == self.ht: #put all times in a list and sort them and print them.
					if w == 'morgen':
						self.time_list.append(t.time)
				
					if w == 'schiet':
						self.time_list_geveegd.append(t.time)

					if w == 'trefzekerder':
						self.time_list_trefzekerder.append(t.time)

			if t.get_label() == 'after':

				for w in t.get_wordsequence():
					if w in self.dutch_words_dict:
						self.counter_after[w] += 1
					else:
						self.counter_after_rest[w] += 1

					# if t.event == self.ht: #put all times in a list and sort them and print them.
					if w == 'morgen':
						self.time_list.append(t.time)

					if w == 'schiet':
						self.time_list_geveegd.append(t.time)

					if w == 'trefzekerder':
						self.time_list_trefzekerder.append(t.time)

		self.all_before_word_count = sum(self.counter_before.values())
		self.all_during_word_count = sum(self.counter_during.values())
		self.all_after_word_count = sum(self.counter_after.values())
		self.word_list = list(self.counter_before + self.counter_during + self.counter_after)
		self.word_list_rest = self.counter_before_rest + self.counter_during_rest + self.counter_after_rest
		#print(self.word_list)
		# self.time_series = Series(0, sorted(self.time_list))
		# print(sorted(self.time_list))
			# num_dates = [date2num(d) for d in sorted(self.time_list)]
			# histo = numpy.histogram(num_dates)
			# cumulative_histo_counts = histo[0].cumsum()
			# bin_size = histo[1][1]-histo[1][0]
			# pyplot.bar(histo[1][:-1], cumulative_histo_counts, width=bin_size)
			# pyplot.plot(histo[1][1:], cumulative_histo_counts)

			# ts= Series()

		# ts.plot()

		
		

		begintime = datetime.datetime(2012,5,19,11,0,0)
		endtime = datetime.datetime(2012,5,20,3,0,0)
		xvalues = []
		xvalues_geveegd = []
		xvalues_trefzekerder = []
		xlabels = []

		interval = begintime
		while interval < endtime:
			nextinterval = interval + datetime.timedelta(0,3600*1)
			#nextinterval = interval + datetime.timedelta(hours=1)
			count = 0
			for t in self.time_list:
				if t >= interval and t < nextinterval:
					count += 1
			xvalues.append(count)

			count_geveegd = 0
			for t in self.time_list_geveegd:
				if t >= interval and t < nextinterval:
					count_geveegd += 1
			xvalues_geveegd.append(count_geveegd)

			count_trefzekerder = 0
			for t in self.time_list_trefzekerder:
				if t >= interval and t < nextinterval:
					count_trefzekerder += 1
			xvalues_trefzekerder.append(count_trefzekerder)
			#print(count_trefzekerder, "-----")


			xlabels.append(date2num(interval))
			interval = nextinterval
		
		for x in self.time_list_trefzekerder:# important range controll
			pass
			#print(x)
			if x < begintime or x > endtime:
				pass
				#print("out of range")

		# drng = pandas.date_range(begintime, periods=218, freq='H')
		# print(drng[0],drng[:-1], len(drng), len(xvalues))
		# ts = pandas.Series(xvalues, index=drng)
		# ts= ts.cumsum()
		# ts.plot()
		# exit()

		fig = matplotlib.pyplot.figure(figsize=(15,10)) #  'module' object is not callable
		matplotlib.pyplot.grid(True)

		matplotlib.pyplot.title('Title')
		#matplotlib.pyplot.plot(xlabels,xvalues,"morgen",xlabels, xvalues_geveegd, "geveegd")
		#matplotlib.pyplot.plot(xlabels,xvalues,'r-',xlabels, xvalues_geveegd,'b-', xlabels, xvalues_trefzekerder, 'g-')
		plot(xlabels, xvalues, color='red')
		plot(xlabels, xvalues_geveegd, color='blue')
		plot(xlabels, xvalues_trefzekerder, color='green')

		#xlim(0, 45)

		#matplotlib.pyplot.plot(xlabels,xvalues_geveegd)
		fig.savefig('/home/ali-hurriyetoglu/Desktop/graph.png',format='png', facecolor='w',edgecolor='w', orientation='portrait')

		#exit()


	def calc_words_freq(self):
		for w in self.word_list:
			if (self.counter_before[w] + self.counter_during[w] + self.counter_after[w]) > 4:

				#print(self.counter_before[w], self.all_before_word_count) #: check all words

				self.freq_before_dict[w] = self.counter_before[w] / self.all_before_word_count
				self.freq_during_dict[w] = self.counter_during[w] / self.all_during_word_count
				self.freq_after_dict[w] = self.counter_during[w] / self.all_after_word_count
			# elif (self.counter_before[w] == 4):
			# 	print("B::", w)
			# elif (self.counter_during[w] == 4):
			# 	print("D::", w)
			# elif (self.counter_after[w] == 4):
			# 	print("A::", w)


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


	def get_sorted_rel_freq(self):#adjust this method to be calleble for different dicts and different thresholds
		self.print_sorted(self.relative_freq_before_dict, self.counter_before)
		input("Press Enter ..-----------------: End Before")
		input("Press Enter ..-----------------: End Before")
		input("Press Enter ..-----------------: End Before")
		self.print_sorted(self.relative_freq_during_dict, self.counter_during)
		input("Press Enter .. ----------------: End During")
		input("Press Enter .. ----------------: End During")
		input("Press Enter .. ----------------: End During")
		self.print_sorted(self.relative_freq_after_dict, self.counter_after)
		input("Press Enter .. ----------------: End After")

	def get_sorted_freq():
		pass
	

	def print_sorted(self, d, c): #d:dict, c:counter
		values = sorted(d.items(), key= operator.itemgetter(1), reverse= True)
		
		i = 1
		for k, v in values:
			print(k, v, c[k])
			i += 1

			if i % 500 == 0:
				input("Press Enter to Continue...")
				print('..................................')

	def print_rest_words(self, counter_rest=None):#words that do not occur in sonar, and eliminated.
		print("Count of words in Rest words in before - during - after")
		#input("Press Enter ..----------------- to continue")
		for w, c in self.word_list_rest.most_common():
			if w[0] != '@' and len(w)>1:
				print(w, "sum:", self.word_list_rest[w], "b:",self.counter_before_rest[w], "d:", self.counter_during_rest[w], "a:", self.counter_after_rest[w])

		print("End of rest words list")
		# for word, count in self.counter_before_rest.most_common(150):
		# 	print(word, count)

		# input("Press Enter ..-----------------: End Before")

		# for word, count in self.counter_during_rest.most_common(150):
		# 	print(word, count)

		# input("Press Enter ..-----------------: End During")

		# for word, count in self.counter_after_rest.most_common(150):
		# 	print(word, count)

		# input("Press Enter ..-----------------: End after")


	def timerel(event_begin,event_end,tweet_time):
		if (event_begin > tweet_time):
			rel = "before"
		elif event_end < tweet_time:
			rel = "after"
		else:
			rel = "during"    
		return rel

	def get_sorted_freq(self):
		pass






		# i = 0
		# for item in self.relative_freq_before_dict:
		# 	if self.relative_freq_before_dict[item] > 5:
		# 		print(item, self.relative_freq_before_dict[item], self.counter_before[item])
		# 		i += 1
		# 		if i % 30 == 0:
		# 			input("Press Enter to Continue...")
		# 			print('..................................')

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




# Code Sample :
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
# # ---------------------------------------------------------------------------------------------------------------------------------

