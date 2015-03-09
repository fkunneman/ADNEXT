#! /usr/bin/env python

import re
import datetime

month = {"Jan":"01", "Feb":"02", "Mar":"03", "Apr":"04", "May":"05", "Jun":"06", "Jul":"07", "Aug":"08", "Sep":"09", "Oct":"10", "Nov":"11", "Dec":"12"}
date_time = re.compile(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d+) (\d{2}:\d{2}:\d{2}) \+\d+ (\d{4})")

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
                    dtsearch = date_time.search(decoded["created_at"]).groups()
                    date = dtsearch[1] + "-" + month[dtsearch[0]] + "-" + dtsearch[3]
                    time = dtsearch[2]
                    tweets_total.append("\t".join([str(tweet['id']),date,time,tweet['text']]))
        c+= 1

    return tweets_total