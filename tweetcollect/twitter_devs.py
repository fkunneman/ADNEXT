#! /usr/bin/env python

import re
import urllib2
import datetime
import otter

# def for collecting tweets based on a keyword, returns tweet text with metadata
def extract_tweets(keyword,api,l):
    tweets_output = []
    keyword = "\"" + keyword + "\""
#    print keyword,l
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
    no_tweets = False
    tweets_total = []
    c = 1

    while not no_tweets:
        tweets = api.get_user_timeline(screen_name=user,count=200,page=c)
        try:
            tweets = api.get_user_timeline(screen_name=user,count=200,page=c)
        except t.TwythonError:
            tweets = []
            print(user,'Twython is sad :(')
            break

        if len(tweets) < 1:
            no_tweets = True
        else:
            for tweet in tweets:
                    tweets_total.append("\t".join(str([tweet['id']),tweet['created_at'],tweet['text']]))
        c+= 1

    return tweets_total

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
