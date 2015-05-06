#! /usr/bin/env python

import os
import re
import datetime
from collections import defaultdict
import multiprocessing
#from pattern.nl import parse, pprint, sentiment
import frog
import time_functions
import gen_functions
import ucto

class Tweetsfeatures():
    """
    Container of tweetfeatures.
    It is instantiated with a .txt file, that contains tweets or tweettokens as a 
    result of Frog processing. 
    The file should be in the right format: 
    - One tweet per line
    - data separated by tabs
    - label\ttweetid\tuser\tdate\ttime\ttweettext\n
    Instances can be outputted in different formats, like sparse.
    
    Example usage:
        collection = tweetsfeatures.Tweetsfeatures(tweets.txt)
        collection.set_tweets(p = 1)
        collection.add_ngrams(n = 3)
        collection.features2sparsebinary(out.txt)
    """
    
    def __init__(self,infile,columns):
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
            fields = True
            tweet_fields = []
            for i,column in enumerate(columns):
                if column or column == 0:
                    try:
                        tweet_fields.append(tokens[column])
                    except IndexError:
                        print("field indexes do not correspond for",tokens)
                        fields=False
                        continue
                else:
                    tweet_fields.append("-")
            if fields:
                self.instances.append(Tweetsfeatures.Tweet(tweet_fields))

    def process_frog(self,punct):
        fo = frog.FrogOptions(threads=16)
        frogger = frog.Frog(fo,"/vol/customopt/uvt-ru/etc/frog/frog-twitter.cfg")
        num_instances = len(self.instances)
        for i,t in enumerate(self.instances):
            print("tokenizing",i,"of",num_instances,"instances")
            tokens = []
            stems = []
            poss = []
            data = frogger.process(t.text)
            for token in data:
                if (punct and not token["pos"] == "LET()") or \
                    not punct:
                    tokens.append(token["text"])
                    poss.append(token["pos"])
                    stems.append(token["lemma"])
            t.add_stem(stems)
            t.add_pos(poss)
            t.text = " ".join(tokens)

    def add_label(self,label):
        """add static label to tweets"""
        for t in self.instances:
            t.set_label(label)

    def filter_label(self,label):
        """Remove tweets with the given label."""
        templist = []
        for t in self.instances:
            if t.label == label:
                templist.append(t)           
        self.instances = templist

    def set_sequences(self, ht = False, lower = False, us = False, ur = False, cap = False):
        hashtag = re.compile(r"#")
        url = re.compile(r"http://")
        user = re.compile(r"@")
        for t in self.instances:
            if lower: 
                words = t.text.lower().split(" ")
            else:
                words = t.text.split(" ") 
            for word in words:
                if (ht and hashtag.search(word)):
                    continue
                elif ur and url.search(word):
                    t.wordsequence.append("URL")
                elif us and user.search(word):
                    t.wordsequence.append("USER")
                elif cap and re.search("[A-Z]",word) and re.search("[a-z]",word):
                    t.wordsequence.append(word.lower())
                else:
                    t.wordsequence.append(word)      

    def extract_listfeatures(self,l,n):
        """
        Extract features from a list and single them out
        """
        self.specials.append(n)
        li = sorted(l, key=len, reverse=True)
        li = [tx.replace('.','\.').replace('*','\*') for tx in li]
        patterns = re.compile('\\b'+'\\b|\\b'.join(li)+'\\b')
        neg_patterns = re.compile('\\b'+'\\b|\\b'.join(li)+'\\b')
        feats = []
        for t in self.instances:
            if t.stemseq:
                features = [x.replace(" ","_") for x in re.findall(patterns," ".join(t.stemseq))]
            else:
                features = [x.replace(" ","_") for x in re.findall(patterns,
                    " ".join(t.wordsequence))]
            feats.append(len([x for x in features if not x == ""]) / len(t.wordsequence))
        if not len(feats) == len(self.instances):
            print("listfeatures and tweets not aligned, feats:",len(feats),", instances:",
                len(self.instances),"exiting program")
        for i,rf in enumerate(feats):
            self.instances[i].features.append(str(round(rf/max(feats),2)))

    def return_ngrams(self,l,n):
        return [(l[i:i+n]) for i in range(len(l)-n+1)]

    #Make N-grams of tweets that were set
    def add_ngrams(self,n,t):
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
        if t == "word":
            for t in self.instances:
                for n_val in n:
                    if n_val > 1:
                        seq = ["<s>"] + t.wordsequence + ["<s>"]
                    else:
                        seq = t.wordsequence
                    t.features[0].extend(["_".join(x) for x in self.return_ngrams(seq,n_val)])
        elif t == "pos":
            for t in self.instances:
                for n_val in n:
                    if n_val > 1:
                        seq = ["<s>"] + t.posseq + ["<s>"]
                    else:
                        seq = t.posseq
                    t.features[0].extend(["_".join(x) for x in self.return_ngrams(seq,n_val)])
        elif t == "stem":
            for t in self.instances:
                for n_val in n:
                    if n_val > 1:
                        seq = ["<s>"] + t.stemseq + ["<s>"]
                    else:
                        seq = t.stemseq
                    t.features[0].extend(["_".join(x) for x in self.return_ngrams(seq,n_val)])

    def add_char_ngrams(self,n,ignore = False,lower = False):
        """
        add character ngrams to the featurespace of each tweet 
        """        
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
            if lower:
                test = text.lower()
            if ignore:
                text = rm_string([text],ignore)
            for n_val in n:
                t.features[0].extend(self.return_ngrams(text,n_val))

    def add_stats(self,hashtags,capitalization,tweetlength,pronouns,punctuation,emoticon):
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
        if emoticon:
            self.specials.append("positive emoticons")
            self.specials.append("neutral emoticons")
            self.specials.append("negative emoticons")
            posi = re.compile(r"(:(-|[oO]|[cC]|\^)?(\)|\]|>|}|D"
                "|[pP]|[dD])\)?|\(:|;-?\)|=-?(\]|\)|D|3)|8-?(\)|D)|B\^D|[Xx]-?D)")
            neutr = re.compile(r":(\$|\*|o|s|\|)")
            nega = re.compile(r"(>?:-?\'?(\(|\[|c|<|{|\|\||@)|D(:|;)?(<|8|=|X)|;\(|v\.v)?")
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
                    if 'VNW(pers,pron,nomin,red,2v,ev)' in tags or \
                        'VNW(pers,pron,nomin,vol,2v,ev)' in tags:
                        t.pronouns = '1.0'
                    else:
                        t.pronouns = '0.0'
            if hashtags:
                t.hashtags = len([x for x in t.wordsequence if x[0] == '#']) / len(t.wordsequence)
            if capitalization:
                t.uppercase = len([x for x in t.text if x.isupper()]) / len(t.text)
            if emoticon:
                if posi.search(t.text):
                    t.posi = '1.0'
                else:
                    t.posi = '0.0'
                if neutr.search(t.text):
                    t.neutr = '1.0'
                else:
                    t.neutr = '0.0'
                if nega.search(t.text):
                    t.nega = '1.0'
                else:
                    t.nega = '0.0'
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
            if emoticon:
                t.features.extend([t.posi,t.neutr,t.nega])

    # def add_sentiment(self):
    #     self.specials.extend(["polarity","subjectivity"])
    #     for t in self.instances:
    #         senti = sentiment(t.text)
    #         t.features.extend([str(senti[0]),str(senti[1])])

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
            tweet_datetime = time_functions.return_datetime(instance.date,
                time=instance.time,setting="vs")
            #Extract the time difference between the tweet and the event 
            if tweet_datetime > point_datetime_begin and tweet_datetime < point_datetime_end:
                filtered_tweets.append(instance)
                        
        self.instances = filtered_tweets

    def remove_blacklist(self,blacklist,eos):
        """Remove a feature if it contains a word in the blacklist."""
        for t in self.instances:
            removed_features = []
            for i,feature in enumerate(t.features[0]):
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
                    if re.search("_<s>",t.features[0][index]):
                        pre_last_feature = t.features[0][index-1]
                        parts = pre_last_feature.split("_")
                        if len(parts) == 2:
                            new_feature = parts[-1]
                        else: 
                            new_feature = "_".join(parts[-2:])
                        new_feature = new_feature + "_<s>"
                        t.features[0][index] = new_feature
                    else:
                        del(t.features[0][index])
                        offset +=  1
            else:
                for offset,index in enumerate(removed_features):
                    index -=  offset
                    del(t.features[0][index])

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
        directory = "/".join(outfile.split("/")[:directory_index]) + "/"
        while True:
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
            out.write("\t".join(i.meta) + "\t" + " ".join(i.features[0]) + "\t" + \
                " ".join(i.features[1:]) + "\n")
        out.close()
        if len(self.specials) > 0:
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

        def set_label(self,lab):
            self.label = lab

        def add_pos(self,seq):
            self.posseq = seq

        def add_stem(self,seq):
            self.stemseq = seq

        def set_meta(self):
            self.meta = [self.id,self.label,self.user,self.date,self.time,self.text]

        def get_datetime(self):
            return time_functions.return_datetime(self.date,self.time,"vs")
