#! /usr/bin/env python

import os
import argparse
import lineconverter

parser = argparse.ArgumentParser(description = "")
parser.add_argument('-d', action = 'store', required = True, help = "the directory of the experiment")
parser.add_argument('-l', action = 'store', required = True, help = "the label linked to the hashtag")
parser.add_argument('-b', action = 'store', required = True, help = "the directory for background tweets")
parser.add_argument('-f', action = 'store', required = True, help = "the directory in which lcs files are stored")
parser.add_argument('-i', action = 'store', required = False, help = "the input file (if starting from tweets or frogged tweets)")  
parser.add_argument('-c', action = 'store', default = "/scratch/fkunneman/classify_lcs/", help = "the directory to perform lcs classification in (default is /scratch/fkunneman/classify_lcs/)")
parser.add_argument('--frog', action = 'store', required = False, help = "to frog, specify the port of the Frog server")
parser.add_argument('--features', action = 'store', required = True, help = "")


parser.add_argument('--header', action = 'store_true', default = "False", help = "choose to ignore the first line of the input-file")
parser.add_argument('--text', action = 'store', required = False, help = "give the field on a line that contains the text (starting with 0 (the third column would be given by '2'). If the lines only contain text, give '0'.")
parser.add_argument('--user', action = 'store', required = False, help = "if one of the fields contain a username, specify its column.")
parser.add_argument('--date', action = 'store', required = False, help = "if one of the fields contain a date, specify its column.")
parser.add_argument('--time', action = 'store', required = False, help = "if one of the fields contain a time, specify its column.")
parser.add_argument('--id', action = 'store', required = False, help = "if one of the fields contain a tweetid, specify its column.")
parser.add_argument('--label', action = 'store', required = False, help = "if one of the fields contain a label / score of the tweet, specify its column.")
parser.add_argument('--punct', action = 'store_true', default = False, help = "choose if punctuation should be removed from the output")
parser.add_argument('--parralel', action = 'store_true', default = False, help = "choose if the file should be processed in parralel (recommended for big files).")
parser.add_argument('--events', action = 'store', required = False, help = "if the event of a tweet should be given as a label, give a file containing the events")
parser.add_argument('--man', action = 'store', required = False, help = "specify a label that applies to all tweets")

args = parser.parse_args() 

background_dir = args.b
label = args.l
directory = args.d
label_parts = directory + label + "/parts.txt"

#frog the tweets
if args.i:
    tweets = args.i
    if args.frog:
        frogged_file = "/".join(tweets.split("/")[:-2]) + "frogged_tweets/frogged_" + tweets.split("/")[-1]
        os.system("python ~/ADNEXT/frog_tweets -i " + tweets + " -p " + args.frog + " -w " + frogged_file + "--text 7 --user 6 --date 2 --time 3 --id 1 --man " + label + " --parralel")
    else:
        frogged_file = tweets
#set tweets to lcs features
    os.system("python ~/ADNEXT/tweetprocessing/tweets_2_features.py -i " + frogged_file + " -n 1 2 3 -t tweet -rb " + label + " \#" + label + " -ur -us -o lcs -w " + args.f + " " + label[:2] + " 25000 " + label_parts + " " + directory + label + "/meta.txt" + " --parralel")
#set test in background tweets
meta_grep = directory + "meta_" + label + ".txt"
new_parts = directory + "parts_test_bg.txt"
background_parts = directory + "parts_test_background.txt"
background_label_parts = directory + "parts_test_" + label + ".txt"
os.system("grep \#" + label + " " + background_dir + "meta.txt > " + meta_grep)
os.system("python ~/ADNEXT/classification/synchronize_meta_parts_lcs.py " + background_dir + "parts.txt " + metagrep + " " + new_parts + " " + label)
os.system("grep " + label + " " + new_parts + " > " + background_label_parts
os.system("grep -v " + label + " " + new_parts + " > " + background_parts)
#draw train sample from background tweets
background_training = directory + "parts_training_background.txt"
bg_training_out = open(background_training,"w")
lineconvert = lineconverter.Lineconverter(background_parts," ")
label_parts_file = open(label_parts)
size = len(label_parts_file.readlines())
label_parts_file.close()
extracted_lines = lineconvert.extract_sample(size)
for line in extracted_lines:
    bg_training_out.write(line + "\n")
bg_training_out.close()
bg_test_remains = directory + "parts_test_background_remains.txt"
keep_out = codecs.open(bg_test_background,"w","utf-8")
for line in lineconvert.lines:
    keep_out.write(line + "\n")
keep_out.close()
#prepare training and test
training = directory + "parts_train.txt"
test = directory + "parts_test.txt"
os.system("cat " + label_parts + " > " + training)
os.system("cat " + background_training + " >> " + training)
os.system("cat " + bg_test_remains + " > " + test)
os.system("cat " + background_label_parts + " >> " + test

#clean up some files
os.system("rm -r " + directory + "data/")
os.system("rm -r " + directory + "index/")
os.system("rm -r " + args.c + "data/")
os.system("rm -r " + args.c + "index/")
#perform classification
os.system("python ~/ADNEXT/classification/classify.py -i " + training + " -v test -t " + test + " -c lcs -a " + args.c + " " + args.f)

#perform evaluation
results = directory + "results_" + label + ".txt"
fp = directory + "fp_" + label + ".txt"
os.system("python ~/ADNEXT/evaluation/evaluate.py -l " + directory + "test -c " + directory + "test.rnk -o " + results + " -i lcs -fp " + fp + " " + label + " 500 " + args.f)
#extract top features
top_features = directory + "top_features_" + label + ".txt"
top_features_sorted = directory + "top_features_" + label + "_sorted.txt"
os.system("tail -n +7 " + directory + "data/" + label + "_3.mitp > " + top_features)
os.system("campyon -k 1,2 -Z 2 " + top_features + " | head -500 > " + top_features_sorted)
#extract training sample
sample = directory + "sample_" + label + ".txt"
os.system("python ~/ADNEXT/convert_lines.py -i " + directory + "meta.txt -o " + sample + " -a extract --extract 500")





