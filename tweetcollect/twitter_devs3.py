#! /usr/bin/env python

import re
import datetime
import time
import time_functions

month = {"Jan":"01", "Feb":"02", "Mar":"03", "Apr":"04", "May":"05", "Jun":"06", "Jul":"07", "Aug":"08", "Sep":"09", "Oct":"10", "Nov":"11", "Dec":"12"}
date_time = re.compile(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d+) (\d{2}:\d{2}:\d{2}) \+\d+ (\d{4})")

# def for collecting tweets based on a keyword, returns tweet text with metadata
def extract_tweets(keyword,api,l):
    tweets_output = []
    keyword = "\"" + keyword + "\""
    tweets = api.search(q = keyword, result_type = "mixed", lang = l)["statuses"]
    for tweet in tweets:
        user = tweet["user"]["screen_name"]
        tm = tweet["created_at"]
        text = re.sub("\n","",tweet["text"])
        tweet_id = tweet["id"]
        output = [tweet_id,"\t".join([keyword[1:-1],str(tweet_id),user,tm,text]) + "\n"]
        tweets_output.append(output)

    return tweets_output

def collect_usertweets(api,user,max_c = 1000,cnt=200):
    no_tweets = False
    tweets_total = []
    c = 1

    while not no_tweets:
        try:
            tweets = api.get_user_timeline(screen_name=user,count=cnt,page=c)
            if len(tweets) < 1:
                no_tweets = True
            else:
                print(tweets[1])
                for tweet in tweets:
                    dtsearch = date_time.search(tweet["created_at"]).groups()
                    date = dtsearch[1] + "-" + month[dtsearch[0]] + "-" + dtsearch[3]
                    tm = dtsearch[2]
                    tweets_total.append("\t".join([str(tweet['id']),date,tm,tweet['text']]))
            c+= 1
            if c >= max_c:
                no_tweets = True
        except:
            print("limit exceeded")
            return [False]
            break

    return tweets_total

def return_tweet(api,tid):
    status = api.show_status(id=tid)
    tweet = [tid,status["user"]["screen_name"],time_functions.return_datetime(status["created_at"],setting="twitter"),status["text"]]
    return tweet
