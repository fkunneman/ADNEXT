#! /usr/bin/env python

from __future__ import division
import codecs
import re
#import nltk
import datetime
from collections import defaultdict

class Tweetsfeatures():
	"container of tweetfeatures"
	"""
	instance starts off with an inputted tweetfile 
	the file contains tweettokens as a result of frog parsing
	the file should have the format [tweetnumber]\t[label]\t[word]\t[lemma]\t[morph.units]\t[pos]\t[keyword (based on which tweet was searched)]\t[username]\t[time_posted]\n
	an instance can be manipulated by sequences of different units and different features like ngrams
	instances can be outputted in different formats, like sparse
	
	example usage:
	collection = tweetsfeatures.Tweetsfeatures([frogged_file])
	collection.set_tweets(p=1)
	for tweet in collection.tweets:
		print tweet.user 

	"""
	
	def __init__(self,frogged_file):
		self.frogged_file = frogged_file
		self.tweets = []

	def set_tweets(self,sw=0,p=0,ht=0,u=0):
		"extract sequences per tweet out of the file"
		"""
		will make different types of sequences, words, lemma's and postags
		result is a list of tweet objects
		the different types can be extracted independent from each other from a tweet object
		different sorts of tokens can be left out of the sequences:
			- sw-stopwords (based on a list from snowball, can be extended in this def)
			- p-punctuation
			- ht-hashtags
			- u-urls
		by default nothing is removed
		specify '1' for each category to choose for removal
		"""
		tweet_tokens = codecs.open(self.frogged_file,"r","utf-8").readlines()
		
		hashtag = re.compile(r"#")
		punct = re.compile(r"LET")
		url = re.compile(r"http:")
		conv = re.compile(r"^@")
		stopwords = [] #nltk.corpus.stopwords.words('dutch')
		stopwords.extend(["we","heel","wel","waar","wij"])

		first = tweet_tokens[0]
		first = re.sub("\n","",first)
		tags_first = first.split("\t")
		current_tweet_number = tags_first[0]
		current_tweet = Tweetsfeatures.Tweet(tags_first)
		current_tweet.add_sequence(tags_first)

		for token in tweet_tokens[1:]:
			token = re.sub("\n","",token)
			tags = token.split("\t")
			tweet_number = tags[0]
			if not int(tweet_number) == int(current_tweet_number):
				self.tweets.append(current_tweet)
				current_tweet_number = tweet_number
				current_tweet = Tweetsfeatures.Tweet(tags)
			word = tags[2]
			lemma = tags[3]
			pos = tags[5]
			if (sw and lemma in stopwords) or (p and punct.search(pos)) or (ht and hashtag.search(lemma)) or (u and url.search(word)):
				continue
			else:
				current_tweet.add_sequence(tags)

	def set_tweets_oneline(self,ht=0,u=0):
		"extract sequences per tweet out of the file"
		"""
		will make different types of sequences, words, lemma's and postags
		result is a list of tweet objects
		the different types can be extracted independent from each other from a tweet object
		different sorts of tokens can be left out of the sequences:
			- sw-stopwords (based on a list from snowball, can be extended in this def)
			- p-punctuation
			- ht-hashtags
			- u-urls
		by default nothing is removed
		specify '1' for each category to choose for removal
		"""
		tweets = codecs.open(self.frogged_file,"r","utf-8").readlines()
		
		hashtag = re.compile(r"#")
		url = re.compile(r"http:")
		conv = re.compile(r"^@")
		
		for line in tweets:
			tokens = line.split("\t")
			tweet = Tweetsfeatures.Tweet(tokens,"one_column")
			words = tokens[5].split(" ") 
			for word in words:
				if (ht and hashtag.search(word)) or (u and url.search(word)):
					continue
				else:
					tweet.wordsequence.append(word.lower().strip())		
			self.tweets.append(tweet)

	def tweets_2_lcsinput(self, path, bucketsize, classfile, metafile):
		bucket_i = 0
		dirnum = 1
		outclass = codecs.open(classfile,"a","utf-8")
		outmeta = codecs.open(metafile,"a","utf-8")
		for t in self.tweets:
			if bucket_i > int(bucketsize):
				dirnum += 1
				bucket_i = 0
			outfilename = path + str(dirnum) + ".txt"
			outfile = codecs.open(outfilename,"w","utf-8")
			words = t.wordsequence
			text = " ".join(words)
			label = t.label
			user = t.user
			time = t.time
			event = t.event
			outfile.write(text)
			outclass.write(outfilename + " " + label + "\n")
			outmeta.write(outfilename + " " + event + " " + time + " " + user + "\n")
			bucket_i += 1


	def add_ngrams(self,word=1,lemma=0,pos=0):
		"add ngrams to the features of each tweetobject"
		"""
		can only be used after 'set_sequences'
		a choice can be made for the three units word, lemma and pos
		furthermore, the size of N can be chosen for each feature
		example usage:
			tweetsobject = Tweetsfeatures.tweetsfeatures(infile)
			tweetsobject.set_sequences(p = 1)
			tweetsobject.add_ngrams(word = 2,lemma = 3)
		there will always be one n of ngrams be extracted from a unit 
		for accumulations of N for the same units (eg. unigrams and bigrams), 
			call this def several times
		"""

		def make_ngrams(sequence,n):
			ngram_features = []		
			if n == 1:
				for token in sequence:
					ngram_features.append(token)
			else:
				temp_lines = []
				temp_lines.extend(sequence)
				temp_lines.append("<s>")
				temp_lines.insert(0,"<s>")
				if n == 2:
					for i,token in enumerate(temp_lines[:len(temp_lines)-1]):
						bigram = token + "_" + temp_lines[i+1]
						ngram_features.append(bigram)
				elif n == 3:
					for i,token in enumerate(temp_lines[:len(temp_lines)-2]):
						trigram = token + "_" + temp_lines[i+1] + "_" + temp_lines[i+2]
						ngram_features.append(trigram)

			return ngram_features


		for t in self.tweets:
			features = t.get_features()
			if word:
				features.extend(make_ngrams(t.get_wordsequence(),word))
			if lemma:
				features.extend(make_ngrams(t.get_lemmasequence(),lemma))
			if pos:
				features.extend(make_ngrams(t.get_possequence(),pos))
			t.set_features(features)

	def prune_ngrams(self,p=10):
		"""prune features out based on a minimum frequency, thereby 
		restricting the dimensionspace"""
		featurefrequencies = defaultdict(int)
		for t in self.tweets:
			features = t.get_features()
			for feature in features: 
				featurefrequencies[feature] += 1

		for t in self.tweets:
			features = t.get_features()
			pruned_features = []
			for feature in features:
				if featurefrequencies[feature] >= p:
					pruned_features.append(feature)
			t.set_features(pruned_features)

	def evaluate_baseline(self):
		tp = 0
		fp = 0
		fn = 0
		tn = 0
		print(len(self.tweets))
		for t in self.tweets:
			label = t.label
			baseline_class = t.baseline_class
			if label == "before": 
				if label == baseline_class:
					tp += 1
				else:
					fn += 1
			else:
				if baseline_class == "before":
					fp += 1
				else:
					tn += 1

		precision = tp / (tp+fp)
		recall = tp / (tp+fn)
		f1 = 2 * ((precision * recall) / (precision + recall))
		accuracy = (tp+tn)/(fp+fn+tp+tn)
		return (precision,recall,f1,accuracy)

	def filter_domain(self,domain_eventlist):
		eventlist = []
		templist = []
		for entry in open(domain_eventlist):
			columns = entry.split(" ")
			event = columns[0]
			eventlist.append(event)

		for t in self.tweets:
			for word in t.wordsequence:
				word = re.sub("#","",word)
				if word in eventlist:
					templist.append(t)
					break

		self.tweets = templist

	def filter_label(self,label):
		templist = []

		for t in self.tweets:
			if t.label == label:
				templist.append(t)

		print(len(self.tweets))
		self.tweets = templist
		print(len(self.tweets))

	def remove_during(self):
		templist = []
		for t in self.tweets:
			if not t.label == "during":
				templist.append(t)

		self.tweets = templist

	def sequence2standard(self,outfile):
		out = codecs.open(outfile,"w","utf-8")
		for t in self.tweets:
			words = t.wordsequence
			words.append("<s>")
			words.insert(0,"<s>")
			line = " ".join(words) + "\n"
			out.write(line)

	def sequence2pplfiles(self,outdirectory):
		tweetnr = 1
		for t in self.tweets:
			words = t.wordsequence
			words.append("<s>")
			words.insert(0,"<s>")
			line = " ".join(words) + "\n"
			outfilename = outdirectory + "tweet_" + str(tweetnr) + ".txt"
			outfile = codecs.open(outfilename,"w","utf-8")
			tweetnr += 1

	def features2sparse(self,outfile):
		"TODO"

	def url_percent(self):

		tweet_tokens = codecs.open(self.frogged_file,"r","utf-8").readlines()
		
		url = re.compile(r"http:")
		conv = re.compile(r"^@")

		tweetcount = 0
		urlcount = 0
		convcount = 0
		first = tweet_tokens[0]
		first = re.sub("\n","",first)
		tags_first = first.split("\t")
		label = tags_first[1]
		current_tweet_number = tags_first[0]

		new_count_conv = True
		new_count_url = True

		for token in tweet_tokens[1:]:
			token = re.sub("\n","",token)
			tags = token.split("\t")
			tweet_number = tags[0]
			if not int(tweet_number) == int(current_tweet_number):
				if label == "before":
					tweetcount += 1
				current_tweet_number = tweet_number
				new_count_conv = True
				new_count_url = True
				label = tags[1]
			word = tags[2]
			lemma = tags[3]
			pos = tags[5]
			if url.search(word) and new_count_url and label == "before":
				urlcount += 1
				new_count_url = False
			elif conv.search(lemma) and new_count_conv and label == "before":
				convcount += 1
				new_count_conv = False

		percent_url = (urlcount / tweetcount) * 100
		percent_conv = (convcount / tweetcount) * 100
		print("num tweets = " + str(tweetcount) + ", num url = " + str(urlcount) + " (" + str(percent_url) + "%), num conv = " + str(convcount) + " (" + str(percent_conv) + "%)")

	def get_top_ngrams(self,label):
		topfreq = defaultdict(int)
		feats = []
		for t in self.tweets:
			if t.label == label:
				feats.extend(t.get_features())
		for feat in feats:
			topfreq[feat] += 1

		sorted_topfreq = []
		for w in sorted(topfreq, key=topfreq.get, reverse=True):
  			sorted_topfreq.append((w, topfreq[w]))

		print(sorted_topfreq)

	def write_standard_output(self,outfile):
  		out = codecs.open(outfile,"w","utf-8")
  		for t in self.tweets:
  			outstring = t.label
  			for f in t.features:
  				outstring = outstring + " " + f
  			outstring = outstring + "\n"
  			out.write(outstring)

	def get_wordsequences(self):
		wordsequences = [] 
		for t in self.tweets:
			wordsequences.append(t.get_wordsequence())
		return wordsequences

	def get_lemmasequences(self):
		lemmasequences = [] 
		for t in self.tweets:
			lemmasequences.append(t.get_lemmasequence())
		return lemmasequences		

	def get_possequences(self):
		possequences = [] 
		for t in self.tweets:
			possequences.append(t.get_possequence())
		return possequences

	def get_features(self): 
		tweet_features = []
		for t in self.tweets:
			tweet_features.append(t.get_features())
		return tweet_features

	def get_words_set(self):
		"Return a set of words from a frogged file"
		s=set()
		for t in self.tweets:
			for w in t.get_wordsequence():
				# if w[0] != '@': #-- does not exclude usernames.
				s.add(w)
		return s



	class Tweet:
		"container of sequences and features of a tweet"
		def __init__(self,token):
			self.label = token[1]
			self.event = token[6]
			self.user = token[7]
			time = token[8]
			timestructure = re.compile(r"(\d{4})-(\w{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})")
			structured_date_and_time = timestructure.search(time)
			try:
				year = int(structured_date_and_time.groups(0)[0])
				month = int(structured_date_and_time.groups(0)[1])
				day = int(structured_date_and_time.groups(0)[2])
				hour = int(structured_date_and_time.groups(0)[3])
				minute = int(structured_date_and_time.groups(0)[4])
				second = int(structured_date_and_time.groups(0)[5])
				self.time = datetime.datetime(year,month,day,hour,minute,second)
			except AttributeError:
				self.time = None
				print("Time feature error, in tweet number:" + str(time) + token[0])
			self.wordsequence = []
			self.lemmasequence = []
			self.possequence = [] 
			self.features = []

		def __init__(self,token,form):
			if form == "one_column":
				self.event = token[0]
				self.user = token[2]
				
				date = token[3]
				parse_date = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
				structured_date = parse_date.search(date)

				time = token[4]
				parse_time = re.compile(r"(\d{2}):(\d{2})")
				structured_time = parse_time.search(time)
				try:
					year = int(structured_date.groups(0)[0])
					month = int(structured_date.groups(0)[1])
					day = int(structured_date.groups(0)[2])
					hour = int(structured_time.groups(0)[0])
					minute = int(structured_time.groups(0)[1])
					self.time = datetime.datetime(year,month,day,hour,minute,0)
				except AttributeError:
					self.time = None
					print("Time feature error, in tweet number:" + str(time) + token[0])
				
				self.wordsequence = []
				self.lemmasequence = []
				self.possequence = [] 
				self.features = []
		
		def add_sequence(self,token):
			self.add_word(token)
			self.add_lemma(token)
			self.add_pos(token)

		def add_word(self,token):
			word = token[2]
			self.wordsequence.append(word.lower())

		def delete_word(self, token):
			pass

		def add_lemma(self,token):
			lemma = token[3]
			self.lemmasequence.append(lemma.lower())

		def add_pos(self,token):
			pos = token[5]
			self.possequence.append(pos)

		def set_features(self,features):
			self.features = features

		def set_classification(self,baseline_class):
			self.baseline_class = baseline_class

		def get_label(self): return self.label

		def get_wordsequence(self): return self.wordsequence

		def get_lemmasequence(self): return self.lemmasequence

		def get_possequence(self): return self.possequence

		def get_features(self): return self.features 

