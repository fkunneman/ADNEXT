
from __future__ import division
import re
import datetime

def return_datetime(date,time = False,setting = "eu"):
    """Put a date and time string in the python datetime format."""
    if setting == "eu":            
        parse_date = re.compile(r"(\d{2})-(\d{2})-(\d{4})")
        date = [parse_date.search(date).groups(1)[2],parse_date.search(date).groups(1)[1],parse_date.search(date).groups(1)[0]]
    elif setting == "vs":
        parse_date = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
        date = parse_date.search(date).groups(1)
    if time:
        parse_time = re.compile(r"(\d{2}):(\d{2})")
        timeparse = parse_time.search(time).groups(1)
        datetime_obj = datetime.datetime(int(date[0]),int(date[1]),int(date[2]),int(timeparse[0]),int(timeparse[1]),0)
    else:
        datetime_obj = datetime.datetime(int(date[0]),int(date[1]),int(date[2]),0,0,0)
    return datetime_obj

def timerel(time1,time2,unit):
    """Return the difference in time in a given time unit between two datetime objects.""" 
    dif = time1 - time2
    if unit == "day":
        zeropoint = datetime.datetime(time1.year,time1.month,time1.day,0,0,0)
        difzero = time1 - zeropoint
        dif += difzero
        day = int(dif.days)
        if dif.seconds > difzero.seconds: 
            day += 1
        return day
    elif unit == "hour":
        hours = (int(dif.days) * 24) + (int(dif.seconds) / 3600)
        return hours
    elif unit == "minute":   
        minutes = (int(dif.days) * 1440) + int(dif.seconds / 60)
        return minutes
        
def generate_event_time_hash(events,delimiter="\t"):
    """Based on an eventfile, generate a dictionary with events as keys and their start/end time as value."""
    event_time = {}
    eventfile_open = open(events)
    for event in eventfile_open:
        tokens = event.strip().split(delimiter)
        event_name = tokens[0]
        event_date_begin = tokens[1]
        event_time_begin = tokens[2]
        event_datetime_begin = return_datetime(event_date_begin,event_time_begin)
        
        event_date_end = tokens[3]
        event_time_end = tokens[4]
        event_datetime_end = return_datetime(event_date_end,event_time_end)
        event_time[event_name] = (event_datetime_begin,event_datetime_end)
    eventfile_open.close()
    return event_time


