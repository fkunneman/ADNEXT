#!/usr/bin/env python

import argparse
import codecs
from tweetsfeatures import Tweetsfeatures

"""
Script to generate instances with metadata and features, based on a file with lines of tweets, 
and output these in a specified format.
"""
parser = argparse.ArgumentParser(description = "Script to generate instances with metadata and \
    features, based on a file with lines of tweets, and output these in a specified format.")
parser.add_argument('-i', action = 'store', required = True, 
    help = "the input file")  
parser.add_argument('-e', action = 'store', required = False, 
    help = "choose to extract features based on the phrases in a file")
parser.add_argument('-n', action = 'store', nargs = '+', required = False, 
    help = "to include word n-grams, specify the values of \'n\'")
parser.add_argument('-r', action = 'store_true',
    help = "extract time features based on rules")
parser.add_argument('-d', action = 'store_true',
    help = "extract dates as time features")
parser.add_argument('-m', action = 'store', required = False,
    help = "list with rules to match")
parser.add_argument('-w', action = 'store_true',
    help = "extract weekdays as time features")
parser.add_argument('-cn', action = 'store', nargs = '+', required = False, 
    help = "to include character n-grams, specify the values of \'n\'")
parser.add_argument('-rb', action = 'store', nargs='+', required = False, 
    help = "[OPTIONAL] choose to remove features given after this parameter")
parser.add_argument('-ri', action = 'store', required = False, nargs = '+', 
    help = "[OPTIONAL] remove instances if they contain one of the given words") 
parser.add_argument('-re', action = 'store', required = False, nargs = '+', 
    help = "[OPTIONAL] remove instances if the do not end with a given hashtag (the given hashtag \
    may still be followed by a URL or other hashtags)")
parser.add_argument('-rw', nargs='+', action = 'store', required = False, nargs = '+', 
    help = "[OPTIONAL] to filter tweets outside of a specified timewindow, specify the two points \
    in time")
parser.add_argument('-ur', action = 'store_true', default = False, 
    help = "[OPTIONAL] choose whether url's are normalized")
parser.add_argument('-us', action = 'store_true', default = False, 
    help = "[OPTIONAL] choose whether usernames are normalized")
parser.add_argument('-lo', action = 'store_true', default = False, 
    help = "[OPTIONAL] choose whether words are standardized to lower case")
parser.add_argument('-o', action = 'store', required = True, 
    help = "specify the output file")
parser.add_argument('--eos', action = 'store_true', 
    help = "choose to retain end-of-sentence markers, if a feature with such a marker is removed \
    (the marker will be added to previous word)")
args = parser.parse_args() 

tf = Tweetsfeatures(args.i)
tf.set_wordsequences(lower=args.lo,us=args.us,ur=args.ur)

if args.ri:
    tf.filter_tweets(args.ri)
if args.re:
    tf.filter_tweets_reflexive_hashtag(args.re)
if args.rw:
    tf.filter_tweets_timepoint(args.rw[0],args.rw[1])

print "Generating features..." 
if args.e:
    #generate list
    extractfile = codecs.open(args.e,"r","utf-8")
    extracts = extractfile.read().split("\n")
    extractfile.close()
    tf.extract_listfeatures(extracts)
if args.r:
    tf.extract_timefeatures()
if args.d:
    tf.extract_date()
if args.w:
    tf.extract_weekday()
if args.m:
    l = codecs.open(args.m,"r","utf-8")
    tf.match_rulelist(l.readlines())
    l.close()
if args.n:
    for n in args.n:
        tf.add_ngrams(n=int(n))
    if args.rb:
        tf.remove_blacklist(args.rb,args.eos)
if args.cn:
    tf.add_char_ngrams(args.cn,args.rb)

print "Writing classifier input..."
tf.set_meta()
tf.output_features(args.o)
