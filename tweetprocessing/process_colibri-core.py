
import sys
import os
import re

textcol = int(sys.argv[1])
recurse = int(sys.argv[2]) * -1
outdir = sys.argv[3]
dutchfilter = sys.argv[4]

infiles = sys.argv[5:]

for infile in infiles:
    print infile
    parts = infile.split("/")
    ident = parts[-1]
    eventdir = outdir
    #for part in ident:
    eventdir = eventdir + ident + "/"
    print ident,eventdir
    if not os.path.exists(eventdir):
        print "make"
        os.system("mkdir " + eventdir)
    os.system("python ~/ADNEXT/tweetprocessing/tweets_2_corpus.py " + infile + " " + eventdir + "tweets" + " " + str(textcol) + " " + dutchfilter)
    os.chdir(eventdir)
    os.system("colibri-classencode tweets")
    os.system("colibri-patternmodeller -f tweets.colibri.dat -t 1 -l 1 -o tweets.colibri.indexedpatternmodel")
    os.system("colibri-patternmodeller -i tweets.colibri.indexedpatternmodel -c tweets.colibri.cls -P > tweets_wordcounts_ranked.txt")
