#! /usr/bin/env python

import re
import urllib2
import datetime
import otter

# def for collecting tweets based on a keyword, returns tweet text with metadata
def extract_tweets(keyword,api,l):
    tweets_output = []
    keyword = "\"" + keyword + "\""
    tweets = api.search(q = keyword, result_type = "mixed", lang = l)["statuses"]
    for tweet in tweets:
        user = tweet["user"]["screen_name"]
        time = tweet["created_at"]
        text = re.sub("\n","",tweet["text"])
        tweet_id = tweet["id"]
        output = [tweet_id,"\t".join([keyword[1:-1],str(tweet_id),user,time,text]) + "\n"]
        tweets_output.append(output)

    return tweets_output

def collect_usertweets(api,user):
    outtweet = []
    tweetnr = 0
    for i in range(100):
        user_timeline = api.getUserTimeline(screen_name=user,page=i)
        if len(user_timeline) <= 0:
            if len(outtweet) == 0:
                return ["stop"]
            return outtweet
        for tweet in user_timeline:
            print tweet
            quit()
            try:
                time = tweet["created_at"]
                tweet_id = tweet["id"] 
                text = tweet["text"]
                tweetline = user + "||" + time + "||" + text
                outtweet.append(tweetline)
                tweetnr += 1
            except TypeError:
                if tweetnr >= 1950:
                    return outtweet
                else:
                    return ["stop"]

    return outtweet

def collect_user_topsy(username,kw):
    tweetlist = []
    for page in range(500):
#        try:
        search = otter.Resource('search', **kw)
        searchterm = "from:" + username 
        #    try:
        search(q=searchterm, type='tweet', perpage=100, page = page + 1)
        for item in search.response.list:
            print item
            tweetuser = item.trackback_author_nick
            tweetdate = datetime.datetime.fromtimestamp(int(item.trackback_date))
            tweet = item.content
            tweettokens = [tweetuser,str(tweetdate),tweet]
            tweetlist.append(tweettokens)
            #except UnicodeEncodeError:
            #    print "ascii..."
            #    continue
        #except urllib2.HTTPError:
         #   print "break..."
         #   break
        try:
            search = otter.Resource('search', **kw)
            searchterm = "from:" + username 
            try:
                search(q=searchterm, type='tweet', perpage=100, page = page + 1)
                for item in search.response.list:
                    tweetuser = item.trackback_author_nick
                    tweetdate = datetime.datetime.fromtimestamp(int(item.trackback_date))
                    tweet = item.content
                    tweettokens = [tweetuser,str(tweetdate),tweet]
                    print tweettokens
                    tweetlist.append(tweettokens)
            except UnicodeEncodeError:
                print "ascii..."
                continue
        except urllib2.HTTPError:
            print "break..."
            break
    return tweetlist

def collect_tweets_topsy(term):
    tweetlist = []
    for page in range(500):
        kw = otter.loadrc()
        search = otter.Resource('search', **kw)
        search(q=searchterm, type='tweet', perpage=100, page = page + 1)
        for item in search.response.list:
            tweetuser = item.trackback_author_nick
            tweetdate = datetime.datetime.fromtimestamp(int(item.trackback_date))
            tweet = item.content
            tweettokens = [tweetuser,str(tweetdate),tweet]
            tweetlist.append(tweettokens)
    #     except UnicodeEncodeError:
    #             print "ascii..."
    #             continue
    # except urllib2.HTTPError:
    #         print "break..."
    #         break
    return tweetlist
