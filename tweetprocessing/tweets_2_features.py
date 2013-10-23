#!/usr/bin/env python

import argparse
import codecs
from tweetsfeatures import Tweetsfeatures

"""
Script to generate instances with metadata and features, based on a file with lines of tweets, and output these in a specified format.
"""
parser = argparse.ArgumentParser(description = "Script to generate instances with metadata and features, based on a file with lines of tweets, and output these in a specified format.")
parser.add_argument('-i', action = 'store', required = True, help = "the input file")  
parser.add_argument('-n', action = 'store', nargs = '+', required = False, help = "the word n-grams that will be generated (for uni- and trigrams give \'1 3\')")
parser.add_argument('-cn', action = 'store', nargs = '+', required = False, help = "to include character n-grams, specify the values of \'n\'")
parser.add_argument('-rb', action = 'store', nargs='+', required = False, help = "[OPTIONAL] choose to remove features given after this parameter")
parser.add_argument('-ri', action = 'store', required = False, nargs = '+', help = "[OPTIONAL] remove instances if they contain one of the given words") 
parser.add_argument('-re', action = 'store', required = False, nargs = '+', help = "[OPTIONAL] remove instances if the do not end with a given hashtag (the given hashtag may still be followed by a URL or other hashtags)")
parser.add_argument('-rp', action = 'store', required = False, nargs = '+', help = "[OPTIONAL] to filter tweets before or after a point in time, specify the point in time and \'before\' or \'after\' respectively")
parser.add_argument('-ur', action = 'store_true', default = False, help = "[OPTIONAL] choose whether url's are normalized")
parser.add_argument('-us', action = 'store_true', default = False, help = "[OPTIONAL] choose whether usernames are normalized")
parser.add_argument('-lo', action = 'store_true', default = False, help = "[OPTIONAL] choose whether words are standardized to lower case")
parser.add_argument('-a', action = 'store', required = False, help = "[OPTIONAL] in order to aggregate instances by time the size of the window (in number of tweets) here")
# parser.add_argument('-o', action = 'store', required = True, choices = ["sparse","sparsebin","lcs","big","lda"], help = "specify the output type")
parser.add_argument('-o', action = 'store', required = True, help = "specify the output file")
# parser.add_argument('--prefix', action='store', required = False, help = "specify a prefix to characterize files in the directory")
# parser.add_argument('--parralel', action = 'store_true', help = "choose if parralel processing is done while writing to files")
parser.add_argument('--eos', action = 'store_true', help = "choose to retain end-of-sentence markers, if a feature with such a marker is removed (the marker will be added to previous word)")
args = parser.parse_args() 

print "Generating features..."
tf = Tweetsfeatures(args.i)
tf.set_wordsequences(lower=args.lo)
if args.ri:
    tf.filter_tweets(args.ri)
if args.re:
    tf.filter_tweets_reflexive_hashtag(args.re)
if args.rp:
    tf.filter_tweets_timepoint(args.rp[0],args.rp[1])

if args.ur:
    tf.normalize("url")
if args.us:
    tf.normalize("user")
    
if args.n:
    for n in args.n:
        tf.add_ngrams(n=int(n))
    if args.rb:
        tf.remove_blacklist(args.rb,args.eos)
if args.cn:
    tf.add_char_ngrams(args.cn,args.rb)

if args.a:
    tf.aggregate_instances(int(args.a))
tf.set_meta()

print "Writing classifier input..."
tf.output_features(args.o)

# if output_type == "lcs":    
#     tf.features2standard(args.d,args.prefix,args.parralel)
# elif output_type == "sparsebin":
#     tf.features2sparsebinary(target[0],target[1],target[2])
# elif output_type == "big":
#     tf.features_2_bigdoc(target[0])
# elif output_type == "lda":
#     tf.features_2_lda(target[0])
#tf.print_data(outfile)


