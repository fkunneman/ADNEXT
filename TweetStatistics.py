

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


tweets_file_big_temp = "/home/ali-hurriyetoglu/ADNEXT-Git/Data/football/frogged_tweets_league1112.txt"


#Be careful ! index of the names and times must be the same in the list
event_names=['tweaja','fcuexc','utrexc','grohee', \
             'psvvvv','fctrod','twerod','fctrjc', \
             'twerjc','feynac','necgra','ajaher', \
             'rkcado','vitaz', 'vitaza','excnec', \
             'aztwe','azatwe', 'rodfey','rjcfey', \
             'nacher','rkcpsv','heeaja','grafcu', \
             'grautr','vvvvit','adogro','psvaz', \
             'psvaza','nechee','feyexc','twenac',\
             'grorod','grorjc','utrvvv','fcuvvv', \
             'ajagra','vitado','herrkc','nacrjc',\
             'nacrod','heevit', 'rkcutr','rkcfcu',\
             'graher','exctwe','adofey','azavvv', \
             'azvvv','psvnec','ajagro','grogra', \
             'herhee','fcunac','utrnac','vitexc',\
             'vvvado','rodpsv','feyaza','feyaz', \
             'necrkc','feyher','necaza','necaz', \
             'twehee','gronac','rkcrjc','rkcrod',\
             'fcuvit','utrvit','graexc','ajavvv', \
             'psvado','heefey','adogra','excpsv',\
             'azagro','azgro', 'rjcfcu','rjcutr',\
             'rodfcu','rodutr','nacrkc','vitaja', \
             'vvvtwe','necvit','rkcfct','rkctwe',\
             'vitnec','fctrkc','twerkc','fcdgra',\
             'wiispa','helfce','sccvvv','grafcd', \
             'spawii','fcehel','vvvscc','rkcvit',\
             'vitrkc','fcdwii','helvvv','wiifcd','vvvhel'] # make it automatic
event_times = [datetime.datetime(2012,4,29,14,30,0), datetime.datetime(2012,3,30,20,0,0),datetime.datetime(2012,3,30,20,0,0),datetime.datetime(2012,3,31,18,45,0),\
               datetime.datetime(2012,3,31,19,45,0),datetime.datetime(2012,3,31,19,45,0),datetime.datetime(2012,3,31,19,45,0),datetime.datetime(2012,3,31,19,45,0),\
               datetime.datetime(2012,3,31,19,45,0),datetime.datetime(2012,3,31,20,45,0),datetime.datetime(2012,4,1,14,30,0),datetime.datetime(2012,4,1,14,30,0),\
               datetime.datetime(2012,4,1,14,30,0),datetime.datetime(2012,4,1,16,30,0),datetime.datetime(2012,4,1,16,30,0),datetime.datetime(2012,4,10,20,0,0),\
               datetime.datetime(2012,4,11,19,0,0),datetime.datetime(2012,4,11,19,0,0),datetime.datetime(2012,4,11,20,0,0),datetime.datetime(2012,4,11,20,0,0),\
               datetime.datetime(2012,4,11,20,0,0),datetime.datetime(2012,4,11,20,0,0),datetime.datetime(2012,4,11,21,0,0),datetime.datetime(2012,4,12,19,0,0),\
               datetime.datetime(2012,4,12,19,0,0),datetime.datetime(2012,4,12,20,0,0),datetime.datetime(2012,4,12,21,0,0),datetime.datetime(2012,4,14,18,45,0),\
               datetime.datetime(2012,4,14,18,45,0),datetime.datetime(2012,4,14,19,45,0),datetime.datetime(2012,4,14,19,45,0),datetime.datetime(2012,4,14,20,45,0),\
               datetime.datetime(2012,4,15,12,30,0),datetime.datetime(2012,4,15,12,30,0),datetime.datetime(2012,4,15,14,30,0),datetime.datetime(2012,4,15,14,30,0),\
               datetime.datetime(2012,4,15,14,30,0),datetime.datetime(2012,4,15,14,30,0),datetime.datetime(2012,4,15,16,30,0),datetime.datetime(2012,4,20,20,0,0),\
               datetime.datetime(2012,4,20,20,0,0),datetime.datetime(2012,4,21,18,45,0),datetime.datetime(2012,4,21,19,45,0),datetime.datetime(2012,4,21,19,45,0),\
               datetime.datetime(2012,4,21,19,45,0),datetime.datetime(2012,4,21,20,45,0),datetime.datetime(2012,4,22,12,30,0),datetime.datetime(2012,4,22,14,30,0),\
               datetime.datetime(2012,4,22,14,30,0),datetime.datetime(2012,4,22,14,30,0),datetime.datetime(2012,4,22,16,30,0),datetime.datetime(2012,4,27,20,0,0),\
               datetime.datetime(2012,4,28,18,45,0),datetime.datetime(2012,4,28,19,45,0),datetime.datetime(2012,4,28,19,45,0),datetime.datetime(2012,4,28,19,45,0),\
               datetime.datetime(2012,4,28,20,45,0),datetime.datetime(2012,4,29,12,30,0),datetime.datetime(2012,4,29,14,30,0),datetime.datetime(2012,4,29,14,30,0),\
               datetime.datetime(2012,4,29,16,30,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),\
               datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),\
               datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),\
               datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),\
               datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),\
               datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),\
               datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,10,19,0,0),datetime.datetime(2012,5,10,21,0,0),datetime.datetime(2012,5,10,21,0,0),\
               datetime.datetime(2012,5,13,14,30,0),datetime.datetime(2012,5,13,16,30,0),datetime.datetime(2012,5,13,16,30,0),datetime.datetime(2012,5,10,19,0,0),\
               datetime.datetime(2012,5,10,20,0,0),datetime.datetime(2012,5,10,20,0,0),datetime.datetime(2012,5,10,21,0,0),datetime.datetime(2012,5,13,12,30,0),\
               datetime.datetime(2012,5,13,14,30,0),datetime.datetime(2012,5,13,14,30,0),datetime.datetime(2012,5,13,16,30,0),datetime.datetime(2012,5,17,20,45,0),\
               datetime.datetime(2012,5,20,16,30,0),datetime.datetime(2012,5,17,12,30,0),datetime.datetime(2012,5,17,14,30,0),datetime.datetime(2012,5,20,12,30,0),datetime.datetime(2012,5,20,14,30,0)]
event_places = {'fce':'eindhoven','spa':'rotterdam','scc':'leeuwarden','fcd':'den bosch','aja':'amsterdam','fey':'rotterdam','psv':'eindhoven','fcu':'utrecht','utr':'utrecht','gro':'groningen','hee':'heerenveen','vvv':'venlo','twe':'enschede','fct':'enschede','rod':'kerkrade','rjc':'kerkrade','her':'almelo','nac':'breda','rkc':'waalwijk','ado':'den haag','az':'alkmaar','aza':'alkmaar','exc':'rotterdam','gra':'doetinchem','nec':'nijmegen','vit':'arnhem','wii':'tilburg','hel':'helmond'}
labels = ['before'] # it can include any others as well like: during, after, etc.

#Why is this strange error decrease than increase than again decrease.
#What other distances would provide
crea_event_objs_for=['tweaja','feyaz', 'feyaza','rodutr','excpsv','azgro', 'rjcfcu', 'adogra', 'rjcutr', 'vvvtwe', 'nacrkc','vitaja','heefey', 'rodfcu' ]
train_events = ['tweaja','feyaz', 'feyaza']
test_events = ['rodutr','excpsv','azgro', 'rjcfcu', 'adogra', 'rjcutr', 'vvvtwe', 'nacrkc','vitaja','heefey', 'rodfcu'] #14.30 sunday - 29/04/2012
#crea_event_objs_for=['ajavvv','feyher'] # Wednesday - 02/05/2012
#crea_event_objs_for=['ajavvv','tweaja'] # there is something in tweaja - same error rate increase
#crea_event_objs_for=['ajavvv','feyaz'] #try this and below.
#crea_event_objs_for=['feyher','tweaja']
#crea_event_objs_for=['feyher','feyaz']

#crea_event_objs_for=['vitaja', 'heefey'] # 14.30 sunday - 06/04/2012
#crea_event_objs_for=['vitaja', 'tweaja']
#crea_event_objs_for=['vitaja', 'feyaz']
#crea_event_objs_for=['heefey', 'tweaja']
#crea_event_objs_for=['heefey', 'feyaz']

#Random Experiments
#crea_event_objs_for=['nacrod','feyaz']


#controls:
#confirm match date and time



minueTimeFrame = 60
daycountback = 8


swa = SingleWordAnalysis(tweets_file_big_temp, event_names, event_times, event_places)
swa.crea_event_objs_for(labels, crea_event_objs_for) # just this list, restricted

# print(*swa.get_event_tweets_from_to(labels[0], 'ajavvv', 65, 85), sep='\n')
# exit()


#swa.crea_event_objs_for(labels, event_names) # all

#swa.calc_euc_distance_w('morgen', labels, crea_event_objs_for, minueTimeFrame, 8)


#for word counts more than range, plot predictions from normalized and smoothed frequencies.
same_count_control = 0
w_ĺist = []
for w_occur_count in range(50,51):

	w_list = swa.get_intersec_word_counts(w_occur_count, labels, [train_events, test_events] )

	swa.calc_euc_dist_w_list_normalized_random(w_list, labels, [train_events, test_events], minueTimeFrame, daycountback)
	#swa.calc_euc_dist_w_list_normalized(w_list, labels, [test_events,train_events], minueTimeFrame, daycountback)
  #smoothed
	#swa.calc_euc_dist_w_list(w_list, labels, [train_events, test_events], minueTimeFrame, daycountback)
	#swa.calc_euc_dist_w_list(w_list, labels, [test_events,train_events], minueTimeFrame, daycountback)
	same_count_control = len(w_list)

#swa.calc_euc_distance_w_list(['morgen', 'zondag'], labels, crea_event_objs_for, minueTimeFrame, 8)


#w_list = [] # put what ever you want in it.
#w_list = swa.get_intersec_word_counts('before', 'tweaja','feyaz', 1)
#for c_e in crea_event_objs_for:
	#swa.plot_word_list_of_label_of_event(w_list, 'before', c_e, minueTimeFrame, 8)


#plot words for the events listed in crea_event_objs_for list
# for c_e in crea_event_objs_for:
# 	swa.plot_words_of_label_of_event('before', c_e, minueTimeFrame, 8)


# Event based, word graphs
# for w in ['enschede', 'twente','ajax']:
# 	swa.plot_word_event_based(w,'before', 'tweaja', minueTimeFrame, 8) # word, label, event_name, minutesForFrame, day back count


# swa.count_words() # order of these mathods should be preserved.
# #swa.get_tweetCountPerEvent()
# swa.calc_words_freq()
# swa.calc_words_relative_freq()
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
#  --> swa.find_same_time_events() # 1. and 6. sequences different week, same weekday, same hour
#... Events per time ...

#Train
# 1 --2012-04-29 14:30:00 ['feyaz'(3326), 'feyaza'(18), 'tweaja'(3380)]
# 
# ?- 2 -- 2012-05-02 20:00:00 ['psvado'(801), 'twehee'(1127), 'feyher'(1885), 'fcuvit'(37), 'utrvit'(349), 'necaz'(249), 'ajavvv'(3308), 'graexc'(774),
#                        'rkcrod'(177), 'necaza', 'rkcrjc'(80), 'gronac' (291)]
# Test
# 3 --2012-05-06 14:30:00 ['rodutr'(130), 'excpsv(616)', 'azgro'(242), 'rjcfcu'(4), 'azagro'(0), 'adogra'(361), 'rjcutr'(40), 'vvvtwe'(338), 'nacrkc'(311),
#  'vitaja'(1056) : 6 may 14.30, 'heefey'(3168), 'rodfcu'(2)]
#

# 2 --2012-05-13 14:30:00 ['vitnec'(567), 'spawii'(3), 'fcehel'(71)]

# 2012-05-13 16:30:00 ['twerkc'(519), 'vvvscc'(11), 'fctrkc'(40)]
# 5 --2012-04-20 20:00:00 ['nacrjc'(69), 'nacrod'(191)]
#                       
# 
# 7 --2012-04-28 19:45:00 ['vitexc'(266), 'fcunac'(17), 'utrnac'(228)]
# 8 --2012-04-21 19:45:00 ['graher'(288), 'rkcfcu'(19), 'rkcutr'(188)]

# 2012-05-20 14:30:00 ['vvvhel']  --  2012-03-30 20:00:00 ['utrexc'(0), 'fcuexc'(0)]
# 2012-04-29 12:30:00 ['rodpsv']  --  2012-05-10 20:00:00 ['helfce'(0), 'wiispa'(6)]
# 2012-05-20 12:30:00 ['wiifcd']  --  2012-04-11 19:00:00 ['aztwe'(0), 'azatwe'(0)]
# 2012-05-17 14:30:00 ['helvvv']  --  2012-05-10 21:00:00 ['rkctwe'(0), 'sccvvv'(4), 'rkcfct'(0)]
# 2012-03-31 20:45:00 ['feynac']  --  2012-04-14 19:45:00 ['feyexc'(0), 'nechee'(0)]
# 2012-04-10 20:00:00 ['excnec']  --  2012-04-11 20:00:00 ['rodfey'(0), 'rkcpsv'(0), 'nacher'(0), 'rjcfey'(6)]
# 2012-04-28 20:45:00 ['vvvado']  --  2012-03-31 19:45:00 ['fctrod'(0), 'psvvvv'(0), 'twerjc'(0), 'twerod'(0), 'fctrjc'(0)]
# 2012-05-13 12:30:00 ['grafcd']  --  2012-04-22 14:30:00 ['psvnec', 'azavvv'(1), 'azvvv'(219)]
# 2012-03-31 18:45:00 ['grohee']  --  2012-04-11 21:00:00 ['heeaja']  --  2012-04-12 20:00:00 ['vvvvit']
# 2012-04-14 20:45:00 ['twenac']  --  2012-04-14 18:45:00 ['psvaz', 'psvaza']
# 2012-05-20 16:30:00 ['vitrkc']  --  2012-04-01 14:30:00 ['rkcado'(0), 'ajaher'(0), 'necgra'(0)]
# 2012-05-17 12:30:00 ['fcdwii']  --  2012-04-12 21:00:00 ['adogro']  --  
# 2012-04-28 18:45:00 ['herhee']  --  2012-04-12 19:00:00 ['grautr'(7), 'grafcu'(0)]
# 2012-04-29 16:30:00 ['necrkc']  --  2012-04-01 16:30:00 ['vitaza'(0), 'vitaz'(0)]
# 2012-04-22 16:30:00 ['ajagro']  --  2012-04-15 14:30:00 ['fcuvvv'(0), 'ajagra'(6), 'vitado'(0), 'utrvvv'(0)]
# 2012-04-15 16:30:00 ['herrkc']  --  2012-05-10 19:00:00 ['necvit'(0), 'fcdgra'(13)]
# 2012-04-21 20:45:00 ['exctwe']  --  2012-04-21 18:45:00 ['heevit']
# 2012-05-17 20:45:00 ['rkcvit']  -- 2012-04-15 12:30:00 ['grorjc'(0), 'grorod'(0)]
# 2012-04-27 20:00:00 ['grogra']  --  2012-04-22 12:30:00 ['adofey']
#-----------------------------------------------------------------------------
