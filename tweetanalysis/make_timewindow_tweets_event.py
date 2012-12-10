#! /usr/bin/env python

from __future__ import division
import sys
import datetime
import re
from collections import defaultdict
import argparse

parser = argparse.ArgumentParser(description = "Produce a txt-file with timegraph-coordinates of tweetfrequency in time related to events")

parser.add_argument('-e', action='store', required = True, help = 'File with eventtags, date and time, divided by a linebreak (for example \'grorod 15-04-2012 12:30\'')
parser.add_argument('-t', action='store', required = True, help = 'File with tweets in standard format')
parser.add_argument('-o', action='store', required = True, help = 'The name of the outputfile to write the coordinates to (extension .txt)')
parser.add_argument('-u', action='store', default = 'day', choices = ['day','hour','minute'], help = 'The unit of time by which the difference will be measured (one of \'day\', \'hour\' or \'minute\'')
parser.add_argument('--begin', action='store', type = int, required = True, help = 'The first unit of time of tweets related to an event to be counted (for example \'-7\' for 7 units before')
parser.add_argument('--end', action='store', type = int, required = True, help = 'The last unit of time of tweets related to an event to be counted (for example \'5\' for 5 units after')
parser.add_argument('--weekdays', action='store', nargs='+', default = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"], help = 'Restriction in the days of the week on which an event is held (default = all days)')
parser.add_argument('--timewindow', action='store', type = int, nargs=2, default = [0,24], help = 'Restriction in the window of time (in hours) within which an event may start on a day (default = all hours)')

args = parser.parse_args() 

eventfile = open(args.e,"r")
tweetfile = open(args.t,"r")
outfile = open(args.o,"w")
timetype = args.u
begin = args.begin
end = args.end
dayrestriction = args.weekdays
timerestriction = args.timewindow

events = []
tweetwindow = defaultdict(int)

weekday_dict = {"monday" : 0, "tuesday" : 1, "wednesday" : 2, "thursday" : 3, "friday" : 4, "saturday" : 5, "sunday" : 6}
weekdays = []
for day in dayrestriction:
	daycode = weekday_dict[day]
	weekdays.append(daycode)

num_events = 0

parse_date = re.compile(r"(\d{2})-(\d{2})-(\d{4})")
parse_time = re.compile(r"(\d{2}):(\d{2})")
parse_datetime = re.compile(r"(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):\d{2}") 

for event in eventfile:
	eventinfo = event.split(" ")
	eventtag = eventinfo[0] 
	eventdate = eventinfo[1]
	eventtime = eventinfo[2]
	#eventdate_end = eventinfo[3]
	#eventtime_end = eventinfo[4]
	dateparse = parse_date.search(eventdate).groups(1)
	eventyear = int(dateparse[2])
	eventmonth = int(dateparse[1])
	eventday = int(dateparse[0])
	eventweekday = datetime.date(eventyear,eventmonth,eventday).weekday()
	if eventweekday in weekdays:
		timeparse = parse_time.search(eventtime).groups(1)
		eventhour = int(timeparse[0])
		eventminute = int(timeparse[1])
		if eventhour > timerestriction[0] and eventhour < timerestriction[1]:
			events.append((eventtag,eventyear,eventmonth,eventday,eventhour,eventminute))
			num_events += 1

for tweet in tweetfile:
	tweetinfo = tweet.split("\t")
	tweettext = tweetinfo[4]
	tweettag = tweetinfo[1]
	tweetdatetime = tweetinfo[3]
	try: 
		datetimeparse = parse_datetime.search(tweetdatetime).groups(1)
	except AttributeError:
		continue
	tweetyear = int(datetimeparse[0])
	tweetmonth = int(datetimeparse[1])
	tweetday = int(datetimeparse[2])
	tweethour = int(datetimeparse[3])
	tweetminute = int(datetimeparse[4])
	for eventtuple in events:
		eventtag = eventtuple[0]
		if eventtag == tweettag:
			eventyear = eventtuple[1]
			eventmonth = eventtuple[2]
			eventday = eventtuple[3]
			eventhour = eventtuple[4]
			eventminute = eventtuple[5]
			yeardif = tweetyear - eventyear
			monthdif = (yeardif * 12) + (tweetmonth - eventmonth)
			daydif = (monthdif * 30) + tweetday-eventday
			if timetype == "day" and daydif > begin and daydif < end:
				tweetwindow[daydif] += (1 / num_events)
			else:
				hourdif = (daydif * 24) + (tweethour - eventhour)
				if timetype == "hour" and hourdif > begin and hourdif < end:
					tweetwindow[hourdif] += (1 / num_events)
				else:
					minutedif = (hourdif * 60) + (tweetminute - eventminute)
					if timetype == "minute" and minutedif > begin and minutedif < end:
						tweetwindow[minutedif] += (1 / num_events)
			
dict_sorted = [x for x in tweetwindow.iteritems()]
dict_sorted.sort(key=lambda x: x[0]) # sort by key

for tup in dict_sorted:
	outfile.write(str(tup[0]) + "\t")
	outfile.write(str(tup[1]) + "\n")
