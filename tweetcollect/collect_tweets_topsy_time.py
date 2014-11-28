#! /usr/bin/env python

import sys
import time
import datetime
import re
import time_functions
import urllib2
import json
import codecs

time_file = open(sys.argv[1])
tweet_file = codecs.open(sys.argv[2],"a","utf-8")
key = sys.argv[3]
try: 
    languagestring="&allow_lang=" + sys.argv[4]
except:
    languagestring=""

def s(btu,etu,page):
    print "http://otter.topsy.com/searchdate.json?apikey=HXKHTJKDA7J5Z3LDSAHAAAAAAC2GJE5XVVJAAAAAAAAFQGYA&q=" + key + "&mintime=" + btu + "&maxtime=" + etu + languagestring + "&type=tweet&perpage=100&page=" + str(page)
    search = urllib2.urlopen("http://otter.topsy.com/searchdate.json?apikey=HXKHTJKDA7J5Z3LDSAHAAAAAAC2GJE5XVVJAAAAAAAAFQGYA&q=" + key + "&mintime=" + btu + "&maxtime=" + etu + languagestring + "&type=tweet&perpage=100&page=" + str(page)) 
    print page
    data = json.load(search)
    print data
    return data
    
def collect_tweets(begin_time_unix,end_time_unix):
    datetweets = []
    p = 1
    d = s(begin_time_unix,end_time_unix,p)
    while len(d["response"]["list"]) > 0:
        for entry in d["response"]["list"]:
#            print entry["content"]
            print entry
            datetweets.append("\t".join([str(entry["topsy_trackback_url"].split("/")[-1]),time.strftime("%D %H:%M", time.localtime(entry["date"])),entry["trackback_author_nick"],re.sub("\n"," | ",entry["content"])]))
        p += 1
        d = s(begin_time_unix,end_time_unix,p)
    return datetweets

print key
date_time = time_file.readlines()[0].strip().split(" ")
begin_time = time_functions.return_datetime(date_time[0],time=date_time[1])
end_time = begin_time + datetime.timedelta(days=50)
begin_time_unix = str(int(time.mktime(begin_time.timetuple())))
end_time_unix = str(int(time.mktime(end_time.timetuple())))
print begin_time_unix,end_time_unix
new_tweets = collect_tweets(begin_time_unix,end_time_unix)
while len(new_tweets) > 0:
    print begin_time_unix,end_time_unix
    print "len",len(new_tweets)
    for t in new_tweets:
        tweet_file.write(t + "\n")
    begin_time = end_time
    end_time = begin_time + datetime.timedelta(days=50)
    begin_time_unix = str(int(time.mktime(begin_time.timetuple())))
    end_time_unix = str(int(time.mktime(end_time.timetuple())))
    new_tweets = collect_tweets(begin_time_unix,end_time_unix)

print "done"
tweet_file.close()

# begin_time = end_time
# end_time = begin_time + datetime.timedelta(days=1)
# begin_time_unix = begin_time.timestamp()
# end_time_unix = end_time.timestamp()
