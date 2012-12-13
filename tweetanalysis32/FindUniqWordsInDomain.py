from tweetprocessing32.tweetfeatures import Tweetsfeatures
import argparse
import os

#import glob
#from TLangStatistics.wordcounts import SingleWordAnalysis #wordcounts

parser = argparse.ArgumentParser(description = "Find unique words for each domain")

parser.add_argument('-f', action='store', nargs='+', required = True, help = 'Folder where frogged files in it')
parser.add_argument('-g', action='store', nargs='+', required = False, help = 'if the file is frogged')

args = parser.parse_args()

folder = args.f

# if !(os.path.isdir(folder)):
# 	print("This is not a folder")

# elif !os.path.exists(folder):
# 	print("Folder does not exists")

# swa = SingleWordAnalysis() #No tweetfeatures ?
# swa.froggedToSet()

#for filename in glob.glob('/home/ali-hurriyetoglu/ADNEXT-Git/Data/fromAll/*.txt'):# how to give arg the folder.
i=0
for frogged_file in args.f:# how to give arg the folder.
	print(frogged_file)

	tf = Tweetsfeatures(frogged_file)
	tf.set_tweets(u=1, ht=1, p=1) # remove urls, hashtags and punctuation
	set_list[i] = tf.get_words_set()
	print(set_list[i])
	i += 1

#For the word counts call wordCounts classes method. or create some other class.
#By sending file pointers, it should be possible to let the required data structures created.





