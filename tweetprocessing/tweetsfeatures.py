#! /usr/bin/env python

from __future__ import division
import os
import codecs
import re
import datetime
from collections import defaultdict
import multiprocessing
import time_functions
import gen_functions
import operator

class Tweetsfeatures():
    """
    Container of tweetfeatures.
    It is instantiated with a .txt file, that contains tweets or tweettokens as a result of Frog processing. 
    The file could have two formats: 
    1:  [tweetnumber]\t[label]\t[word]\t[lemma]\t[morph.units]\t
        [pos]\t[keyword (based on which the tweet was searched)]\t
        [username]\t[time_posted]\n
    2:  One tweet per line
        features seperated by whitespace
    From an instance different features and labels can be generated.  
    Instances can be outputted in different formats, like sparse.
    
    Example usage (for file 'tweets.txt' and 'out.txt'):
        collection=tweetsfeatures.Tweetsfeatures(tweets.txt)
        collection.set_tweets(p=1)
        collection.add_ngrams(n=3)
        collection.features2sparsebinary(out.txt)
    """
    
    def __init__(self,frogged_file):
        self.frogged_file=frogged_file
        self.tweets=[]
        self.eventhash=False

    def set_events(self,eventfile,aggregation=False):
        self.eventhash=time_functions.generate_event_time_hash(eventfile)
        self.event_tweets=self.generate_tfz(aggregation)

    def set_tweets(self,p=0,ht=0,u=0):
        """
        Instantiate tweetobjects with meta-information and sequences of words, lemma's and pos-tags.
        Presumes a file with format 1.
        Different sorts of tokens can be left out of the sequences:
            - p-punctuation
            - ht-hashtags
            - u-urls
        By default nothing is removed, specify '1' for each category to choose for removal.
        """
        tweet_tokens=codecs.open(self.frogged_file,"r","utf-8").readlines()
        
        hashtag=re.compile(r"#")
        punct=re.compile(r"LET")
        url=re.compile(r"http:")
        
        first=tweet_tokens[0]
        first=re.sub("\n","",first)
        tags_first=first.split("\t")
        current_tweet_number=tags_first[0]
        current_tweet=Tweetsfeatures.Tweet(tags_first)
        current_tweet.add_sequence(tags_first)

        for token in tweet_tokens[1:]:
            token=re.sub("\n","",token)
            tags=token.split("\t")
            tweet_number=tags[0]
            if not int(tweet_number)==int(current_tweet_number):
                self.tweets.append(current_tweet)
                current_tweet_number=tweet_number
                current_tweet=Tweetsfeatures.Tweet(tags)
            word=tags[2]
            lemma=tags[3]
            pos=tags[5]
            if (p and punct.search(pos)) or (ht and hashtag.search(lemma)) or (u and url.search(word)):
                continue
            else:
                current_tweet.add_sequence(tags)

    def set_tweets_one_line(self,ht=False,u=False,lower=False,info_type = "meta"):
        """
        Instantiate tweetobjects with meta-information and a sequence of words.
        Presumes a file with format 2.
        Different sorts of tokens can be left out of the sequences:
            - p-punctuation
            - ht-hashtags
            - u-urls
        By default nothing is removed, specify '1' for each category to choose for removal
        """
        tweets=codecs.open(self.frogged_file,"r","utf-8").readlines()
        
        hashtag=re.compile(r"#")
        url=re.compile(r"http:")
        conv=re.compile(r"^@")
        
        for line in tweets:
            tokens=line.split("\t")
            if info_type == "meta":
                if len(tokens) >= 5:
                    tweet=Tweetsfeatures.Tweet(tokens,"one_line")
                    words=tokens[5].split(" ") 
                else: 
                    continue
            elif info_type == "text":
                tweet=Tweetsfeatures.Tweet(tokens,"text")
                words=tokens[1].split(" ")
            for word in words:
                if (ht and hashtag.search(word)) or (u and url.search(word)):
                    continue
                else:
                    if lower:
                        word=word.lower()
                    tweet.wordsequence.append(word.strip())        
            self.tweets.append(tweet)


    def filter_label(self,label):
        """Remove tweets with a certain label."""
        templist=[]
        for t in self.tweets:
            if t.label==label:
                templist.append(t)
               
        self.tweets=templist
    
    def normalize(self,cat):
        """Normalize diverse word types like url's and usernames to one standard form"""
        if cat=="url":
            find=re.compile("http://")
            replace="URL"
        elif cat=="user":
            find=re.compile("@")
            replace="USER"
        
        for t in self.tweets:
            for i,w in enumerate(t.wordsequence):
                if find.search(w):
                    t.wordsequence[i]=replace

    #Make N-grams of tweets that were set
    def add_ngrams(self,word=1,lemma=0,pos=0,n=3):
        """
        Extend features with N-grams.
        Can only be used after 'set_tweets' or 'set_tweets_oneline'
        A choice can be made for the three units word, lemma and pos
        The size of N can be chosen for each feature (only does one N a time)
        For several N-gram types per unit (eg. unigrams and bigrams) call this function several times.
        
        Example usage:
            collection=Tweetsfeatures.tweetsfeatures(infile)
            collection.set_tweet(p=1)
            collection.add_ngrams(word=2,lemma=3)
        """
        def make_ngrams(sequence,n):
            """sub-function to generate N-grams based on a specific sequence (words,lemma's,pos's) and a given N."""
            ngram_features=[]
            if n==1:
                for token in sequence:
                    ngram_features.append(token)
            else:
                temp_lines=[]
                temp_lines.extend(sequence)
                temp_lines.append("<s>")
                temp_lines.insert(0,"<s>")
                if n==2:
                    for i,token in enumerate(temp_lines[:len(temp_lines)-1]):
                        bigram="_".join([token,temp_lines[i+1]])
                        ngram_features.append(bigram)
                elif n==3:
                    for i,token in enumerate(temp_lines[:len(temp_lines)-2]):
                        trigram="_".join([token, temp_lines[i+1], temp_lines[i+2]])
                        ngram_features.append(trigram)

            return ngram_features

        for t in self.tweets:
            features=t.get_features()
            if word:
                features.extend(make_ngrams(t.get_wordsequence(),n))
            if lemma:
                features.extend(make_ngrams(t.get_lemmasequence(),n))
            if pos:
                features.extend(make_ngrams(t.get_possequence(),n))
            t.set_features(features)
  
    def add_char_ngrams(self,raw_file,n,id_col = 1,ignore = False,):
        """
        add character ngrams to the featurespace of each tweet, based on a raw untokenized file 
        (in order to take into account spaces and punctuation)
        """
        
        def make_char_ngrams(text,n):
            ngrams=[]
            for string in text:
                index=n
                while index < len(string):
                    ngrams.append(string[index-n:index])
                    index += 1
            return ngrams

        def rm_string(inputstring,rmstrings):
            new_strings = []
            inputstrings = [inputstring]
            for rmstring in rmstrings:
                keep_inputstring = []
                for inputstring in inputstrings:
                    new_inputstrings = [inputstring]
                    while re.search(rmstring,new_inputstrings[-1]):
                        new_inputstrings_rear = [new_inputstrings[-1][:new_inputstrings[-1].index(rmstring)]] + [new_inputstrings[-1][new_inputstrings[-1].index(rmstring)+len(rmstring):]]
                        if len(new_inputstrings) > 1:
                            new_inputstrings = new_inputstrings[:-1] + new_inputstrings_rear
                        else:
                            new_inputstrings = new_inputstrings_rear
                    keep_inputstring.extend(new_inputstrings)
                inputstrings = keep_inputstring
            return inputstrings

        #make a dictionary for tweet_ids
        tid_tweet = {}
        for t in self.tweets:
            tid_tweet[t.id] = t
            
        #make list of raw tweets        
        infile=codecs.open(raw_file,"r","utf-8")
        for line in infile.readlines():
            tokens=line.split("\t")
            tweet_id=tokens[id_col]
            try:
                tweet = tid_tweet[tweet_id]
                text = tokens[-1]
                if ignore:
                    text = rm_string(text,ignore)
                else:
                    text = [text]
                for n_val in n:
                    tweet.features.extend(make_char_ngrams(text,int(n_val)))
            except KeyError:
                continue
        infile.close()
  
    def filter_tweets(self,blacklist):
        """Filter tweets from this container if they contain a marker in a given list, like an event reference or RT"""
        print "removing tweets containing",blacklist
        print "freq tweets before", len(self.tweets)
        templist=[]
        for t in self.tweets:
            black=False
            for w in t.wordsequence:
                for b in blacklist:
                    if re.search(b,w,re.IGNORECASE):
                        black=True
            if not black:
                templist.append(t)

        self.tweets=templist
        print "freq tweets after", len(self.tweets)

    def filter_tweets_timewindow(self,windowsize,timeunit):
        """Filter tweets that do not fall within the specified timewindow before and after the event they refer to 
            (given in eventtime, as list with lines formatted as [eventname]\t[eventdate]\t[eventtime]\t[eventdate_end]etc."""
        print "num_tweets before: ",len(self.tweets)
        filtered_tweets=[]
        for t in self.tweets:
            #Get the time of the event mentioned in the tweet 
            tweet_datetime=time_functions.return_datetime(t.date,t.time,"vs")
            event_datetime_begin=self.eventhash[t.event][0]
            event_datetime_end=self.eventhash[t.event][1]
            #Extract the time difference between the tweet and the event 
            if tweet_datetime < event_datetime_begin:
                tweet_event_time=time_functions.timerel(event_datetime_begin,tweet_datetime,timeunit) 
                if tweet_event_time < windowsize:
                    filtered_tweets.append(t)
            else:
                if tweet_datetime < event_datetime_end:
                    filtered_tweets.append(t)
                else:
                    tweet_event_time=time_functions.timerel(tweet_datetime,event_datetime_end,timeunit)
                    if tweet_event_time < windowsize:
                        filtered_tweets.append(t)
                        
        self.tweets=filtered_tweets
        print "num_tweets ",len(self.tweets)
        
    def filter_tweets_timepoint(self,timepoint,split):
        """Filter tweets that are posted before or after a chosen timepoint"""
        print "splitting tweets to " + split + " " + timepoint + ",tweets before:",len(self.tweets)
        filtered_tweets=[]
        point_datetime=time_functions.return_datetime(timepoint)
        for t in self.tweets:
            #Get the time of the event mentioned in the tweet 
            tweet_datetime=time_functions.return_datetime(t.date,t.time,"vs")
            #Extract the time difference between the tweet and the event 
            if tweet_datetime<point_datetime:
                if split=="before":
                    filtered_tweets.append(t)
            else:    
                if split=="after":
                    filtered_tweets.append(t)
                        
        self.tweets=filtered_tweets
        print "tweets after",len(self.tweets)

    def remove_eventmention(self):
        """Remove a feature if it contains the mentioning of one of the given events."""
        blacklist=[]
        print "removing eventmentions..."
        for event in self.eventhash.keys():
            words=event.split(" ")
            for word in words:
                blacklist.append(word)
        removed_features=[]
        for t in self.tweets:
            removed_features=[]
            for i,feature in enumerate(t.features):
                parts=feature.split("_")
                for term in blacklist:
                    match=False
                    for p in parts:
                        if re.search(term,p,re.IGNORECASE):
                            match=True
                    if match:
                        removed_features.append(i)
                        break
            for offset,index in enumerate(removed_features):
                index -= offset
                del(t.features[index])

    def remove_blacklist(self,blacklist):
        """Remove a feature if it contains a word in the blacklist."""
        for t in self.tweets:
            removed_features=[]
            for i,feature in enumerate(t.features):
                parts=feature.split("_")
                for term in blacklist:
                    match=False
                    for p in parts:
                        if re.search(term,p,re.IGNORECASE):
                            match=True
                    if match:
                        removed_features.append(i)
                        break
            for offset,index in enumerate(removed_features):
                index -= offset
                del(t.features[index])

    def generate_tfz(self,agg=False):
        """
        Add time-from zero in hours information to tweets based on their time of posting
        """
        event_tweets=defaultdict(list)
        event_tweets_tfz=defaultdict(list)
        for t in self.tweets:
            event_tweets[t.event].append(t)
        
        for event in event_tweets.keys():
            tweets=event_tweets[event]
            tweets_tfz=[]
            tweets.sort(key=operator.methodcaller("get_datetime"), reverse=False)
            zeropoint=tweets[0].get_datetime()
            for t in tweets:
                tfz=int(time_functions.timerel(t.get_datetime(),zeropoint,"hour"))
                t.tfz=str(tfz)
                tweets_tfz.append(([t],tfz))        
            if agg:
                window=int(agg[0])
                slider=int(agg[1])
                event_tweets_tfz[event]=time_functions.extract_sliding_window_instances(tweets_tfz,window,slider)                    
            else: 
                event_tweets_tfz[event]=tweets_tfz
            
        return event_tweets_tfz

    def generate_time_label(self,timeunit,labeltype,threshold=False):
        """
        Add a label to tweets based on their tte
        The unit of time given as a label can be 'minute', 'hour' or 'day'.
        It can be chosen whether tweets posted during and after an event are taken into account. 
        During will always be given with the label 'during'. After can be given as 'after' or with the actual amount of time after the end time of the event.
        Options for labeltype are 'before' (for before only), 'category' (for the label 'after') and 'time' (for temporal labels for after-tweets).     
        Specify a threshold of tte 
        """
        threshold=threshold * -1
        for t in self.tweets:
            #Get the time of the event mentioned in the tweet 
            tweet_datetime=time_functions.return_datetime(t.date,t.time,"vs")
            event_datetime_begin=self.eventhash[t.event][0]
            event_datetime_end=self.eventhash[t.event][1]
            #Extract the time difference between the tweet and the event 
            if tweet_datetime < event_datetime_begin:
                tweet_event_time=time_functions.timerel(event_datetime_begin,tweet_datetime,timeunit) * -1
                if labeltype=="category":
                    t.label="before"
                    if threshold and tweet_event_time < threshold:
                        t.tte="early"
                    else:
                        t.tte=str(tweet_event_time)
                else:
                    if threshold and tweet_event_time < threshold:
                        t.label="early"
                        t.tte="early"
                    else:
                        t.label=str(tweet_event_time)
                        t.tte=str(tweet_event_time)
            else:
                if labeltype != "before":
                    if tweet_datetime < event_datetime_end:
                        t.set_label("during")
                    else:
                        if labeltype=="category":
                            t.set_label("after")
                        else:
                            tweet_event_time=time_functions.timerel(event_datetime_begin,tweet_datetime,"minute")
                            t.set_label=tweet_event_time

    def set_meta(self):
        """for each tweet, combine their metadata into one list"""
        for t in self.tweets:
            t.set_meta()

    def features2standard(self, path, prefix, dirsize, classfile, metafile, aggregate=False, parralel=False):
        """Write the features of a tweet to separate files to be processed by the LCS balanced Winnow classifier."""
        outparts=codecs.open(classfile,"a","utf-8")
        outmeta=codecs.open(metafile,"a","utf-8")
                    
        def filewriter(tweets,lab,tfz=False, qp=False,qm=False):
            i=0
            dir_index=0
            while i < len(tweets):
                print "instance",i,"of",len(tweets)
                if re.search(" ",lab):
                    lab=re.sub(" ","_",lab)
                if re.search("#",lab):
                    lab=re.sub("#","",lab)
                dir_string=str(lab) + "_" + prefix + "_" + str(i)
                os.system("mkdir " + path + dir_string)
                file_index=0
                if i+dirsize < len(tweets):
                    ctweets=tweets[i:i+dirsize]
                else: 
                    ctweets=tweets[i:]
                for t in ctweets:
                    #make filename and write contents to it
                    zeros=5-len(str(file_index))
                    j=0
                    file_name=str(file_index) + ".txt"
                    while j < zeros:
                        file_name="0" + file_name
                        j += 1
                    file_name=dir_string + "/" + file_name
                    outfile=codecs.open(path + file_name,"w","utf-8")

                    if aggregate:
                        features=[]
                        words=[]
                        for tt in t[0]:
                            features.extend(tt.features)
                            words.extend(tt.wordsequence)
                        features=list(set(features))
                        tweetlabel=t[0][-1].label
                        meta=t[0][-1].meta
                    else:
                        if tfz:
                            t=t[0][0]
                        features=t.features
                        words=t.wordsequence
                        tweetlabel=t.label
                        meta=t.meta

                    contents="\n".join(features)
                    outfile.write(contents)
                    #write file name and label to the partsfile
                    instanceline=file_name + " " + tweetlabel + "\n"
                    if qp:
                        qp.put(instanceline)
                    else:
                        outparts.write(instanceline)
                    
                    #write meta to metafile
                    metaline=file_name + "\t" + "\t".join(meta) + "\t" + " ".join(words) + "\n"
                    if qm:
                        qm.put(metaline)
                    else:
                        outmeta.write(metaline)
                    file_index += 1
                i += dirsize
            print lab,"done"
       
        if parralel:
            q=multiprocessing.Queue()
            r=multiprocessing.Queue()
            qwrites=[]
            rwrites=[]
            num_instances=0
            try:
                for event in self.event_tweets.keys():
                    num_instances += len(self.event_tweets[event])
                    p=multiprocessing.Process(target=filewriter,args=[self.event_tweets[event],event,True,q,r])
                    p.start()

            except AttributeError:
                num_instances=len(self.tweets)
                tweet_chunks=gen_functions.make_chunks(self.tweets)
                for i in range(16):
                    p=multiprocessing.Process(target=filewriter,args=[tweet_chunks[i],str(i),False,q,r])
                    p.start()

            while len(qwrites) < num_instances:
                l=q.get()
                qwrites.append(l)
                outparts.write(l)
            while len(rwrites) < num_instances:
                l=r.get()
                rwrites.append(l)
                outmeta.write(l)
            
        else:
            try:
                for event in self.event_tweets.keys():
                    filewriter(self.event_tweets[event],event,True)
                   
            except AttributeError:
                chunk_size=int(len(instances) / 16)
                tweet_chunks=gen_functions.make_chunks(self.tweets,chunk_size)
                for i in range(16):
                    filewriter(tweets_chunks[i],str(i))
            
        outparts.close()
        outmeta.close()
                
    def generate_feature_indexes(self,vocabulary):
        """Generate a dictionary to be used for sparse and sparse binary output."""
        feature_frequency=defaultdict(int)
        vocabulary_out=codecs.open(vocabulary,"w","utf-8")
        self.feature_index={}
        for t in self.tweets:
            for feature in t.features:
                feature_frequency[feature] += 1
        
        for i,feature in enumerate(feature_frequency.keys()):
             self.feature_index[feature]=i
             vocabulary_out.write(str(i) + "\t" + feature + "\n")

    def features2sparsebinary(self,out_file,vocabulary_file,metafile=False,threshold=False, aggregate=False):
        """Write the features to a file in the sparse-binary format."""
        
        out=open(out_file,"w")
        if metafile:
            meta_out=codecs.open(metafile,"w","utf-8")

        def generate_dataline(eventtweets,event):
            for t in eventtweets:
                tweets=t[0]
                tfz=t[1]
                datastring=""
                indexes=[]
                features=[]
                for tweet in tweets:
                    features.extend(tweet.features)
                features=list(set(features))
                for feature in features:
                    indexes.append(self.feature_index[feature])
                indexes=sorted(indexes)
                metatweet=tweets[-1]
                for index in indexes:
                    datastring=datastring + str(index) + ","
                datastring=datastring + metatweet.label + "\n"
                out.write(datastring)
                if metafile:
                    metastring="\t".join(self.meta) + "\t" + " ".join(metatweet.wordsequence) + "\n"
                    meta_out.write(metastring)
            print event,"done"

        self.generate_feature_indexes(vocabulary_file)
        if threshold:
            for event in self.event_tweets.keys():
                generate_dataline(event_tweets[event],event)

        out.close() 
        if metafile:            
            meta_out.close()
    
    #turn the tweets into one big document
    def features_2_bigdoc(self,outfile):
        outwrite = codecs.open(outfile,"w","utf-8")
        document = []
        for tweet in self.tweets:
            document.extend(tweet.features)
        outwrite.write(" ".join(document))
        outwrite.close() 

    #Standard subfunctions
    def get_wordsequences(self):
        wordsequences=[]
        for t in self.tweets:
            wordsequences.append(t.get_wordsequence())
        return wordsequences

    def get_lemmasequences(self):
        lemmasequences=[]
        for t in self.tweets:
            lemmasequences.append(t.get_lemmasequence())
        return lemmasequences

    def get_possequences(self):
        possequences=[] 
        for t in self.tweets:
            possequences.append(t.get_possequence())
        return possequences

    def get_features(self): 
        tweet_features=[]
        for t in self.tweets:
            tweet_features.append(t.get_features())
        return tweet_features

    class Tweet:
        """Class containing the features and  istics of a tweet."""
        def __init__(self,token):
            self.label=token[1]
            self.event=token[6]
            self.user=token[7]
            self.time=token[8]
            self.wordsequence=[]
            self.lemmasequence=[]
            self.possequence=[]
            self.features=[]
        
        def __init__(self,token,form):
            if form=="one_line":
                self.label=token[0]
                self.event=token[0]
                self.id=str(token[1])
                self.user=token[2]
                self.date=str(token[3])
                self.time=str(token[4])
                self.tte="-"
                self.wordsequence=[]
                self.lemmasequence=[]
                self.possequence=[]
                self.features=[]
            elif form == "text":
                self.id=str(token[0])
                self.

        def add_sequence(self,token):
            self.add_word(token)
            self.add_lemma(token)
            self.add_pos(token)

        def add_word(self,token):
            word=token[2]
            self.wordsequence.append(word.lower())

        def add_lemma(self,token):
            lemma=token[3]
            self.lemmasequence.append(lemma.lower())

        def add_pos(self,token):
            pos=token[5]
            self.possequence.append(pos)

        def set_label(self,label):
            self.label=label

        def set_features(self,features):
            self.features=features

        def set_meta(self):
            try:
                self.meta=[self.id,self.event,self.label,self.tte,self.tfz,self.date,self.time,self.user]
            except AttributeError:
                self.meta=[self.id,self.event,self.label,self.date,self.time,self.user]
            
        def get_label(self): return self.label

        def get_datetime(self):
            return time_functions.return_datetime(self.date,self.time,"vs")

        def get_wordsequence(self): return self.wordsequence

        def get_lemmasequence(self): return self.lemmasequence

        def get_possequence(self): return self.possequence

        def get_features(self): return self.features 

