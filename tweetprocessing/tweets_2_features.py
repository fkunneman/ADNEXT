#!/usr/bin/env python

import argparse
import codecs
from tweetsfeatures import Tweetsfeatures

"""
Script to generate instances with metadata and features, based on a file with lines of tweets, and output these in a specified format.
"""
parser = argparse.ArgumentParser(description = "Script to generate instances with metadata and features, based on a file with lines of tweets, and output these in a specified format.")
parser.add_argument('-i', action = 'store', required = True, help = "the input file")  
parser.add_argument('-e', action = 'store', required = False, help = "[OPTIONAL] to link tweets to event time, specify a file with events")
parser.add_argument('-n', action = 'store', nargs = '+', required = True, help = "the word n-grams that will be generated (for uni- and trigrams give \'1 3\')")
parser.add_argument('-cn', action = 'store', nargs = '+', required = False, help = "to include character n-grams, give a file with raw (un-frogged) tweets and after this specify the column of the tweet id and the values of \'n\' (anything goes)")
parser.add_argument('-t', action = 'store', required = True, choices = ["term","tweet"], help = "the type of input (\'term\' refers to one term per line, \'tweet\' refers to a total tweet per line)")  
parser.add_argument('-rf', action = 'store_true', required = False, help = "[OPTIONAL] choose to remove features if they have a reference to one of the given events (only works in combination with \'-e\')")
parser.add_argument('-rb', action = 'store', nargs='+', required = False, help = "[OPTIONAL] choose to remove features given after this parameter")
parser.add_argument('-ri', action = 'store', required = False, nargs = '+', help = "[OPTIONAL] remove instances if they contain one of the given words") 
parser.add_argument('-re', action = 'store', required = False, nargs = '+', help = "[OPTIONAL] remove instances if the do not end with a given hashtag (the given hashtag may still be followed by a URL or other hashtags)")
parser.add_argument('-rw', action = 'store', required = False, nargs = '+', help = "[OPTIONAL] to remove instances based on their temporal distance related to an event, give a file with the event, the size of the time window (before and after the event instances are removed) and the timeunit ('hour' or 'day')")
parser.add_argument('-rp', action = 'store', required = False, nargs = '+', help = "[OPTIONAL] to filter tweets before or after a point in time, specify the point in time and \'before\' or \'after\' respectively")
parser.add_argument('-ur', action = 'store_true', default = False, help = "[OPTIONAL] choose whether url's are normalized")
parser.add_argument('-us', action = 'store_true', default = False, help = "[OPTIONAL] choose whether usernames are normalized")
parser.add_argument('-lo', action = 'store_true', default = False, help = "[OPTIONAL] choose whether words are standardized to lower case")
parser.add_argument('-tl', action = 'store', required = False, nargs = '+', help = "[OPTIONAL] for attaching time-to-event labels to instances, give a time unit (\'minute\', \'day\' or \'hour\'), a labeltype (\'before\' to only label and retain tweets before eventtime, \'category\' for the label \'after\' and \'time\' for temporal labels for after-tweets) and optionally a threshold before which tweets are not labeled with their tte, but with \'early\'.")
parser.add_argument('-a', action = 'store', required = False, nargs = '+', help = "[OPTIONAL] in order to aggregate instances by time, define the window and slider here")
parser.add_argument('-o', action = 'store', required = True, choices = ["sparse","sparsebin","lcs","big","lda"], help = "specify the output type")
parser.add_argument('-w', action = 'store', required = True, nargs = '+', help = "specify the target to write output to; for big and lda specify the outfile, for sparse(bin) specify the outfile, the vocabulary file and optionally the metafile and a \'1\' to give the time of a tweet with a given hashtag after the first occurence in time; for lcs give respectively the directory, prefix, dirsize, partsfile and metafile")
parser.add_argument('--parralel', action = 'store_true', help = "choose if parralel processing is done")
parser.add_argument('--text', action= 'store_true', help = "if the inputted tweets do not contain metadata, indicate by this parameter")
parser.add_argument('--eos', action = 'store_true', help = "choose to retain end-of-sentence markers, if a feature with such a marker is removed (the marker will be added to previous word)")

args = parser.parse_args() 
infile = args.i
events = args.e
ngrams = args.n
input_type = args.t
remove_features = args.rf
remove_instances = args.ri
remove_instances_window = args.rw
url = args.ur
user_name = args.us
time_labels = args.tl
output_type = args.o
target = args.w 

print "Generating features..."
tf = Tweetsfeatures(infile)
if input_type == "term":
    tf.set_tweets()
elif input_type == "tweet":
    if args.text:
        tf.set_tweets_one_line(lower = args.lo,info_type="text")
    else:
        tf.set_tweets_one_line(lower = args.lo)

if remove_instances:
    tf.filter_tweets(remove_instances)

if args.re:
    tf.filter_tweets_reflexive_hashtag(args.re)

if remove_instances_window:
    event_file = remove_instances_window[0]
    window_size = int(remove_instances_window[1])
    time_unit = remove_instances_window[2]
    tf.filter_tweets_timewindow(window_size,time_unit)

if args.rp:
    tf.filter_tweets_timepoint(args.rp[0],args.rp[1])

if url:
    tf.normalize("url")

if user_name:
    tf.normalize("user")
    
for n in ngrams:
    tf.add_ngrams(n=int(n))

if args.cn:
    tf.add_char_ngrams(args.cn[0],args.cn[2:],int(args.cn[1]),args.text,args.rb)

if events:
    tf.set_events(events,args.a)

if remove_features:
    tf.remove_eventmention()

if args.rb:
    tf.remove_blacklist(args.rb,args.eos)

if time_labels:
    time_unit = time_labels[0]
    label_type = time_labels[1]
    if len(time_labels) > 2:
        tf.generate_time_label(time_unit,label_type,int(time_labels[2]))
    else:
        tf.generate_time_label(time_unit,label_type)

tf.set_meta()

print "Writing classifier input..."
if output_type == "lcs":    
    target_dir = target[0]
    prefix = target[1]
    dirsize = int(target[2])
    partsfile = target[3]
    metafile = target[4]
    tf.features2standard(target_dir, prefix, dirsize, partsfile, metafile, args.a,args.parralel)
elif output_type == "sparsebin":
    tf.features2sparsebinary(target[0],target[1],target[2],target[3],args.a,args.parralel)
elif output_type == "big":
    tf.features_2_bigdoc(target[0])
elif output_type == "lda":
    tf.features_2_lda(target[0])

