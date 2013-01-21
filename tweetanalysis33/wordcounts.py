
import sys
#sys.path.append("..")


from tweetprocessing33.tweetsfeatures import Tweetsfeatures
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
from collections import Counter

from pylab import *
# from time import clock, time

#Notes:
# Create running average Graphs.
# Make it to work for particular events
# Store in a dict- word:timeseries for it
# Vector similarity measures ? How can we discover related words by these similarity.
# Create methods for Tweet based and CrossDomainWord relative frequencies.

class Event:
	"Events has an object that contains, event time, event place, used words, ..."

	def __init__(self, e_name, e_place, e_time):
		self.event_place = e_place
		self.event_time = e_time
		self.event_name = e_name
		self.event_tweets = []

class SingleWordAnalysis():
	"Statistical analysis of Tweets"
	"""
	Currently it uses Tweetfeatures objects to calculate statistical measures of word use in different tweet classes.
	Tweets could be in different classes like before, during, after. 
	-- Later, category type and count can be done generic.
	
	example usage:
	...

	"""

	def __init__(self, frogged_file=None, dutch_words_file=None, stop_words_file=None, events=None, event_times=None):
		"Set the file values"

		self.events=events
		self.tf = Tweetsfeatures(frogged_file)
		self.tf.set_tweets(u=1, ht=1, p=1) # remove urls, hashtags and punctuation

		self.stop_words = [] #only if it has any element in, will taken into account.

		if stop_words_file != None: # implement exception control
			stop_words_f = codecs.open(stop_words_file,"r","utf-8")
		
			with stop_words_f as f:
				for line in f:
					stop_words_tmp = line.split(', ')
					for sw in stop_words_tmp:
						self.stop_words.append(sw[1:-1])

		# self.dutch_words_dict = {}
		# if dutch_words_file != None:
		# 	dutch_words_f = codecs.open(dutch_words_file,"r","utf-8")

		# 	with dutch_words_f as f:
		# 		for line in f:
		# 			key, val = line.split('\t')
		# 			self.dutch_words_dict[key] = int(val)

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
		self.begintime = datetime.datetime(2012,12,31,23,59,0) # for this particular event
		self.endtime = datetime.datetime(2012,1,1,1,0,0)
		self.event_times = event_times
		self.before_tweets = []
		#self.t_before_smallest = datetime.datetime("2013","01","01","00",minute,second)
		# self.t_before_smallest = datetime.datetime.now()
		# self.t_before_biggest = datetime.datetime.now() - datetime.timedelta(days=3*365)
		# print("Initial Smallest:", self.t_before_smallest)
		# print("Initial Biggest:", self.t_before_biggest)
		#print(dutch_words_file, stop_words_file, frogged_file)


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
			#print("in the event ...:", t.event, "Tweet:", i)
			
			if t.event in self.events: #for this event
				
				
				if t.time < self.begintime:
					self.begintime = t.time

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
					
		# Ask Maarten: values and sum does not work properly.
		# self.all_before_word_count = sum(self.counter_before.values())
		# self.all_during_word_count = sum(self.counter_during.values())
		# self.all_after_word_count = sum(self.counter_after.values())
		
		print("Twente Ajax Before, During, After, Sum Tweet Count:", tweet_count_tweaja_before, tweet_count_tweaja_during, \
		   tweet_count_tweaja_after, tweet_count_tweaja_before+tweet_count_tweaja_during+tweet_count_tweaja_after)
		#exit()
		self.all_words_counter = self.counter_before + self.counter_during + self.counter_after
		self.word_list = list(self.all_words_counter)

		# i=0
		# for t in self.tweets_for_this_event:
		# 	print(t.get_wordsequence())
		# 	i += 1
		# 	if i%100 == 0:
		# 		input('tweets for this event ---- 100')


	def calc_words_freq(self):
		for w in self.word_list:
			if (self.counter_before[w] + self.counter_during[w] + self.counter_after[w]) > 0:

				#self.freq_before_dict[w] = self.counter_before[w]/self.all_before_word_count
				
				self.freq_before_dict[w] = self.counter_before[w]/len(self.before_tweets) # freq according tweet count.
				self.freq_during_dict[w] = self.counter_during[w]/self.all_during_word_count
				self.freq_after_dict[w] = self.counter_during[w]/self.all_after_word_count

				# print(w, self.freq_before_dict[w])
				# print(w, self.freq_during_dict[w])
				# print(w, self.freq_after_dict[w])
			


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
		#input("Press Enter ..----------------- to continue")
		for w, c in self.word_list_rest.most_common():
			if w[0] != '@' and len(w)>1:
				print(w, "sum:", self.word_list_rest[w], "b:",self.counter_before_rest[w], "d:", self.counter_during_rest[w], "a:", self.counter_after_rest[w])

		print("End of rest words list")
		# for word, count in self.counter_before_rest.most_common(150):
		# 	print(word, count)

		# input("Press Enter .-----------------: End Before")

		# for word, count in self.counter_during_rest.most_common(150):
		# 	print(word, count)

		# input("Press Enter .-----------------: End During")

		# for word, count in self.counter_after_rest.most_common(150):
		# 	print(word, count)

		# input("Press Enter .-----------------: End after")

	def get_BeginEndTime(self):
		print('\n Begintime:',self.begintime, '\n Endtime',self.endtime)
		input("Press Enter .. ----------------: End After")

	
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

			#xlabels.append(date2num(interval))


		return (xlabels, xvalues)

	def running_average_1(self, t_series_l):
		"first version of running_average()-middle element based"
		r_average = []
		av = 0
		divide_by = 4 # 3 elems + 1 for the weight of the middle one = 4
		for prev,item,next in self.neighborhood(t_series_l):
			print (prev, item, next)

			if prev == None:
				pass
			elif next == None:
				(prev + item*2)/(divide_by-1)
			else:	
				av = (prev+item*2+next)/divide_by
			
			r_average.append(av)

		return r_average # or 4

	def running_average_2(self, t_series_l):
		"second version of running_average()-.Wrong Temporal order"
		r_average = []
		av = 0
		divide_by = 7 # 3 elems + 1 for the weight of the middle one = 4
		for prev2, prev1, current in self.neighborhood(t_series_l):
			print (prev2, prev1, current)

			if prev2 == None:
				continue;
			else:
				av=(prev2 + 2*prev1 + 4*current)/divide_by
			
			r_average.append(av)

		return r_average # or 4

	def running_average(self, t_series_l):
		"returned list has 2 elements less than normal one, make the change in plotting for the other list"
		r_average = []
		av = 0
		divide_by = 7 # 3 elems + 1 for the weight of the middle one = 4
		for current, next1, next2 in self.neighborhood(t_series_l):
			print (current, next1, next2)

			av=(4*current + 2*next1+next2)/divide_by
			
			r_average.append(av)

		return r_average # or 4

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

	def neighborhood_2(self, iterable):
		"2. version of neighborhood(), wrong temporal order"
		iterator = iter(iterable)
		prev1 = None
		prev2 = None

		current = iterator.__next__()  # throws StopIteration if empty.
		for next in iterator:
			yield (prev2, prev1, current)
			prev2 = prev1
			prev1 = current
			current = next

	def neighborhood_1(self, iterable):
		"1. version of neighborhood()"
		iterator = iter(iterable)
		prev = None
		item = iterator.__next__()  # throws StopIteration if empty.
		for next in iterator:
			yield (prev,item,next)
			prev = item
			item = next
		yield (prev,item,None)



	def plot_word(self, w, minutes_for_time_period, day_back_count, withTweetCount, is_running_average): #use n to indicate number of words to make plot for

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
		w_st_dev=sqrt(sum(w_st_power_diff)/len(w_mean_freq_list))
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


	def fast_plot_word():




	def plot_mostCommonWords_RelFreqWithTweets(self, n, min, withTweetCount = True): #use n to indicate number of words to make plot for

		line_colors=['blue', 'green','red', 'cyan', 'magenta', 'yellow', 'black', 'white']
		line_style = ['--']
		line_markers = []
		minutes_for_time_period = 30
		day_back_count = 8

		plotted_words = ''

		fig = matplotlib.pyplot.figure(figsize=(50,100)) #  'module' object is not callable
		matplotlib.pyplot.grid(True)

		matplotlib.pyplot.title('Title')

		i=0
		if withTweetCount == True:
			time_list_for_tweets = self.calc_time_list_for_tweets()

			axes = self.calc_time_list_for_time_intervals(sorted(time_list_for_tweets), minutes_for_time_period, day_back_count)
			newTweetCount = []

			#newTweetCount = [x/4 for x in axes[1]] # divide all tweet counts by 2, normalization

			newTweetCount = axes[1]

			#plot(axes[0], newTweetCount, color= line_colors[0]) # Plot Tweet count Time series.
			i += 1
		 
		for w, v in self.all_words_counter.most_common(n):		

			time_list_for_a_word = self.calc_time_list_for_word(w)

			axes = self.calc_time_list_for_time_intervals(sorted(time_list_for_a_word))
			
			w_time_per_count = []

			w_time_per_count=[a/b for  a, b in zip(axes[1], newTweetCount)] # Relative to Tweet count.

			plot(axes[0], w_time_per_count, color=line_colors[i])
			plotted_words += '-'+w

			# *** For mean freq Line, Be careful for the color when plot many words.
			#w_mean_freq_list = []
			# for x in de_time_per_count:
			# 	w_mean_freq_list.append(self.freq_before_dict[w])
			# plot(axes[0], de_mean_freq, color=line_colors[i+1]) # Plot the mean for this word for comparison. 

			print(w, '-is-', line_colors[i])

			i += 1
			
		fig.savefig('/home/ali-hurriyetoglu/Desktop/graph'+plotted_words+'-'+str(minutes_for_time_period)+'minPeriod'+'-'+str(day_back_count)+'daysBack'+'.png',format='png', facecolor='w',edgecolor='w', orientation='portrait')

	def plot_Most_relFreqAcrossCategoriesWithWords_before(self, n=6, withTweetCount = False): #use n to indicate number of words to make plot for

		line_colors=['blue', 'green','red', 'cyan', 'magenta', 'yellow', 'black'] # 'white' not used
		line_style = ['--']
		line_markers = []
		plotted_words = ''
		minutes_for_time_period = 30
		day_back_count = 8

		fig = matplotlib.pyplot.figure(figsize=(25,20)) #  'module' object is not callable
		matplotlib.pyplot.grid(True)

		matplotlib.pyplot.title('Title')

		i=0
		if withTweetCount == True:
			time_list_for_tweets = self.calc_time_list_for_tweets()
			
			newTweetCount = []
			axes = self.calc_time_list_for_time_intervals(time_list_for_tweets, minutes_for_time_period, day_back_count)
			#newTweetCount = [x/4 for x in axes[1]] # divide all tweet counts by 2, normalization

			plot(axes[0], newTweetCount, color= line_colors[0])
			print('Tweet Count is-', line_colors[i])
			i += 1

		
		for w, v in self.sort_dict(self.relative_freq_before_dict):		
			if w[0] != '@' and len(w)>1:
				time_list_for_a_word = self.calc_time_list_for_word(w)
				
				axes = self.calc_time_list_for_time_intervals(time_list_for_a_word)
				if w in ['amsterdam', 'zondag', 'weekend']:
					plot(axes[0], axes[1], color=line_colors[i])

				print(w, '-is-', line_colors[i])
				print(i)

				i += 1
				if i == n+1:
					break

		fig.savefig('/home/ali-hurriyetoglu/Desktop/graph'+plotted_words+str(minutes_for_time_period)+'minPeriod'+str(day_back_count)+'daysBack'+'.png',format='png', facecolor='w',edgecolor='w', orientation='portrait')

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

