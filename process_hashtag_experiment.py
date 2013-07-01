
import os

tweets
background_parts
label
directory

#frog the tweets
if args.frog:
    frogged_file = "/".join(tweets.split("/")[:-2]) + "frogged_tweets/frogged_" + tweets.split("/")[-1]
    os.system("python ~/ADNEXT/frog_tweets -i " + tweets + " -p " + args.frog + " -w " + frogged_file + "--text 7 --user 6 --date 2 --time 3 --id 1 --man " + label + " --parralel")
#set tweets to lcs features
if args.features:
    os.system("python ~/ADNEXT/tweetprocessing/tweets_2_features.py -i " + frogged_file + " -n 1 2 3 -t tweet -rb " + label + " \#" + label + " -ur -us -o lcs -w " + directory + "data/files/ " + label[:2] + " 25000 " + directory + label + "/parts_" + label + ".txt " + directory + label + "/meta_" + label + ".txt" + " --parralel")
#set test in background tweets
meta_grep = directory + "meta_" + label + ".txt"
new_parts = directory + "parts_test_bg.txt"
background_parts = directory + "parts_test_background.txt"
os.system("grep \#" + label + " " + background_dir + "meta.txt > " + metagrep)
os.system("python ~/ADNEXT/classification/synchronize_meta_parts_lcs.py " + background_dir + "parts.txt " + metagrep + " " + new_parts + " " + label)
os.system("grep -v " + label + " " + new_parts + " > " + background_parts)

#draw train sample from background tweets


#perform classification
os.system("python ADNEXT/classification/classify.py -i /vol/bigdata/users/fkunneman/exp/pathos/yolo/total/parts_train.txt -v test -t /vol/bigdata/users/fkunneman/exp/pathos/yolo/total/parts_test.txt -c lcs -a /scratch/fkunneman/classify_lcs/ /vol/bigdata/users/fkunneman/exp/pathos/data/files/")

#evaluate


"campyon -k 1,2 -Z 2 /vol/bigdata/users/fkunneman/exp/pathos/yolo/total/features_yolo.txt > /vol/bigdata/users/fkunneman/exp/pathos/yolo/total/features_yolo_sorted.txt"

"python ADNEXT/convert_lines.py -i /vol/bigdata/users/fkunneman/exp/pathos/yolo/total/meta_yolo.txt -o /vol/bigdata/users/fkunneman/exp/pathos/yolo/total/sample_yolo.txt -a extract --extract 500"





