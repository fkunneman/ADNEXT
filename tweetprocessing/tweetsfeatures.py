#! /usr/bin/env python

import os
import codecs
import re
import datetime
from collections import defaultdict
import time_functions
import gen_functions

class Tweetsfeatures():
    """
    Container of tweetfeatures.
    It is instantiated with a .txt file, that contains tweets or tweettokens as a result of Frog processing. 
    The file should be in the right format: 
    - One tweet per line
    - data seperated by tabs
    - label\ttweetid\tuser\tdate\ttime\ttweettext\n
    Instances can be outputted in different formats, like sparse.
    
    Example usage:
        collection=tweetsfeatures.Tweetsfeatures(tweets.txt)
        collection.set_tweets(p=1)
        collection.add_ngrams(n=3)
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
        self.instances=[]
        
        lines = codecs.open(infile,"r","utf-8")
        tweets=lines.readlines()
        lines.close()
   
        for line in tweets:
            tokens=line.strip().split("\t")
            tweet=Tweetsfeatures.Tweet(tokens)
            self.instances.append(tweet)

    def filter_label(self,label):
        """Remove tweets with the given label."""
        templist=[]
        for t in self.instances:
            if t.label==label:
                templist.append(t)           
        self.instances=templist
    
    def set_wordsequences(self,ht=False,u=False,lower=False):
        hashtag=re.compile(r"#")
        url=re.compile(r"http:")
        for t in self.instances:
            if lower: 
                t.text = t.text.lower()
            words=t.text.split(" ") 
            for word in words:
                if (ht and hashtag.search(word)) or (u and url.search(word)):
                    continue
                else:
                    t.wordsequence.append(word)        

    def normalize(self,cat):
        """Normalize diverse word types like url's and usernames to one standard form"""
        if cat=="url":
            find=re.compile("http://")
            replace="URL"
        elif cat=="user":
            find=re.compile("@")
            replace="USER"
        
        for t in self.instances:
            for i,w in enumerate(t.wordsequence):
                if find.search(w):
                    t.wordsequence[i]=replace

    #Make N-grams of tweets that were set
    def add_ngrams(self,word=1,n=3):
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

        for t in self.instances:
            features=t.features
            features.extend(make_ngrams(t.wordsequence,n))
            t.set_features(features)
  
    def add_char_ngrams(self,n,ignore = False):
        """
        add character ngrams to the featurespace of each tweet 
        """        
        def make_char_ngrams(text,n):
            ngrams=[]
            for string in text:
                index=n
                while index < len(string):
                    char_ngram = string[index-n:index]
                    char_ngram = re.sub(" ","_",char_ngram)
                    if len(char_ngram) == n: 
                        ngrams.append(char_ngram)
                    index += 1
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
                t.features.extend(make_char_ngrams(text,int(n_val)))
  
    def filter_tweets(self,blacklist):
        """Filter tweets from this container if they contain a marker in a given list, like an event reference or RT"""
        print "removing tweets containing",blacklist
        print "freq tweets before", len(self.instances)
        templist=[]
        for t in self.instances:
            black=False
            for w in t.wordsequence:
                for b in blacklist:
                    if re.match(b,w,re.IGNORECASE):
                        black=True
            if not black:
                templist.append(t)

        self.instances=templist
        print "freq tweets after", len(self.instances)

    def filter_tweets_reflexive_hashtag(self,hashtag):
        """filter tweets from this container if they do not contain a given hashtag at the end (may still proceed other hashtags or a url"""
        print "filtering to tweets with",hashtag,"at the end"
        print "freq tweets before", len(self.instances)
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
        print "freq tweets after", len(self.instances)
        
    def filter_tweets_timepoint(self,timepoint,split):
        """Filter tweets that are posted before or after a chosen timepoint"""
        print "splitting tweets to " + split + " " + timepoint + ",tweets before:",len(self.instances)
        filtered_tweets=[]
        point_datetime=time_functions.return_datetime(timepoint)
        for t in self.instances:
            #Get the time of the event mentioned in the tweet 
            tweet_datetime=time_functions.return_datetime(t.date,t.time,"vs")
            #Extract the time difference between the tweet and the event 
            if tweet_datetime<point_datetime:
                if split=="before":
                    filtered_tweets.append(t)
            else:    
                if split=="after":
                    filtered_tweets.append(t)
                        
        self.instances=filtered_tweets
        print "tweets after",len(self.instances)

    def remove_blacklist(self,blacklist,eos):
        """Remove a feature if it contains a word in the blacklist."""
        for t in self.instances:
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
            if eos:
                offset = 0
                for index in removed_features:
                    index -= offset
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
                        offset += 1

            else:
                for offset,index in enumerate(removed_features):
                    index -= offset
                    del(t.features[index])

    def aggregate_instances(self,size):
        #sort instances in time
        self.instances.sort(key = lambda i: (i.get_datetime))
        windows = []
        features = []
        i = 0
        while i+size < len(self.instances):
            window = self.instances[i+size]
            if len(features) == 0:
                for instance in self.instances[i:i+size]:
                    features.extend(instance.features)
            else:
                features = features[len(self.instances[i-1].features):]
                features.extend(self.instances[i+size].features)
            window.features = features
            windows.append(window)
            i+=1
        self.instances = windows

    def set_meta(self):
        """for each tweet, combine their metadata into one list"""
        for t in self.instances:
            t.set_meta()

    def output_features(self, outfile):
        out = codecs.open(outfile,"w","utf-8")
        for i in self.instances:
            out.write("\t".join(i.meta) + "\t" + " ".join(i.features) + "\n")
        out.close()

    # def features2standard(self, directory, prefix, parralel=False):
    #     """Write the features of a tweet to separate files to be processed by the LCS balanced Winnow classifier."""
        
    #     path = directory + "files/"
    #     if not os.path.exists(path):
    #         os.system("mkdir " + path)
    #     outparts=codecs.open(directory + prefix + "parts.txt","w","utf-8")
    #     outmeta=codecs.open(directory + prefix + "meta.txt","w","utf-8")
                    
    #     def filewriter(instances,lab,qp=False,qm=False):
    #         dir_index=0
    #         for i in range(len(instances)):
    #             dir_string=str(lab) + "_" + prefix + "_" + str(i)
    #             os.system("mkdir " + path + dir_string)
    #             file_index,dirsize=0,25000
    #             if i+dirsize < len(instances):
    #                 ctweets=instances[i:i+d]
    #             else: 
    #                 ctweets=instances[i:]
    #             for t in ctweets:
    #                 #make filename and write contents to it
    #                 zeros=5-len(str(file_index))
    #                 j=0
    #                 file_name=str(file_index) + ".txt"
    #                 while j < zeros:
    #                     file_name="0" + file_name
    #                     j += 1
    #                 outfile=codecs.open(path + dir_string + "/" + file_name,"w","utf-8")
    #                 features,words,tweetlabel,meta=t.features,t.wordsequence,t.label,t.meta
    #                 outfile.write("\n".join(features))
    #                 outfile.close()
    #                 #write file name and label to the partsfile
    #                 instanceline=file_name + " " + tweetlabel + "\n"
    #                 if qp:
    #                     qp.put(instanceline)
    #                 else:
    #                     outparts.write(instanceline)
    #                 #write meta to metafile
    #                 metaline=file_name + "\t" + "\t".join(meta) + "\t" + " ".join(words) + "\n"
    #                 if qm:
    #                     qm.put(metaline)
    #                 else:
    #                     outmeta.write(metaline)
    #                 file_index += 1
    #             i += dirsize
    #         print lab,"done"
       
    #     if parralel:
    #         q=multiprocessing.Queue()
    #         r=multiprocessing.Queue()
    #         qwrites=[]
    #         rwrites=[]
    #         num_instances=0
    #         num_instances=len(self.instances)
    #         tweet_chunks=gen_functions.make_chunks(self.instances)
    #         for i in range(16):
    #             p=multiprocessing.Process(target=filewriter,args=[tweet_chunks[i],i,q,r])
    #             p.start()

    #         while len(qwrites) < num_instances:
    #             l=q.get()
    #             qwrites.append(l)
    #             outparts.write(l)
    #         while len(rwrites) < num_instances:
    #             l=r.get()
    #             rwrites.append(l)
    #             outmeta.write(l)
            
    #     else:      
    #         filewriter(self.instances,0)
            
    #     outparts.close()
    #     outmeta.close()
                
    # def generate_feature_indexes(self,vocabulary):
    #     """Generate a dictionary to be used for sparse and sparse binary output."""
    #     feature_frequency=defaultdict(int)
    #     vocabulary_out=codecs.open(vocabulary,"w","utf-8")
    #     self.feature_index={}
    #     for t in self.instances:
    #         for feature in t.features:
    #             feature_frequency[feature] += 1
        
    #     for i,feature in enumerate(feature_frequency.keys()):
    #          self.feature_index[feature]=i+1
    #          vocabulary_out.write(str(i) + "\t" + feature + "\n")

    # def features2sparsebinary(self,directory,prefix):
    #     """Write the features to a file in the sparse-binary format."""
        
    #     out=open(directory+"instances.txt","w")
    #     meta_out=codecs.open(directory+"meta.txt","w","utf-8")
    #     vocabulary_file = directory+"vocabulary.txt","w","utf-8"

    #     def generate_dataline(eventtweets,event):
    #         for t in eventtweets:
    #             tweets=t[0]
    #             tfz=t[1]
    #             datastring=""
    #             indexes=[]
    #             features=[]
    #             for tweet in tweets:
    #                 features.extend(tweet.features)
    #             features=list(set(features))
    #             for feature in features:
    #                 indexes.append(self.feature_index[feature])
    #             indexes=sorted(indexes)
    #             metatweet=tweets[-1]
    #             for index in indexes:
    #                 datastring=datastring + str(index) + ","
    #             datastring=datastring + metatweet.label + "\n"
    #             out.write(datastring)
    #             if metafile:
    #                 metastring="\t".join(metatweet.meta) + "\t" + " ".join(metatweet.wordsequence) + "\n"
    #                 meta_out.write(metastring)
    #         print event,"done"

    #     self.generate_feature_indexes(vocabulary_file)
    #     for event in self.event_tweets.keys():
    #         generate_dataline(self.event_tweets[event],event)

    #     out.close() 
    #     if metafile:            
    #         meta_out.close()
    
    # #turn the tweets into one big document
    # def features_2_bigdoc(self,outfile):
    #     outwrite = codecs.open(outfile,"w","utf-8")
    #     document = []
    #     for tweet in self.instances:
    #         document.extend(tweet.features)
    #     outwrite.write(" ".join(document))
    #     outwrite.close() 

    # def features_2_lda(self,outfile):
    #     out = codecs.open(outfile,"w","utf-8")
    #     for tweet in self.instances:
    #         line = tweet.id + "\tXXX\t" + tweet.date + "," + tweet.time + "\t" + " ".join(tweet.wordsequence) + "\n"
    #         out.write(line)
    #     out.close()

    class Tweet:
        """Class containing the features and characteristics of a tweet."""
        def __init__(self,tokens):
            self.label=tokens[0]
            self.id=str(tokens[1])
            self.user=tokens[2]
            self.date=str(tokens[3])
            self.time=str(tokens[4])
            self.text=tokens[5]
            self.wordsequence=[]
            self.features = []

        def set_meta(self):
            self.meta=[self.id,self.label,self.user,self.date,self.time]

        def get_datetime(self):
            return time_functions.return_datetime(self.date,self.time,"vs")
