#!/usr/bin/env python

import sys
import codecs
import xml.etree.ElementTree as ET

infiles = sys.argv[1:]

for infile in infiles:
    tree = ET.parse(infile)
    root = tree.getroot()
    print root
