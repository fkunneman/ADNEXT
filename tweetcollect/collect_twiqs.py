
import os
import argparse
import requests
import datetime
import time
import codecs

"""
Script to collect tweets within a timeframe from twiqs
"""
parser = argparse.ArgumentParser(description = 
    "Script to collect tweets within a timeframe from twiqs")
parser.add_argument('-k', action = 'store', required = True, help = "the keyword")
parser.add_argument('-u', action = 'store', required = True, help = "twiqs username")
parser.add_argument('-p', action = 'store', required = True, help = "twiqs password") 
parser.add_argument('-s', action = 'store', required = True, help = 
    "the start time (format = YYYYMMDDHH)")
parser.add_argument('-f', action = 'store', required = True, help = 
    "the end time (format = YYYYMMDDHH)")
parser.add_argument('-i', action = 'store', required = True, help = "the ip")
parser.add_argument('-o', action = 'store', required = True, help = "the directory to write to")

args = parser.parse_args()

looptime = 1
requestwait = 2
requestloop = int(30/requestwait)

#get cookie
s = requests.Session()
r = s.post("http://" + args.i + "/cgi-bin/twitter", data={"NAME":args.u, "PASSWD":args.p})

def request_tweets(t):
    try:
            output1st = requests.get("http://" + args.i + "/cgi-bin/twitter", params=t, cookies=s.cookies)
    except:
            print("output1st = false")
            output1st = False
    return output1st

def process_request(t1,t2):
    payload = {'SEARCH': args.k, 'DATE': t1 + "-" + t2, 'DOWNLOAD':True, 'SHOWTWEETS':True}
    print("fetching",payload["SEARCH"],"in",payload['DATE'],"from twiqs")
    output = False
    while not output:
        output = request_tweets(payload)
    dumpoutput = '#user_id\t#tweet_id\t#date\t#time\t#reply_to_tweet_id\t#retweet_to_tweet_id\t#user_name\t#tweet\t#DATE='+payload['DATE']+'\t#SEARCHTOKEN=' + args.k + '\n'
    if output.text[:1000] == dumpoutput: #If there isn't any tweet try the request again for 10 times.
        for i in range(0,requestloop):
            output = False
            while not output:
                time.sleep(60*requestwait) #Wait for the search done at twiqs.nl before the next request
                output = request_tweets(payload)
            if output.text != dumpoutput:
                break

    #Check the results one last time
    if output.text[:1000] == dumpoutput: #If there isn't any tweet again, it will skip this hour.
        print("no tweets last attempt")
    else:
        return output.text

if args.k == "echtalles":
    current = datetime.datetime(int(args.s[:4]),int(args.s[4:6]),int(args.s[6:8]),int(args.s[8:]),0,0)
    end = datetime.datetime(int(args.f[:4]),int(args.f[4:6]),int(args.f[6:8]),int(args.f[8:]),0,0)
    while current <= end:
        year = str(current.year)
        month = str(current.month)
        day = str(current.day)
        hour = str(current.hour)
        if len(month) == 1:
            month = "0" + month
        if len(day) == 1:
            day = "0" + day
        if len(hour) == 1:
            hour = "0" + hour
        timeobj = year+month+day+hour
        tweets = process_request(timeobj,timeobj)
        outfile = codecs.open(args.o + timeobj + ".txt","w","utf-8")
        outfile.write(tweets)
        outfile.close()
        current = current + datetime.timedelta(hours = 1)

else:
    tweets = process_request(args.s,args.f)
    outfile = codecs.open(args.o + args.k + ".txt","w","utf-8")
    outfile.write(tweets)
    outfile.close()
