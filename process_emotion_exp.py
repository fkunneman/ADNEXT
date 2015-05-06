#! /usr/bin/env python

import os
import argparse
import lineconverter
import codecs

parser = argparse.ArgumentParser(description = "pipe-line to perform a distant supervision \
    experiment based on tweets with (a) common hashtag(s)")

parser.add_argument('-i', action = 'store', nargs='+', required = False, 
    help = "the input files (if starting from tweets or tokenized tweets), application of \
    \'tweets_2_features.py\' is implied")
parser.add_argument('-l', action = 'store', required = True, 
    help = "the label linked to the hashtag(s)")
parser.add_argument('-f', action = 'store', required = True, 
    help = "the directory in which lcs files are stored")
parser.add_argument('-b', action = 'store', required = True, 
    help = "partsfile with background tweets (should refer to files in same dir as -f)")
parser.add_argument('-d', action = 'store', required = True, 
    help = "the directory of the experiment")
parser.add_argument('--target', action = 'store', required = False, 
    help = "if the target hashtag is different from the training hashtag, specify it here")  
parser.add_argument('--tokenize', action = 'store', required = False, 
    help = "specify if input files should be tokenized")
parser.add_argument('--classify', action = 'store', required = False, 
    help = "to perform classification (and prepare training and test), give the directory in \
    which classification is performed; without this parameter, only evaluation will be performed")
parser.add_argument('--config', action = 'store', required = False, 
    help = "name of standard config file (needed for classification)")
parser.add_argument('--tfeatures', action = 'store_true', 
    help = "choose to extract top_features from the training model")
parser.add_argument('--sample_training', action = 'store_true', 
    help = "choose to extract a sample from the training data for annotation")

args = parser.parse_args() 

background_file = args.b
label = args.l
directory = args.d
label_parts = directory + "parts.txt"
if args.target:
    target = args.target
else:
    target = label

#extract features from tweets
if args.i:
    print("Extracting features")
    outfile = directory + args.i.split("/")[-1][:-4] + "_features.txt"
    if args.tokenize:
        outfile_frogged = args.o + args.i.split("/")[-1][:-4] + "_frogged.txt"
        os.system("python3 ~/ADNEXT/tweetprocessing/tweets_2_features.py -i " + args.i + \
            " -o " + outfile + " --text 7 --user 6 --date 2 --time 3 --id 1 --frog " + \
            outfile_frogged + " --man " + args.l + " -ur -us -partcap -rb " + target + " \#" + \
            target + " -ri rt -re \#" + target + " -n 1 2 3")
    else:
        os.system("python3 ~/ADNEXT/tweetprocessing/tweets_2_features.py -i " + args.i + \
            " -o " + outfile + " --text 7 --user 6 --date 2 --time 3 --id 1 --man " + args.l + \
            " -ur -us -partcap -rb " + target + " \#" + target + " -ri rt -re " + " \#" + \
            target + " -n 1 2 3")
    #set tweets to features and lcs input
    print("Converting to lcs files")
    os.system("python3 ~/ADNEXT/classification/tweetfiles_2_lcsinput.py -i " + outfile + " -d " \
        + args.f + " -w " + directory + " -l " + args.l + " -p 12")

test = directory + "parts_test.txt"
if args.classify:
    print "setting test..."
    #set test in background tweets
    meta_grep = directory + "meta_" + target + "_bg.txt"
    new_parts = directory + "parts_test_total.txt"
    background_parts = directory + "parts_test_background.txt"
    background_label_parts = directory + "parts_test_" + target + ".txt"
    os.system("grep \#" + target + " " + background_dir + "meta.txt > " + meta_grep)
    os.system("python ~/ADNEXT/classification/synchronize_meta_parts_lcs.py " + background_dir + \
        "parts.txt " + meta_grep + " " + new_parts + " " + label)
    os.system("grep " + label + " " + new_parts + " > " + background_label_parts)
    os.system("grep -v " + label + " " + new_parts + " > " + background_parts)
    
    #sample training tweets from background tweets
    print "setting train..."
    background_training = directory + "parts_training_background.txt"
    bg_training_out = open(background_training,"w")
    background_parts_file = open(background_parts)
    lineconvert = lineconverter.Lineconverter(background_parts_file.readlines()," ")
    background_parts_file.close()
    label_parts_file = open(label_parts)
    size = len(label_parts_file.readlines())
    label_parts_file.close()
    extracted_lines = lineconvert.sample(sample_size=size,return_sample=True)
    for line in extracted_lines:
        bg_training_out.write(line)
    bg_training_out.close()
    bg_test_remains = directory + "parts_test_background_remains.txt"
    keep_out = codecs.open(bg_test_remains,"w","utf-8")
    for line in lineconvert.lines:
        keep_out.write(line)
    keep_out.close()
    #prepare training and test
    training = directory + "parts_train.txt"
    os.system("cat " + label_parts + " > " + training)
    os.system("cat " + background_training + " >> " + training)
    os.system("cat " + bg_test_remains + " > " + test)
    os.system("cat " + background_label_parts + " >> " + test)

    #clean up some files
    if os.path.exists(directory + "data/"):
        os.system("rm -r " + directory + "data/")
    if os.path.exists(directory + "index/"):
        os.system("rm -r " + directory + "index/")
    if os.path.exists(args.classify + "data/"):
        os.system("rm -r " + args.classify + "data/")
    if os.path.exists(args.classify + "index/"):
        os.system("rm -r " + args.classify + "index/")
    #perform classification
    print "performing classification..."
    os.system("python ~/ADNEXT/classification/classify_lcs.py -p " + training + " -t " + test + \
        " -d " + args.classify + " -c " + args.config + " -f " + args.f)

#perform evaluation
print "evaluating..."
results = directory + "results_" + target + ".txt"
os.system("python ~/ADNEXT/evaluation/evaluate_lcs.py -t " + test + " -c " + directory + \
    "test.rnk" + " -w " + results)

#extract top features
if args.tfeatures:
    print "extracting top features..."
    top_features = directory + "top_features_" + label + ".txt"
    top_features_sorted = directory + "top_features_" + label + "_sorted.txt"
    os.system("tail -n +7 " + directory + "data/" + label + "_3.mitp > " + top_features)
    os.system("campyon -k 1,2 -T -Z 2 " + top_features + " | head -500 > " + top_features_sorted)
#extract annotation sample
if args.sample_training:
    print "extracting annotation sample..."
    sample = directory + "sample_" + label + ".txt"
    os.system("python ~/ADNEXT/convert_lines.py -i " + directory + "meta.txt -o " + sample + \
        " -a extract --extract 250")
    os.system("campyon -k 8 -T " + sample + " > " + directory + "sample_" + label + "_text.txt")

