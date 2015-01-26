#! /usr/bin/env python

import os
import re
import datetime
from collections import defaultdict
import time_functions
import gen_functions
import multiprocessing
import frog

class Tweetsfeatures():
    """
    Container of tweetfeatures.
    It is instantiated with a .txt file, that contains tweets or tweettokens as a 
    result of Frog processing. 
    The file should be in the right format: 
    - One tweet per line
    - data seperated by tabs
    - label\ttweetid\tuser\tdate\ttime\ttweettext\n
    Instances can be outputted in different formats, like sparse.
    
    Example usage:
        collection = tweetsfeatures.Tweetsfeatures(tweets.txt)
        collection.set_tweets(p = 1)
        collection.add_ngrams(n = 3)
        collection.features2sparsebinary(out.txt)
    """
    
    def __init__(self,infile):
        """
        Instantiate tweetobjects.
        Presumes a file in the right format.
        Different sorts of tokens can be left out of the sequences:
            - p-punctuation
            - ht-hashtags
            - u-urls
        By default nothing is removed, specify '1' for each category to choose for removal
        """
        self.instances = []
        self.specials = []

        lines = open(infile,encoding = "utf-8")
        tweets = lines.readlines()
        lines.close()
   
        for line in tweets:
            tokens = line.strip().split("\t")
            tweet = Tweetsfeatures.Tweet(tokens)
            self.instances.append(tweet)

    def filter_label(self,label):
        """Remove tweets with the given label."""
        templist = []
        for t in self.instances:
            if t.label == label:
                templist.append(t)           
        self.instances = templist

    def add_frog(self,stem,pos):
        fo = frog.FrogOptions(threads=16)
        frogger = frog.Frog(fo,"/vol/customopt/uvt-ru/etc/frog/frog-twitter.cfg")
        for t in self.instances:
            stems = []
            poss = []
            data = frogger.process(t.text)
            for token in data:
                poss.append(token["pos"])
                stems.append(token["lemma"])
            if stem:
                t.add_stem(stems)
            if pos:
                t.add_pos(poss)

    def set_sequences(self, ht = False, lower = False, us = False, ur = False):
        hashtag = re.compile(r"#")
        url = re.compile(r"http://")
        user = re.compile(r"@")
        for t in self.instances:
            if lower: 
                t.text = t.text.lower()
            else:
                words = t.text.split(" ") 
            for word in words:
                if (ht and hashtag.search(word)):
                    continue
                elif ur and url.search(word):
                    t.wordsequence.append("URL")
                elif us and user.search(word):
                    t.wordsequence.append("USER")
                else:
                    t.wordsequence.append(word)      

    def extract_listfeatures(self,l,n):
        """
        Extract features from a list and single them out
        """
        self.specials.append(n)
        li = sorted(l, key=len, reverse=True)
        li = [tx.replace('.','\.').replace('*','\*') for tx in li] # not to match anything with . (dot) or *
        patterns = re.compile('\\b'+'\\b|\\b'.join(li)+'\\b')
        neg_patterns = re.compile('\\b'+'\\b|\\b'.join(li)+'\\b')
        feats = []
        for t in self.instances:
            if t.stemseq:
                features = [x.replace(" ","_") for x in re.findall(patterns," ".join(t.stemseq))]
            else:
                features = [x.replace(" ","_") for x in re.findall(patterns," ".join(t.wordsequence))]
            feats.append(len([x for x in features if not x == ""]) / len(t.wordsequence))
        if not len(feats) == len(self.instances):
            print("listfeatures and tweets not aligned, feats:",len(feats),", instances:",len(self.instances),"exiting program")
        for i,rf in enumerate(feats):
            self.instances[i].features.append(str(round(rf/max(feats),2)))

    #Make N-grams of tweets that were set
    def add_ngrams(self,n,t="word"):
        """
        Extend features with N-grams.
        Can only be used after 'set_tweets' or 'set_tweets_oneline'
        A choice can be made for the three units word, lemma and pos
        The size of N can be chosen for each feature (only does one N a time)
        For several N-gram types per unit (eg. unigrams and bigrams) call this function several 
        times.
        
        Example usage:
            collection = Tweetsfeatures.tweetsfeatures(infile)
            collection.set_tweet(p = 1)
            collection.add_ngrams(word = 2,lemma = 3)
        """
        def make_ngrams(sequence,n):
            """sub-function to generate N-grams based on a specific sequence (words,lemma's,pos's) 
            and a given N."""
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
                        bigram = "_".join([token,temp_lines[i+1]])
                        ngram_features.append(bigram)
                elif n == 3:
                    for i,token in enumerate(temp_lines[:len(temp_lines)-2]):
                        trigram = "_".join([token, temp_lines[i+1], temp_lines[i+2]])
                        ngram_features.append(trigram)

            return ngram_features

        if t == "word":
            for t in self.instances:
                t.features[0].extend(make_ngrams(t.wordsequence,n))
        elif t == "pos":
            for t in self.instances:
                t.features[0].extend(make_ngrams(t.posseq,n))
  
    def add_char_ngrams(self,n,ignore = False):
        """
        add character ngrams to the featurespace of each tweet 
        """        
        def make_char_ngrams(text,n):
            ngrams = []
            for string in text:
                index = n
                while index < len(string):
                    char_ngram = string[index-n:index]
                    char_ngram = re.sub(" ","_",char_ngram)
                    if len(char_ngram) == n: 
                        ngrams.append(char_ngram)
                    index +=  1
            return ngrams

        def rm_string(inputstrings,rmstrings):
            for rmstring in rmstrings:
                new_inputstrings = []
                for inputstring in inputstrings:
                    if re.search(rmstring,inputstring):
                        new_inputstrings.extend(inputstring.split(rmstring))
                    else:
                        new_inputstrings.append(inputstring)
                inputstrings = new_inputstrings
            return inputstrings

        #make list of raw tweets        
        for t in self.instances:
            text = t.text
            if ignore:
                text = rm_string([text],ignore)
            for n_val in n:
                t.features[0].extend(make_char_ngrams(text,int(n_val)))

    def add_stats(self,hashtags,capitalization,tweetlength,pronouns,punctuation):
        #add features to list
        if hashtags:
            self.specials.append("hashtags")
        if capitalization:
            self.specials.append("capitalization")
        if tweetlength:
            self.specials.append("tweetlength")
        if pronouns:
            self.specials.append("pronouns")
        if punctuation:
            self.specials.append("punctuation")
        #retrieve info
        for t in self.instances:
            if tweetlength or pronouns or punctuation:
                tags = t.posseq
                if tweetlength:
                    tl = len([x for x in tags if not x == 'LET()'])
                    t.tl_absolute = tl
                if punctuation:
                    punct = len([x for x in tags if x == 'LET()']) / len(tags)
                    t.punct = punct
                if pronouns:
                    if 'VNW(pers,pron,nomin,red,2v,ev)' in tags or 'VNW(pers,pron,nomin,vol,2v,ev)':
                        t.pronouns = '1.0'
                    else:
                        t.pronouns = '0.0'
            if hashtags:
                t.hashtags = len([x for x in t.wordsequence if x[0] == '#']) / len(t.wordsequence)
            if capitalization:
                t.uppercase = len([x for x in t.text if x.isupper()]) / len(t.text)
        #add feature
        if hashtags:
            max_ht = max(t.hashtags for t in self.instances)
        if capitalization:
            max_uc = max(t.uppercase for t in self.instances)
        if tweetlength:
            max_tl = max(t.tl_absolute for t in self.instances)
        if punctuation:
            max_punct = max(t.punct for t in self.instances)
        for t in self.instances:
            if hashtags:            
                ht = t.hashtags
                t.features.append(str(round(ht / max_ht,2)))            
            if capitalization:
                uc = t.uppercase
                t.features.append(str(round(uc / max_uc,2)))
            if tweetlength:
                tl = t.tl_absolute
                t.features.append(str(round(tl / max_tl,2)))
            if pronouns:
                t.features.append(t.pronouns)
            if punctuation:
                punct = t.punct
                t.features.append(str(round(punct / max_punct,2)))

    def filter_tweets(self,blacklist):
        """Filter tweets from this container if they contain a marker in a given list, like an 
        event reference or RT"""
        print("removing tweets containing",blacklist)
        print("freq tweets before",len(self.instances))
        templist = []
        for t in self.instances:
            black = False
            for w in t.wordsequence:
                for b in blacklist:
                    if re.match(b,w,re.IGNORECASE):
                        black = True
            if not black:
                templist.append(t)

        self.instances = templist
        print("freq tweets after",len(self.instances))

    def filter_tweets_reflexive_hashtag(self,hashtag):
        """filter tweets from this container if they do not contain a given hashtag at the end 
        (may still proceed other hashtags or a url)"""
        print("filtering to tweets with",hashtag,"at the end")
        print("freq tweets before", len(self.instances))
        templist = []

        def has_endhashtag(sequence):
            if sequence[-1] == ".":
                return False
            for h in hashtag:
                try:
                    if re.match(sequence[-1],h,re.IGNORECASE):
                        return True
                except:
                    return False             
            if re.search("http://",sequence[-1]) or re.search("#",sequence[-1]):
                has_endhashtag(sequence[:-1])
            else:
                return False

        for t in self.instances:
            if has_endhashtag(t.wordsequence):
                templist.append(t)

        self.instances = templist
        print("freq tweets after",len(self.instances))
        
    def filter_tweets_timewindow(self,timepoint_1,timepoint_2):
        """Filter tweets that are posted before or after a chosen timepoint"""
        filtered_tweets = []
        point_datetime_begin = time_functions.return_datetime(timepoint_1)
        point_datetime_end = time_functions.return_datetime(timepoint_2)
        for instance in self.instances:
            #Get the time of the event mentioned in the tweet 
            tweet_datetime = time_functions.return_datetime(instance.date,time=instance.time,setting="vs")
            #Extract the time difference between the tweet and the event 
            if tweet_datetime > point_datetime_begin and tweet_datetime < point_datetime_end:
                filtered_tweets.append(instance)
                        
        self.instances = filtered_tweets

    def remove_blacklist(self,blacklist,eos):
        """Remove a feature if it contains a word in the blacklist."""
        for t in self.instances:
            removed_features = []
            for i,feature in enumerate(t.features):
                parts = feature.split("_")
                for term in blacklist:
                    match = False
                    for p in parts:
                        if re.search(term,p,re.IGNORECASE):
                            match = True
                    if match:
                        removed_features.append(i)
                        break
            if eos:
                offset = 0
                for index in removed_features:
                    index -=  offset
                    if re.search("_<s>",t.features[index]):
                        pre_last_feature = t.features[index-1]
                        parts = pre_last_feature.split("_")
                        if len(parts) == 2:
                            new_feature = parts[-1]
                        else: 
                            new_feature = "_".join(parts[-2:])
                        new_feature = new_feature + "_<s>"
                        t.features[index] = new_feature
                    else:
                        del(t.features[index])
                        offset +=  1

            else:
                for offset,index in enumerate(removed_features):
                    index -=  offset
                    del(t.features[index])

    def aggregate_instances(self,size):
        #sort instances in time
        self.instances.sort(key = lambda i: (i.get_datetime))
        windows = []
        features = []
        i = 0
        while i + size < len(self.instances):
            window = self.instances[i + size]
            if len(features) == 0:
                for instance in self.instances[i:i + size]:
                    features.extend(instance.features)
            else:
                features = features[len(self.instances[i - 1].features):]
                features.extend(self.instances[i + size].features)
            window.features = features
            windows.append(window)
            i += 1
        self.instances = windows

    def set_meta(self):
        """for each tweet, combine their metadata into one list"""
        for t in self.instances:
            try:
                t.set_meta()
            except:
                t.meta = ""

    def output_features(self, outfile):
        directory_index = -1
        directory = "/".join(outfile.split("/")[:directory_index])
        while True:
            print(directory_index,"/".join(outfile.split("/")[:directory_index]))
            if not os.path.exists("/".join(outfile.split("/")[:directory_index])):
                directory_index -= 1
            else:
                break
        while directory_index <= -1: 
            if not os.path.exists("/".join(outfile.split("/")[:directory_index])):
                os.system("mkdir " + "/".join(outfile.split("/")[:directory_index]))
            directory_index += 1
        out = open(outfile,"w",encoding = "utf-8")
        for i in self.instances:
            out.write("\t".join(i.meta) + "\t" + " ".join(i.features[0]) + " | " + " ".join(i.features[1:]) + "\n")
        out.close()
        print(len(self.specials))
        if len(self.specials) > 0:
            print("yes")
            specials_out = open(directory + "special_features.txt","w",encoding = "utf-8")
            for special in self.specials:
                specials_out.write(special + "\n")

    class Tweet:
        """Class containing the features and characteristics of a tweet."""
        def __init__(self,tokens):
            if len(tokens) == 1:
                self.text = unicode(tokens[0])
            else:
                self.label = tokens[0]
                self.id = str(tokens[1])
                self.user = tokens[2]
                self.date = str(tokens[3])
                self.time = str(tokens[4])
                self.text = tokens[5]
            self.wordsequence = []
            self.features = [[]]

        def add_pos(self,seq):
            self.posseq = seq

        def add_stem(self,seq):
            self.stemseq = seq

        def set_meta(self):
            self.meta = [self.id,self.label,self.user,self.date,self.time]

        def get_datetime(self):
            return time_functions.return_datetime(self.date,self.time,"vs")


