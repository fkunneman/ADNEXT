
import os
import argparse
import datetime
import time

"""
Script to collect tweets within a timeframe from twiqs
"""
parser = argparse.ArgumentParser(description = 
    "Script to collect tweets within a timeframe from twiqs")
parser.add_argument('-k', action = 'store', required = True, help = "the keyword")  
parser.add_argument('-s', action = 'store', required = True, help = 
    "the start time (format = YYYYMMDDHH)")
parser.add_argument('-f', action = 'store', required = True, help = 
    "the end time (format = YYYYMMDDHH)")
parser.add_argument('-i', action = 'store', required = True, help = "the ip")
parser.add_argument('-o', action = 'store', required = True, help = "the directory to write to")

args = parser.parse_args()

if args.k == "echtalles":
    current = datetime.datetime(int(args.s[:4]),int(args.s[4:6]),int(args.s[6:8]),int(args.s[8:]),0,0)
    end = datetime.datetime(int(args.f[:4]),int(args.f[4:6]),int(args.f[6:8]),int(args.f[8:]),0,0)
    while current <= end:
        print current
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
        outfile = args.o + timeobj + ".txt"
        print "curl -o " + outfile + " --cookie \'cookie=qg0TPoUmoLW3cYLk\' \'http://145.100.57.182//cgi-bin/twitter?SEARCH=echtalles&DATE=" + timeobj + "&DOWNLOAD\'"
        os.system("curl -o " + outfile + " --cookie \'cookie=qg0TPoUmoLW3cYLk\' \'http://145.100.57.182//cgi-bin/twitter?SEARCH=echtalles&DATE=" + timeobj + "&DOWNLOAD\'")
        outlines = []
        while len(outlines) <= 2:
            print "waiting for",outfile
            time.sleep(300)
            os.system("curl -o " + outfile + " --cookie \'cookie=qg0TPoUmoLW3cYLk\' \'http://145.100.57.182//cgi-bin/twitter?SEARCH=echtalles&DATE=" + timeobj + "&DOWNLOAD\'")
            outopen = open(outfile)
            outlines = outopen.readlines()
            outopen.close()
        current = current + datetime.timedelta(hours = 1)
