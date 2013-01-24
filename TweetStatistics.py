

from tweetanalysis33.wordcounts import SingleWordAnalysis #wordcounts

import sys
import datetime


import argparse

parser = argparse.ArgumentParser(description = "calculate word statistics")

parser.add_argument('-e', action='store', required = False, help = 'File with eventtags, date and time, divided by a linebreak (for example \'grorod 15-4-2012 12:30\'')
parser.add_argument('-t', action='store', required = False, help = 'File with tweets in standard format')
parser.add_argument('-o', action='store', required = False, help = 'The name of the outputfile to write the coordinates to (extension .txt)')
parser.add_argument('-u', action='store', default = 'day', choices = ['day','hour','minute'], help = 'The unit of time by which the difference will be measured (one of \'day\', \'hour\' or \'minute\'')
parser.add_argument('--begin', action='store', type = int, required = False, help = 'The first unit of time of tweets related to an event to be counted (for example \'-7\' for 7 units before')
parser.add_argument('--end', action='store', type = int, required = False, help = 'The last unit of time of tweets related to an event to be counted (for example \'5\' for 5 units after')
parser.add_argument('--weekdays', action='store', nargs='+', default = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"], help = 'Restriction in the days of the week on which an event is held (default = all days)')
parser.add_argument('--timewindow', action='store', type = int, nargs=2, default = [0,24], help = 'Restriction in the window of time (in hours) within which an event may start on a day (default = all hours)')

args = parser.parse_args() 




dutch_words_file = "/home/ali-hurriyetoglu/Desktop/Python/resources/sonarfreqlist.txt"
stop_words_file = "/home/ali-hurriyetoglu/Desktop/Python/resources/dutch_stopwords.txt"
tweets_file_big_temp = "/home/ali-hurriyetoglu/ADNEXT-Git/Data/football/frogged_tweets_league1112.txt"


#Be careful ! index of the names and times must be the same in the list
event_names=['tweaja','fcuexc','utrexc','grohee','psvvvv','fctrod','twerod','fctrjc','twerjc','feynac','necgra','ajaher','rkcado','vitaz','vitaza','excnec','aztwe','azatwe','rodfey','rjcfey','nacher','rkcpsv','heeaja','grafcu','grautr','vvvvit','adogro','psvaz','psvaza','nechee','feyexc','twenac','grorod','grorjc','utrvvv','fcuvvv','ajagra','vitado','herrkc','nacrjc','nacrod','heevit','rkcutr','rkcfcu','graher','exctwe','adofey','azavvv','azvvv','psvnec','ajagro','grogra','herhee','fcunac','utrnac','vitexc','vvvado','rodpsv','feyaza','feyaz','necrkc','feyher','necaza','necaz','twehee','gronac','rkcrjc','rkcrod','fcuvit','utrvit','graexc','ajavvv','psvado','heefey','adogra','excpsv','azagro','azgro','rjcfcu','rjcutr','rodfcu','rodutr','nacrkc','vitaja','vvvtwe','necvit','rkcfct','rkctwe','vitnec','fctrkc','twerkc','fcdgra','wiispa','helfce','sccvvv','grafcd','spawii','fcehel','vvvscc','rkcvit','vitrkc','fcdwii','helvvv','wiifcd','vvvhel'] # make it automatic
event_times = [datetime.datetime(2012,4,29,14,30,0), datetime.datetime(2012,3,30,20,0,0),datetime.datetime(2012,3,30,20,0,0),datetime.datetime(2012,3,31,18,45,0),datetime.datetime(2012,3,31,19,45,0),datetime.datetime(2012,3,31,19,45,0),datetime.datetime(2012,3,31,19,45,0),datetime.datetime(2012,3,31,19,45,0),datetime.datetime(2012,3,31,19,45,0),datetime.datetime(2012,3,31,20,45,0),datetime.datetime(2012,4,1,14,30,0),datetime.datetime(2012,4,1,14,30,0),datetime.datetime(2012,4,1,14,30,0),datetime.datetime(2012,4,1,16,30,0),datetime.datetime(2012,4,1,16,30,0),datetime.datetime(2012,4,10,20,0,0),datetime.datetime(2012,4,11,19,0,0),datetime.datetime(2012,4,11,19,0,0),datetime.datetime(2012,4,11,20,0,0),datetime.datetime(2012,4,11,20,0,0),datetime.datetime(2012,4,11,20,0,0),datetime.datetime(2012,4,11,20,0,0),datetime.datetime(2012,4,11,21,0,0),datetime.datetime(2012,4,12,19,0,0),datetime.datetime(2012,4,12,19,0,0),datetime.datetime(2012,4,12,20,0,0),datetime.datetime(2012,4,12,21,0,0),datetime.datetime(2012,4,14,18,45,0),datetime.datetime(2012,4,14,18,45,0),datetime.datetime(2012,4,14,19,45,0),datetime.datetime(2012,4,14,19,45,0),datetime.datetime(2012,4,14,20,45,0),datetime.datetime(2012,4,15,12,30,0),datetime.datetime(2012,4,15,12,30,0),datetime.datetime(2012,4,15,14,30,0),datetime.datetime(2012,4,15,14,30,0),datetime.datetime(2012,4,15,14,30,0),datetime.datetime(2012,4,15,14,30,0),datetime.datetime(2012,4,15,16,30,0),datetime.datetime(2012,4,20,20,0,0),datetime.datetime(2012,4,20,20,0,0),datetime.datetime(2012,4,21,18,45,0),datetime.datetime(2012,4,21,19,45,0),datetime.datetime(2012,4,21,19,45,0),datetime.datetime(2012,4,21,19,45,0),datetime.datetime(2012,4,21,20,45,0),datetime.datetime(2012,4,22,12,30,0),datetime.datetime(2012,4,22,14,30,0),datetime.datetime(2012,4,22,14,30,0),datetime.datetime(2012,4,22,14,30,0),datetime.datetime(2012,4,22,16,30,0),datetime.datetime(2012,4,27,20,0,0),datetime.datetime(2012,4,28,18,45,0),datetime.datetime(2012,4,28,19,45,0),datetime.datetime(2012,4,28,19,45,0),datetime.datetime(2012,4,28,19,45,0),datetime.datetime(2012,4,28,20,45,0),datetime.datetime(2012,4,29,12,30,0),datetime.datetime(2012,4,29,14,30,0),datetime.datetime(2012,4,29,14,30,0),datetime.datetime(2012,4,29,16,30,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,10,19,0,0),datetime.datetime(2012,5,10,21,0,0),datetime.datetime(2012,5,10,21,0,0),datetime.datetime(2012,5,13,14,30,0),datetime.datetime(2012,5,13,16,30,0),datetime.datetime(2012,5,13,16,30,0),datetime.datetime(2012,5,10,19,0,0),datetime.datetime(2012,5,10,20,0,0),datetime.datetime(2012,5,10,20,0,0),datetime.datetime(2012,5,10,21,0,0),datetime.datetime(2012,5,13,12,30,0),datetime.datetime(2012,5,13,14,30,0),datetime.datetime(2012,5,13,14,30,0),datetime.datetime(2012,5,13,16,30,0),datetime.datetime(2012,5,17,20,45,0),datetime.datetime(2012,5,20,16,30,0),datetime.datetime(2012,5,17,12,30,0),datetime.datetime(2012,5,17,14,30,0),datetime.datetime(2012,5,20,12,30,0),datetime.datetime(2012,5,20,14,30,0)]
event_places = {'fce':'eindhoven','spa':'rotterdam','scc':'leeuwarden','fcd':'den bosch','aja':'amsterdam','fey':'rotterdam','psv':'eindhoven','fcu':'utrecht','utr':'utrecht','gro':'groningen','hee':'heerenveen','vvv':'venlo','twe':'enschede','fct':'enschede','rod':'kerkrade','rjc':'kerkrade','her':'almelo','nac':'breda','rkc':'waalwijk','ado':'den haag','az':'alkmaar','aza':'alkmaar','exc':'rotterdam','gra':'doetinchem','nec':'nijmegen','vit':'arnhem','wii':'tilburg','hel':'helmond'}
labels = ['before'] # it can include any others as well like: during, after, etc.

event_info = []

swa = SingleWordAnalysis(tweets_file_big_temp, dutch_words_file, stop_words_file, event_names, event_times)

swa.create_event_objects(event_names, event_times, event_places, labels)

for w in ['enschede', 'twente','ajax']:
	swa.plot_word_event_based(w,'before', 'tweaja', 120, 8) # word, label, event_name, minutesForFrame, day back count


swa.count_words() # order of these mathods should be preserved.
#swa.get_tweetCountPerEvent()
swa.calc_words_freq()
swa.calc_words_relative_freq()
#swa.plot_word('ticket', 60, 8, True, True) # for the word 'de',x min periods, y days back, Count Tweets, running_average


# Produce many variations for a word:ticket
# for x in reversed([15, 30, 60, 120]):
# 	for b in [True, False]:
# 		swa.plot_word('ticket', x, 8, True, b)

# plot_words = ['de', 'een']
# # ['matchday', 'weekend', 'amsterdam','spelersbus', 'morge','morgen', 'klaarmaken', 'hoelaat', 'bussen', 'beschikbaar', 'verkoop', \
# #    'opstellingen','voorspel', 'morgenavond', 'vanaaf', 'kaartje','tickets',zenuwontsteking']

# for w in plot_words:
# 	print(w)
# 	swa.plot_word(w, 120, 8, True, True)

# print('Finished:\n', plot_words)

#swa.plot_most_common_words(3)
#swa.get_sorted_rel_freq()
#swa.plot_most_relfreq_words_before()
#swa.get_sorted_freq()

#-----------------------------------------------------------------------------
#....... Tweet counts for each Before a soccer match
# tweaja 3380 - feyaz 3326 - ajavvv 3308 - heefey 3168 -feyher 1885 - ajagro 1727
# rkcvit 1345 bayche 1332 adofey 1170 twehee 1127
# vitaja 1056 vitrkc 1005 psvado 801 graexc 774
# psvnec 687 excpsv 616 vitnec 567 twerkc 519
# rodpsv 501 heevit 485 necrkc 481 exctwe 416
# grogra 395 helvvv 386 vvvhel 385 adogra 361
# utrvit 349 vvvtwe 338 herhee 335 nacrkc 311
# gronac 291 graher 288 vitexc 266 vvvado 251
# necaz 249 azgro 242 utrnac 228 azvvv 219
# nacrod 191 rkcutr 188 rkcrod 177 rodutr 130
# rkcrjc 80 fcehel 71 nacrjc 69 fctrkc 40
# rjcutr 40 fcuvit 37 rkcfcu 19 feyaza 18
# fcunac 17 fcdgra 13 vvvscc 11 adogro 10
# twenac 10 vvvvit 8 grautr 7 rjcfey 6
# wiispa 6 grafcd 6 ajagra 6 sccvvv 4
# rjcfcu 4 spawii 3 rodfcu 2 azavvv 1 psvaza 1 

#-----------------------------------------------------------------------------




