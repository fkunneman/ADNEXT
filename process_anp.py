#!/usr/bin/env python

import sys
import codecs
import re
import os

outdir = sys.argv[1]
logs = sys.argv[2]
infiles = sys.argv[3:]

for infile in infiles:
    date = infile.split("/")[-1]
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
        os.system("wget -w 0.1 -v --user=f.kunneman@let.ru.nl --password=crawl2013 -i http://portal.anp.nl/rss/indexer.do?action=article\&id=" + id_ + "\&format=xml" + " -o " + logs + " -O " + date_out + id_)
