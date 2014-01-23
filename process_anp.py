#!/usr/bin/env python

import sys
import codecs
import re

infiles = sys.argv[1:]

for infile in infiles:
    opened_file = open(infile)
    read_file = opened_file.read()
    opened_file.close()
    ids = re.findall(r'id=(\d+)\"', read_file, re.S)
    print ids
