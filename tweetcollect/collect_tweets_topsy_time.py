#! /usr/bin/env python

import sys
import datetime
import time_functions
import urllib2

time_file = open(sys.argv[1])
tweet_file = open(sys.argv[2],"a")
language = sys.argv[3]

begin_time = time_functions.return_datetime(time_file.readlines()[0],time=True)
end_time = begin_time + datetime.timedelta(days=1)
begin_time_unix = begin_time.timestamp()
end_time_unix = end_time.timestamp()

tweets = []
page = 1
while True:
    search = urllib2.url("http://otter.topsy.com/searchdate.json?apikey=HXKHTJKDA7J5Z3LDSAHAAAAAAC2GJE5XVVJAAAAAAAAFQGYA&q=sarcasme&mintime=" + begin_time_unix + "&maxtime=" + end_time_unix + "&type=tweet&locale=" + language + "&perpage=100&page=" + page) 
    print page
    print search
    for entry in search["response"]["list"]:
        tweets.append("\t".join(entry["topsy_trackback_url"],entry["date"],entry["trackback_author_nick"],entry["content"]))
    page += 1


# begin_time = end_time
# end_time = begin_time + datetime.timedelta(days=1)
# begin_time_unix = begin_time.timestamp()
# end_time_unix = end_time.timestamp()

