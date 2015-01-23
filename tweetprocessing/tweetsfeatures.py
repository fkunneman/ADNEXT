#! /usr/bin/env python

import os
#import codecs
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
        self.features = [[]]

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
        li = [tx.replace('.','\.').replace('*','\*') for tx in li] # not to match anything with . (dot)
#        print(sorted(li),len(li))
        patterns = re.compile('\\b'+'\\b|\\b'.join(li)+'\\b')
#        print(patterns)
        neg_patterns = re.compile('\\b'+'\\b|\\b'.join(li)+'\\b')
        #all features
        feats = []
        for t in self.instances:
            if t.stemseq:
                features = [x.replace(" ","_") for x in re.findall(patterns," ".join(t.stemseq))]
            else:
                features = [x.replace(" ","_") for x in re.findall(patterns," ".join(t.wordsequence))]
            feats.append(len(features) / len(t.wordsequence))
            # if len([x for x in features if not x == '']) > 0:
            #     print(t.text,t.posseq,t.stemseq,features)
        if not len(feats) == len(self.instances):
            print("listfeatures and tweets not aligned, feats:",len(feats),", instances:",len(self.instances),"exiting program")
        for i,rf in enumerate(feats):
            self.instances[i].features.append(rf/max(feats))


        #calculated features

    def extract_timefeatures(self):
        convert_nums = {"enige":3,"enkele":3,"een paar":3, "een":1, "twee":2, "drie":3, "vier":4, "vijf":5, "zes":6, "zeven":7, "acht":8, "negen":9, "tien":10, "elf":11, "twaalf":12, "dertien":13, "veertien":14, "vijftien":15, "zestien":16, "zeventien":17, "achtien":18, "negentien":19, "twintig":20}
        convert_tu = {"dagen":1, "daagjes":1, "nachten":1, "nachtjes":1, "week": 7, "weken":7, "weekjes":7, "maand": 30, "maanden":30, "maandjes":30}
        # check = re.compile(r"\b(dagen|daagjes|nachten|nachtjes|weken|weekjes|maanden|maandjes)\b",re.IGNORECASE)
        days = re.compile(r"over iets (meer|minder) dan (\d+|een|twee|drie|vier|vijf|zes|zeven|acht|negen|tien|elf|twaalf|dertien|veertien|vijftien|zestien|zeventien|achtien|negentien|twintig) (dagen|daagjes|nachten|nachtjes|weken|weekjes|maanden|maandjes|week|maand)",re.IGNORECASE)
        days1 = re.compile(r"(over|nog) pakweg (\d+|een|twee|drie|vier|vijf|zes|zeven|acht|negen|tien|elf|twaalf|dertien|veertien|vijftien|zestien|zeventien|achtien|negentien|twintig) (dagen|daagjes|nachten|nachtjes|weken|weekjes|maanden|maandjes|week|maand)",re.IGNORECASE)
        days2 = re.compile(r"nog slechts (een kleine )?(\d+|een|twee|drie|vier|vijf|zes|zeven|acht|negen|tien|elf|twaalf|dertien|veertien|vijftien|zestien|zeventien|achtien|negentien|twintig) (dagen|daagjes|nachten|nachtjes|weken|weekjes|maanden|maandjes|week|maand)",re.IGNORECASE)
        days3 = re.compile(r"(\d+|een|twee|drie|vier|vijf|zes|zeven|acht|negen|tien|elf|twaalf|dertien|veertien|vijftien|zestien|zeventien|achtien|negentien|twintig) (dagen|daagjes|nachten|nachtjes|weken|weekjes|maanden|maandjes|week|maand) tot",re.IGNORECASE)
        days4 = re.compile(r"(met )?nog (een kleine |maar |slechts )?(\d+|een|twee|drie|vier|vijf|zes|zeven|acht|negen|tien|elf|twaalf|dertien|veertien|vijftien|zestien|zeventien|achtien|negentien|twintig) (dagen|daagjes|nachten|nachtjes|weken|weekjes|maanden|maandjes|week|maand)",re.IGNORECASE)
        days5 = re.compile(r"nog (maar )?(\d+|een|twee|drie|vier|vijf|zes|zeven|acht|negen|tien|elf|twaalf|dertien|veertien|vijftien|zestien|zeventien|achtien|negentien|twintig) (dagen|daagjes|nachten|nachtjes|weken|weekjes|maanden|maandjes|week|maand)",re.IGNORECASE)
        days6 = re.compile(r"(\d+|een|twee|drie|vier|vijf|zes|zeven|acht|negen|tien|elf|twaalf|dertien|veertien|vijftien|zestien|zeventien|achtien|negentien|twintig) (dagen|daagjes|nachten|nachtjes|weken|weekjes|maanden|maandjes|week|maand)( slapen)? tot",re.IGNORECASE)
        days7 = re.compile(r"(over|nog) (\d+|een|twee|drie|vier|vijf|zes|zeven|acht|negen|tien|elf|twaalf|dertien|veertien|vijftien|zestien|zeventien|achtien|negentien|twintig) (dagen|daagjes|nachten|nachtjes|weken|weekjes|maanden|maandjes|week|maand)",re.IGNORECASE)
        days8 = re.compile(r"(over|nog) (ruim|krap|een kleine|ongeveer|bijna) (\d+|een|twee|drie|vier|vijf|zes|zeven|acht|negen|tien|elf|twaalf|dertien|veertien|vijftien|zestien|zeventien|achtien|negentien|twintig) (dagen|daagjes|nachten|nachtjes|weken|weekjes|maanden|maandjes|week|maand)",re.IGNORECASE)
        days9 = re.compile(r"(over|nog) (maar |slechts |minimaal |maximaal |tenminste )?(enige|enkele|een paar|\d+|een|twee|drie|vier|vijf|zes|zeven|acht|negen|tien|elf|twaalf|dertien|veertien|vijftien|zestien|zeventien|achtien|negentien|twintig) (dagen|daagjes|nachten|nachtjes|weken|weekjes|maanden|maandjes)",re.IGNORECASE)
        days10 = re.compile(r"met (nog)? (maar |slechts )?(1|een) (dag|week|maand|jaar) (of wat)?( nog)? te gaan",re.IGNORECASE)
        days11 = re.compile(r"met (nog)? (maar|slechts)?( enige| enkele| een paar| een| 1) (dag|dagen|week|weken|maand|maanden) te gaan",re.IGNORECASE)

        for instance in self.instances:
            ws = " ".join(instance.wordsequence)
            m = False
            if days.search(ws):
                sh = days.search(ws)
                m = True
            elif days1.search(ws):
                sh = days1.search(ws)
                m = True
            elif days2.search(ws):
                sh = days2.search(ws)
                m = True
            elif days3.search(ws):
                sh = days3.search(ws)
                m = True
            elif days4.search(ws):
                sh = days4.search(ws)
                m = True
            elif days5.search(ws):
                sh = days5.search(ws)
                m = True
            elif days6.search(ws):
                sh = days6.search(ws)
                m = True
            elif days7.search(ws):
                sh = days7.search(ws)
                m = True
            elif days8.search(ws):
                sh = days8.search(ws)
                m = True
            elif days9.search(ws):
                sh = days9.search(ws)
                m = True
            if m:
                for unit in sh.groups():
                    if unit != None:
                        if unit in convert_nums.keys():
                            num = convert_nums[unit]
                        elif re.match(r"\d+",unit):
                            num = int(unit)
                        elif unit in convert_tu.keys():
                            tu = convert_tu[unit]
                days_ahead = num*tu
                tweet_datetime = time_functions.return_datetime(instance.date,time=instance.time,setting="vs")
                event_datetime = tweet_datetime + datetime.timedelta(days = days_ahead)
                feature = "date_" + event_datetime.strftime("%d-%m-%Y")             
                instance.features.append(feature)

    def extract_date(self):
        convert_nums = {"een":1, "twee":2, "drie":3, "vier":4, "vijf":5, "zes":6, "zeven":7, "acht":8, "negen":9, "tien":10, "elf":11, "twaalf":12, "dertien":13, "veertien":14, "vijftien":15, "zestien":16, "zeventien":17, "achtien":18, "negentien":19, "twintig":20}
        convert_month = {"jan":1, "januari":1, "feb":2, "februari":2, "mrt":3, "maart":3, "apr":4, "april":4, "mei":5, "jun":6, "juni":6, "jul":7, "juli":7, "aug":8, "augustus":8, "sep":9, "september":9, "okt":10, "oktober":10, "nov":11, "november":11, "dec":12, "december":12}
        dates = re.compile(r"([1,2,3]?\d|een|twee|drie|vier|vijf|zes|zeven|acht|negen|tien|elf|twaalf|dertien|veertien|vijftien|zestien|zeventien|achtien|negentien|twintig) (jan|januari|feb|februari|mrt|maart|apr|april|mei|jun|juni|jul|juli|aug|augustus|sep|september|okt|oktober|nov|november|dec|december)(\b|$)",re.IGNORECASE)
        for instance in self.instances:
            ws = " ".join(instance.wordsequence)
            if dates.search(ws):
                tweet_date = time_functions.return_datetime(instance.date,setting="vs")
                sh = dates.search(ws)
                if re.search(r"\d+",sh.groups()[0]):
                    day = int(sh.groups()[0])
                else:
                    day = convert_nums[sh.groups()[0]]
                month = convert_month[sh.groups()[1]]

                try:
                    date = datetime.datetime(tweet_date.year,month,day,0,0,0)
                    feature = "date_" + date.strftime("%d-%m-%Y")
                except:
                    continue
                instance.features.append(feature)  

    def extract_weekday(self):
        future=re.compile(r"(straks|zometeen|vanmiddag|vanavond|vannacht|vandaag|morgenmorgenavond|morgenmiddag|morgenochtend|overmorgen|weekend|maandag|dinsdag|woensdag|donderdag|vrijdag|zaterdag|zondag|maandagavond|dinsdagavond|woensdagavond|donderdagavond|vrijdagavond|zaterdagavond|zondagavond)")       
        today=re.compile(r"(straks|zometeen|vanmiddag|vanavond|vannacht|vandaag)",re.IGNORECASE)
        tomorrow=re.compile(r"(morgen|morgenavond|morgenmiddag|morgenochtend)",re.IGNORECASE)
        day_after_t=re.compile(r"overmorgen",re.IGNORECASE)
        weekend=re.compile(r"\b(weekend)\b",re.IGNORECASE)
        weekday=re.compile(r"(maandag|dinsdag|woensdag|donderdag|vrijdag|zaterdag|zondag)(avond|middag|ochtend)?",re.IGNORECASE)
        weekdays=["maandag","dinsdag","woensdag","donderdag","vrijdag","zaterdag","zondag"]

        for instance in self.instances:
            ws = " ".join(instance.wordsequence)
            da = False
            if weekend.search(ws,re.IGNORECASE) or weekday.search(ws):
                da = True
                tweet_date=time_functions.return_datetime(instance.date,setting="vs")
                tweet_weekday=tweet_date.weekday()
                if weekend.search(ws):
                    ref_weekday=weekdays.index("zaterdag")
                else:
                    ref_weekday=weekdays.index(weekday.search(ws).groups()[0])
                if ref_weekday == tweet_weekday:
                    days_ahead = 0
                elif tweet_weekday < ref_weekday:
                    days_ahead = ref_weekday - tweet_weekday
                else:
                    days_ahead = ref_weekday + (7-tweet_weekday)
            elif today.search(ws):
                da = True
                days_ahead = 0
            elif tomorrow.search(ws):
                da = True
                days_ahead = 1
            elif day_after_t.search(ws):
                da = True
                days_ahead = 2

            if da:
                days_ahead = int(days_ahead)
                tweet_datetime = time_functions.return_datetime(instance.date,time=instance.time,setting="vs")
                event_datetime = tweet_datetime + datetime.timedelta(days = days_ahead)
                feature = "date_" + event_datetime.strftime("%d-%m-%Y")               
                instance.features.append(feature)

    def match_rulelist(self,l):    
    # 1: match ids
        relevant_ids = set([x.id for x in self.instances]) & set([x.split("\t")[0] for x in l])
        matched_rules = [x.strip().split("\t") for x in l if x.split("\t")[0] in relevant_ids]
        matched_tweets = [x for x in self.instances if x.id in relevant_ids]
        for t in matched_tweets:
            tweet_datetime = time_functions.return_datetime(t.date,time=t.time,setting="vs")
            dif_feat = [x for x in matched_rules if x[0] == t.id][0]
            dif = dif_feat[-1]
            feat = dif_feat[2]
            event_datetime = tweet_datetime + datetime.timedelta(hours = int(float(dif)) * -1)
            feature = "date_" + event_datetime.strftime("%d-%m-%Y")
            t.features.append(feature)

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

    def add_tweetlength(self):
        for t in self.instances:
            tags = t.posseq
            tweetlength = len([x for x in tags if not x == 'LET()'])
            t.tl_absolute = tweetlength
        max_tl = max(t.tl_absolute for t in self.instances)
        for t in self.instances:
            tl_absolute = t.tl_absolute
            tl_relative = tl_absolute / max_tl
            t.features.append(tl_relative)

#    def add_stats(self,mention,hashtags,punct,upper):


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
        directory = "/".join(outfile.split("/")[directory_index])
        while True:
            if not os.path.exists("/".join(outfile.split("/")[directory_index])):
                directory_index -= 1
        while directory_index <= -1: 
            if not os.path.exists("/".join(outfile.split("/")[directory_index])):
                os.system("mkdir " + "/".join(outfile.split("/")[directory_index]))
            d += 1
        out = open(outfile,"w",encoding = "utf-8")
        for i in self.instances:
            out.write("\t".join(i.meta) + "\t" + " ".join(i.features[0]) + " | " + " ".join(i.features[1:]) + "\n")
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
            self.features = []

        def add_pos(self,seq):
            self.posseq = seq

        def add_stem(self,seq):
            self.stemseq = seq

        def set_meta(self):
            self.meta = [self.id,self.label,self.user,self.date,self.time]

        def get_datetime(self):
            return time_functions.return_datetime(self.date,self.time,"vs")


