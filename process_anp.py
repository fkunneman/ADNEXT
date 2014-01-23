#!/usr/bin/env python

import sys
import codecs

infiles = sys.argv[1:]

for infile in infiles:
    op = codecs.open(infile,"r","utf-8")
    read = op.read()
    ps = read.split("<p>")
    for chunk in ps:
        print chunk.split("</p>")[0]
