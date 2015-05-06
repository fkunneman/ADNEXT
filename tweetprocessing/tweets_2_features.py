#!/usr/bin/env python

import argparse
from tweetsfeatures import Tweetsfeatures

"""
Script to generate instances with metadata and features, based on a file with lines of tweets, 
and output these in a specified format.
"""
parser = argparse.ArgumentParser(description = "Script to generate instances with metadata and \
    features, based on a file with lines of tweets, and output these in a specified format.")
parser.add_argument('-i', action = 'store', required = True, 
    help = "the input file")  
parser.add_argument('-o', action = 'store', required = True, 
    help = "specify the output file")

parser.add_argument('--header', action = 'store_true', 
    help = "choose to ignore the first line of the input-file")
parser.add_argument('--text', action = 'store', type=int, required = False, 
    help = "give the field on a line that contains the text (starting with 0 (the third column "
        "would be given by '2'). If the lines only contain text, give '0'.")
parser.add_argument('--user', action = 'store', type=int, required = False, 
    help = "if one of the fields contain a username, specify its column.")
parser.add_argument('--date', action = 'store', type=int, required = False, 
    help = "if one of the fields contain a date, specify its column.")
parser.add_argument('--time', action = 'store', type=int, required = False, 
    help = "if one of the fields contain a time, specify its column.")
parser.add_argument('--id', action = 'store', type=int, required = False, 
    help = "if one of the fields contain a tweetid, specify its column.")
parser.add_argument('--label', action = 'store', type=int, required = False, 
    help = "if one of the fields contain a label / score of the tweet, specify its column.")

parser.add_argument('--frog', action = 'store', help = "choose to frog the tweet texts, "
    "give an outfile for frogged tweets")
parser.add_argument('--man', action = 'store', required = False, 
    help = "specify a label that applies to all tweets")
parser.add_argument('-ur', action = 'store_true', default = False, 
    help = "choose whether url's are normalized")
parser.add_argument('-us', action = 'store_true', help = "choose whether usernames are normalized")
parser.add_argument('-lo', action = 'store_true', 
    help = "choose whether words are standardized to lower case")
parser.add_argument('-partcap', action = 'store_true', 
    help = "choose to normalize words to lowercase that -partly- consist of capitals")
parser.add_argument('--eos', action = 'store_true', 
    help = "choose to retain end-of-sentence markers, if a feature with such a marker is removed \
    (the marker will be added to previous word)")
parser.add_argument('-rb', action = 'store', nargs='+', required = False, 
    help = "choose to remove features given after this parameter")
parser.add_argument('-ri', action = 'store', required = False, nargs = '+', 
    help = "remove instances if they contain one of the given words") 
parser.add_argument('-re', action = 'store', required = False, nargs = '+', 
    help = "remove instances if they do not end with a given hashtag (the given hashtag \
    may still be followed by a URL or other hashtags)")
parser.add_argument('-rw', nargs='+', action = 'store', required = False, 
    help = "to filter tweets outside of a specified timewindow, specify the two points \
    in time")
parser.add_argument('-rp', action = 'store_true', default = False, 
    help = "choose if punctuation should be removed from the output")

parser.add_argument('-n', type = int, action = 'store', nargs = '+', required = False, 
    help = "to include word n-grams, specify the values of \'n\'")
parser.add_argument('-p', type = int, action = 'store', nargs = '+', required = False, 
    help = "to include pos n-grams, specify the values of \'n\'" 
        ", frog-argument should be included")
parser.add_argument('-s', type = int, action = 'store', nargs = '+', required = False, 
    help = "to include stem n-grams, specify the values of \'n\'" 
        ", frog-argument should be included")
parser.add_argument('-cn', type = int, action = 'store', nargs = '+', required = False, 
    help = "to include character n-grams, specify the values of \'n\'")
parser.add_argument('-l', nargs='+', action = 'store', required = False, 
    help = "choose to extract features based on the phrases in one or more files")
parser.add_argument('--pronoun', action = 'store_true',
    help = "choose to include second pronoun as feature"
    " (requires pos-tagging)")
parser.add_argument('--punct', action = 'store_true',
    help = "choose to include punctuation as feature"
    " (requires pos-tagging)")
parser.add_argument('--length', action = 'store_true',
    help = "choose to include tweet length as feature")
parser.add_argument('--cap', action = 'store_true',
    help = "choose to include capitalization as feature")
parser.add_argument('--ht', action = 'store_true',
    help = "choose to include hashtag count as feature")
parser.add_argument('--emo', action = 'store_true',
    help = "choose to include emoticons as feature")
#parser.add_argument('--sentiment', action = 'store_true',help = "choose to include the pattern sentiment "
#    " and subjectivity scores as features")

args = parser.parse_args() 

column_sequence = [args.label,args.id,args.user,args.date,args.time,args.text]
tf = Tweetsfeatures(args.i,column_sequence)

if args.frog:
    print("frogging tweets")
    tf.process_frog(args.rp)
    outfile = open(args.frog,"w",encoding="utf-8")
    for tweet in tf.instances:
        outfile.write("\t".join([tweet.label,tweet.id,tweet.user,tweet.date,tweet.time,tweet.text]) + "\n")
tf.set_sequences(lower=args.lo,us=args.us,ur=args.ur,cap=args.partcap)
if args.man:
    tf.add_label(args.man)

print("filtering tweets")
if args.ri:
    tf.filter_tweets(args.ri)
if args.re:
    tf.filter_tweets_reflexive_hashtag(args.re)
if args.rw:
    tf.filter_tweets_timewindow(args.rw[0],args.rw[1])

print("Generating features...") 
if args.l:
    #generate list
    for filename in args.l:
        extractfile = open(filename,"r",encoding = "utf-8")
        extracts = extractfile.read().split("\n")
        extractfile.close()
        listname = filename.split("/")[-1].split(".txt")[0]
        tf.extract_listfeatures(extracts,listname)
if args.n:
    tf.add_ngrams(args.n,t="word")
if args.p:
    tf.add_ngrams(args.p,t="pos")
if args.s:
    tf.add_ngrams(args.s,t="stem")
if args.rb:
    tf.remove_blacklist(args.rb,args.eos)
if args.cn:
    tf.add_char_ngrams(args.cn,args.rb,args.lo)
tf.add_stats(args.ht,args.cap,args.length,args.pronoun,args.punct,args.emo)
# if args.sentiment:
#     tf.add_sentiment()

print("Writing classifier input...")
tf.set_meta()
tf.output_features(args.o)
