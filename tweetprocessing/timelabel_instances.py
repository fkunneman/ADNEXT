    # def generate_tfz(self,agg=False):
    #     """
    #     Add time-from zero in days information to tweets based on their time of posting
    #     """
    #     event_tweets=defaultdict(list)
    #     event_tweets_tfz=defaultdict(list)
    #     for t in self.instances:
    #         event_tweets[t.event].append(t)
        
    #     for event in event_tweets.keys():
    #         tweets=event_tweets[event]
    #         tweets_tfz=[]
    #         tweets.sort(key=operator.methodcaller("get_datetime"), reverse=False)
    #         zeropoint=tweets[0].get_datetime()
    #         for t in tweets:
    #             tfz=int(time_functions.timerel(t.get_datetime(),zeropoint,"day"))
    #             t.tfz=str(tfz)
    #             tweets_tfz.append(([t],tfz))
    #             print t.get_datetime(),tfz        
    #         if agg:
    #             window=int(agg[0])
    #             slider=int(agg[1])
    #             event_tweets_tfz[event]=time_functions.extract_sliding_window_instances(tweets_tfz,window,slider)                    
    #         else: 
    #             event_tweets_tfz[event]=tweets_tfz
            
    #     return event_tweets_tfz

    def generate_time_label(self,timeunit,labeltype,threshold=False):
        """
        Add a label to tweets based on their tte
        The unit of time given as a label can be 'minute', 'hour' or 'day'.
        """
        threshold=threshold * -1
        for t in self.instances:
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