#!/usr/bin/env python

import sys
import codecs
import re
import os

datefile = open(sys.argv[1])
outdir = sys.argv[2]
logs = sys.argv[3]

datelines = datefile.readlines()
current_date = time_functions.return_datetime(datelines[0].strip())
end_date = begin_date + timedelta(days=10)
datefile.close()

dates = []
while current_date <= end_date:
    date = str(current_date.year) + "-" + str(current_date.month) + "-" + str(current_date.day)
    dates.append(date)
    current_date += timedelta(days=1)

date_out = open(sys.argv[1],"w")
new_date = end_date + timedelta(days=1)
datewrites = []
for i,st in enumerate([new_date.day,new_date.month]):
    if len(str(st)) == 1:
        datewrites.append("0" + str(st))
    else:
        datewrites.append(str(st))
date_out.write(datewrites[0] + "-" + datewrites[1] + "-" + str(new_date.year))
date_out.close()

for date in dates:
    dateinfo = re.search(r"(\d{4})-(\d+)-(\d+)",date)
    year = dateinfo.groups()[0]
    month = dateinfo.groups()[1]
    day = dateinfo.groups()[2]
    if len(month) == 1:
        month = "0" + month
    if len(day) == 1:
        day = "0" + day
    date_cleaned = year + "-" + month + "-" + day
    date_out = outdir + date_cleaned + "/"
    date_log = logs + date_cleaned
    os.system("mkdir " + date_out)
    opened_file = open(infile)
    read_file = opened_file.read()
    opened_file.close()
    ids = re.findall(r'id=(\d+)\"', read_file, re.S)
    for id_ in ids:
        os.system("wget -w 0.1 -v --user=f.kunneman@let.ru.nl --password=crawl2013 -i http://portal.anp.nl/rss/indexer.do?action=article\&id=" + id_ + "\&format=xml" + " -o " + date_log + " -O " + date_out + id_)
