from tweetprocessing32.tweetsfeatures import Tweetsfeatures
import copy
import argparse
import os

parser = argparse.ArgumentParser(description = "Find unique words for each domain")

parser.add_argument('-f', action='store', nargs='+', required = True, help = 'Folder where frogged files in it')
parser.add_argument('-g', action='store', nargs='+', required = False, help = 'if the file is frogged')

args = parser.parse_args()

folder = args.f


set_dict = {}
set_common_words = set()
set_all_words = set()
set_all_intersection = set()

for frogged_file in args.f:# how to give arg the folder.
	print(frogged_file)

	tf = Tweetsfeatures(frogged_file)
	tf.set_tweets(u=1, ht=1, p=1) # remove urls, hashtags and punctuation
	set_dict[frogged_file] = tf.get_words_set()
	set_all_words = set_all_words.union(set_dict[frogged_file]) # put all words in this set
	# print(set_dict[frogged_file])



for k in set_dict: # find specific words for each set
	# print("Number:", len(set_dict[k]),"--Unique in", k)
	# input("press enter for next file")

	set_temp = copy.deepcopy(set_dict[k])

	for k2 in set_dict:
		if k != k2:
			set_temp = set_temp - set_dict[k2]

	
	print("----------Specific words to:", k)
	print(*set_temp, sep='\n')
	# print("After distraction of other elements, Number:",len(set_temp))
	# input("press enter for next file")

set_all_intersection = copy.deepcopy(set_all_words)
for k in set_dict:
	set_all_intersection = set_all_intersection & set_dict[k]

print("----------All Common Words-------------")
print(*set_all_intersection, sep='\n')

print("----- All_Union - All Common Words : You can put this in stop words to see what if you use just common words for all domains affect the performance")
set_all_words_without_all_common = set()

print(*(set_all_words - set_all_intersection), sep='\n')











#For the word counts call wordCounts classes method. or create some other class.
#By sending file pointers, it should be possible to let the required data structures created.


# .........Code Notes ......
# import glob
# from TLangStatistics.wordcounts import SingleWordAnalysis #wordcounts
# if !(os.path.isdir(folder)):
# 	print("This is not a folder")

# elif !os.path.exists(folder):
# 	print("Folder does not exists")

# swa = SingleWordAnalysis() #No tweetfeatures ?
# swa.froggedToSet()

#for filename in glob.glob('/home/ali-hurriyetoglu/ADNEXT-Git/Data/fromAll/*.txt'):# how to give arg the folder.





