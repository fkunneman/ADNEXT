#!/usr/bin/env python

import sys
import codecs
import re
import os

outdir = sys.argv[1]
infiles = sys.argv[1:]

for infile in infiles:
    date = infile.split("/")[-1]
    dateinfo = re.search(r"(\d{4})-(\d+)-(\d+)",date)
    print dateinfo.groups()
    quit()

    datedir = outdir + date + "/"
    print datedir
    os.system("mkdir " + outdir + date)
    opened_file = open(infile)
    read_file = opened_file.read()
    opened_file.close()
    ids = re.findall(r'id=(\d+)\"', read_file, re.S)
    for id_ in ids:
        os.system("wget -w 0.1 -v --user=f.kunneman@let.ru.nl --password=crawl2013 -i http://portal.anp.nl/rss/indexer.do?action=article\&id=" + id_ + "\&format=xml" + " -o " + outdir_logs + " -O " + outdir_files)