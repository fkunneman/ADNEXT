
import sys
import os
import re

textcol = int(sys.argv[1])
recurse = int(sys.argv[2]) * -1
outdir = sys.argv[3]
infiles = sys.argv[4:]

for infile in infiles:
    print infile
    parts = infile.split("/")
    ident = parts[recurse:]
    eventdir = outdir
    for part in ident:
        eventdir = eventdir + part + "/"
        if not os.path.exists(eventdir):
            os.system("mkdir " + eventdir)
    os.system("python ~/ADNEXT/tweetprocessing/tweets_2_corpus.py " + infile + " " + eventdir + "tweets" + " " + str(textcol))
    os.chdir(eventdir)
    os.system("colibri-classencode tweets")
    os.system("colibri-patternmodeller -f tweets.colibri.dat -t 1 -l 1 -o tweets.colibri.indexedpatternmodel")
    os.system("colibri-patternmodeller -i tweets.colibri.indexedpatternmodel -c tweets.colibri.cls -P > tweets_wordcounts_ranked.txt")

