

from tweetanalysis33.wordcounts import SingleWordAnalysis #wordcounts

import sys
import time
import datetime
import getpass
#from joblib import Parallel, delayed

import argparse

parser = argparse.ArgumentParser(description = "calculate and find similarity of time series.")

# parser.add_argument("--testevents", help="Events to be tested, system should predict these.")
# parser.add_argument("-m", "--framemin", type=int, help = "Frame length in minutes")
# parser.add_argument("-d", "--daycountback", type=int, help="Day count to go back from the event")
parser.add_argument("--eventno", type=int, help="index of the event")
parser.add_argument("--minframe", type=int, help="frame length in minutes")
parser.add_argument("--dayback", type=int, help="How many days to go back")
parser.add_argument("--wcount", type=int, nargs='?', help="threshold for word counts")
parser.add_argument("-k", type=int, default= 1, help="how many nearest neighbors will be taken into account")
args = parser.parse_args() 

# print('Test events are:', args.testevents)
# print('Frame length in minutes:', args.m)
# print('Day count to go back:', args.d)
# exit()

indexno = args.eventno
w_count_threshold = args.wcount
minueTimeFrame = args.minframe
daycountback = args.dayback
k = args.k

print('Process Information(indexno, minueTimeFrame, daycountback, wcount, k):', indexno, minueTimeFrame, daycountback, w_count_threshold, k)
print('Note about the process:', 'Dev set trails')

#tweets_file_big_temp = "/vol/bigdata/users/fkunneman/exp/DIR13/data/tweets_converted.txt"
if getpass.getuser() == 'ali-hurriyetoglu':
  tweets_file_big_temp = "/home/ali-hurriyetoglu/ADNEXT-Git/Data/ftbll2011-12-700000tweets/tweets_converted.txt"
else:
  tweets_file_big_temp = "/vol/bigdata/users/fkunneman/exp/DIR13/data/tweets_converted.txt"

print('used file is:',tweets_file_big_temp)


#tweets_file_big_temp = "/home/ali-hurriyetoglu/ADNEXT-Git/Data/football/frogged_tweets_league1112.txt"
#tweets_file_big_temp = "/vol/bigdata/users/hurrial/Data/football/frogged_tweets_league1112.txt"

#Be careful ! index of the names and times must be the same in the list
event_names_same_time=['twefey_s11','utrtwe_s11','aztwe_s11','psvaja_s11', \
             'psvutr_s11','utrfey_s11','feypsv_s11','utraz_s11', \
             'ajatwe_s11','utrtwe_f11','utrfey_f11','feytwe_f11', \
             'psvaz_f12','utrpsv_f12', 'twefey_f12','utrtwe_f12', \
             'azfey_f12','utraz_f12', 'azaja_s12','utraz_s12', \
             'tweutr_s12','psvfey_s12','feyutr_s12','twefey_s12', \
             'feyaz_s12','tweaja_s12'] # make it automatic
event_times_same_time = [datetime.datetime(2011,1,30,14,30,0), datetime.datetime(2011,2,6,14,30,0),datetime.datetime(2011,2,27,14,30,0),datetime.datetime(2011,2,27,14,30,0),\
               datetime.datetime(2011,3,20,14,30,0),datetime.datetime(2011,4,10,14,30,0),datetime.datetime(2011,4,24,14,30,0),datetime.datetime(2011,5,15,14,30,0),\
               datetime.datetime(2011,5,15,14,30,0),datetime.datetime(2011,12,4,14,30,0),datetime.datetime(2011,12,11,14,30,0),datetime.datetime(2011,12,18,14,30,0),\
               datetime.datetime(2012,9,2,14,30,0),datetime.datetime(2012,9,16,14,30,0),datetime.datetime(2012,11,4,14,30,0),datetime.datetime(2012,11,18,14,30,0),\
               datetime.datetime(2012,11,25,14,30,0),datetime.datetime(2012,12,2,14,30,0),datetime.datetime(2012,1,22,14,30,0),datetime.datetime(2012,2,19,14,30,0),\
               datetime.datetime(2012,2,26,14,30,0),datetime.datetime(2012,2,26,14,30,0),datetime.datetime(2012,3,11,14,30,0),datetime.datetime(2012,3,18,14,30,0),\
               datetime.datetime(2012,4,29,14,30,0),datetime.datetime(2012,4,29,14,30,0)\
               ]

# 60 events
event_names_all = ['azpsv_f11','tweaz_f11','psvaja_f11','azfey_f11','ajatwe_f11','ajaaz_f11','psvutr_f11','ajafey_f11', \
            'twepsv_f11','utraja_f11','azutr_f11','feypsv_f11','utrtwe_f11','utrfey_f11','feytwe_f11','utrfey_f12','ajaaz_f12', \
            'psvaz_f12','utrpsv_f12','psvfey_f12','ajatwe_f12','ajautr_f12','tweaz_f12','feyaja_f12','twefey_f12','utrtwe_f12', \
            'azfey_f12','ajapsv_f12','utraz_f12','psvtwe_f12','ajafey_s11','utraja_s11','twefey_s11','utrtwe_s11','azpsv_s11', \
            'aztwe_s11','psvaja_s11','ajaaz_s11','psvutr_s11','twepsv_s11','feyaz_s11','utrfey_s11','feypsv_s11','utraz_s11', \
            'ajatwe_s11','azaja_s12','utrpsv_s12','feyaja_s12','ajautr_s12','utraz_s12','tweutr_s12','psvfey_s12','psvtwe_s12',\
            'feyutr_s12','twefey_s12','ajapsv_s12','aztwe_s12','psvaz_s12','feyaz_s12','tweaja_s12']


event_times_all = [datetime.datetime(2011,8,7,12,30,0),datetime.datetime(2011,8,13,18,45,0),datetime.datetime(2011,9,18,12,30,0),datetime.datetime(2011,9,24,12,30,0), \
        datetime.datetime(2011,9,24,20,45,0),datetime.datetime(2011,10,15,18,45,0),datetime.datetime(2011,10,15,20,45,0),datetime.datetime(2011,10,23,12,30,0), \
        datetime.datetime(2011,10,29,20,45,0),datetime.datetime(2011,11,6,12,30,0),datetime.datetime(2011,11,25,20,0,0),datetime.datetime(2011,12,4,12,30,0),\
        datetime.datetime(2011,12,4,14,30,0),datetime.datetime(2011,12,11,14,30,0),datetime.datetime(2011,12,18,14,30,0),datetime.datetime(2012,8,12,12,30,0),\
        datetime.datetime(2012,8,12,16,30,0),datetime.datetime(2012,9,2,14,30,0),datetime.datetime(2012,9,16,14,30,0),datetime.datetime(2012,9,23,16,30,0), \
        datetime.datetime(2012,9,29,20,45,0),datetime.datetime(2012,10,7,12,30,0),datetime.datetime(2012,10,7,16,30,0),datetime.datetime(2012,10,28,12,30,0), \
        datetime.datetime(2012,11,4,14,30,0),datetime.datetime(2012,11,18,14,30,0),datetime.datetime(2012,11,25,14,30,0),datetime.datetime(2012,12,1,20,45,0),\
        datetime.datetime(2012,12,2,14,30,0),datetime.datetime(2012,12,9,16,30,0),datetime.datetime(2011,1,19,20,45,0),datetime.datetime(2011,1,23,12,30,0),\
        datetime.datetime(2011,1,30,14,30,0),datetime.datetime(2011,2,6,14,30,0),datetime.datetime(2011,2,12,20,45,0),datetime.datetime(2011,2,27,14,30,0),\
        datetime.datetime(2011,2,27,14,30,0),datetime.datetime(2011,3,6,16,30,0),datetime.datetime(2011,3,20,14,30,0),datetime.datetime(2011,4,2,18,45,0),\
        datetime.datetime(2011,4,2,20,45,0),datetime.datetime(2011,4,10,14,30,0),datetime.datetime(2011,4,24,14,30,0),datetime.datetime(2011,5,15,14,30,0),\
        datetime.datetime(2011,5,15,14,30,0),datetime.datetime(2012,1,22,14,30,0),datetime.datetime(2012,1,22,16,30,0),datetime.datetime(2012,1,29,12,30,0),\
        datetime.datetime(2012,2,5,12,30,0),datetime.datetime(2012,2,19,14,30,0),datetime.datetime(2012,2,26,14,30,0),datetime.datetime(2012,2,26,14,30,0),\
        datetime.datetime(2012,3,4,16,30,0),datetime.datetime(2012,3,11,14,30,0),datetime.datetime(2012,3,18,14,30,0),datetime.datetime(2012,3,25,16,30,0),\
        datetime.datetime(2012,4,11,19,0,0),datetime.datetime(2012,4,14,18,45,0),datetime.datetime(2012,4,29,14,30,0),datetime.datetime(2012,4,29,14,30,0)]
        

event_places = {'fce':'eindhoven','spa':'rotterdam','scc':'leeuwarden','fcd':'den bosch','aja':'amsterdam','fey':'rotterdam','psv':'eindhoven','fcu':'utrecht','utr':'utrecht','gro':'groningen','hee':'heerenveen','vvv':'venlo','twe':'enschede','fct':'enschede','rod':'kerkrade','rjc':'kerkrade','her':'almelo','nac':'breda','rkc':'waalwijk','ado':'den haag','az':'alkmaar', \
                 'aza':'alkmaar','exc':'rotterdam','gra':'doetinchem','nec':'nijmegen','vit':'arnhem','wii':'tilburg','hel':'helmond'}

crea_event_objs_for_same_time=['twefey_s11','utrtwe_s11','aztwe_s11','psvaja_s11','psvutr_s11','utrfey_s11','feypsv_s11','utraz_s11', \
                    'ajatwe_s11','utrtwe_f11','utrfey_f11','feytwe_f11','psvaz_f12','utrpsv_f12', 'twefey_f12','utrtwe_f12', \
                    'azfey_f12','utraz_f12', 'azaja_s12','utraz_s12','tweutr_s12','psvfey_s12','feyutr_s12','twefey_s12', \
                    'feyaz_s12','tweaja_s12']


crea_event_objs_for_all = ['azpsv_f11','tweaz_f11','psvaja_f11','azfey_f11','ajatwe_f11','ajaaz_f11','psvutr_f11','ajafey_f11',\
              'twepsv_f11','utraja_f11','azutr_f11','feypsv_f11','utrtwe_f11','utrfey_f11','feytwe_f11','utrfey_f12','ajaaz_f12',\
              'psvaz_f12','utrpsv_f12','psvfey_f12','ajatwe_f12','ajautr_f12','tweaz_f12','feyaja_f12','twefey_f12','utrtwe_f12',\
              'azfey_f12','ajapsv_f12','utraz_f12','psvtwe_f12','ajafey_s11','utraja_s11','twefey_s11','utrtwe_s11','azpsv_s11',\
              'aztwe_s11','psvaja_s11','ajaaz_s11','psvutr_s11','twepsv_s11','feyaz_s11','utrfey_s11','feypsv_s11','utraz_s11',\
              'ajatwe_s11','azaja_s12','utrpsv_s12','feyaja_s12','ajautr_s12','utraz_s12','tweutr_s12','psvfey_s12','psvtwe_s12',\
              'feyutr_s12','twefey_s12','ajapsv_s12','aztwe_s12','psvaz_s12','feyaz_s12','tweaja_s12']

# train_events = ['twefey_s11','utrtwe_s11','aztwe_s11','psvaja_s11','psvutr_s11','utrfey_s11','feypsv_s11','utraz_s11','ajatwe_s11','utrtwe_f11','utrfey_s11','feytwe_f11']
# test_events = ['psvaz_f12','utrpsv_f12', 'twefey_f12','utrtwe_f12', 'azfey_f12','utraz_f12', 'azaja_s12','utraz_s12','tweutr_s12','psvfey_s12','feyutr_s12','twefey_s12', 'feyaz_s12','tweaja_s12']

# test_events_list = [['psvaz_f12'],['utrpsv_f12'], ['twefey_f12'],['utrtwe_f12'], ['azfey_f12'],['utraz_f12'], ['azaja_s12'],['utraz_s12'], \
#                     ['tweutr_s12'],['psvfey_s12'],['feyutr_s12'],['twefey_s12'], ['feyaz_s12'],['tweaja_s12']]

events_list_for_same_time = [['psvaz_f12'],['utrpsv_f12'], ['twefey_f12'],['utrtwe_f12'], ['azfey_f12'],['utraz_f12'], ['azaja_s12'],['utraz_s12'], \
                  ['tweutr_s12'],['psvfey_s12'],['feyutr_s12'],['twefey_s12'], ['feyaz_s12'],['tweaja_s12'], ['twefey_s11'],['utrtwe_s11'], \
                  ['aztwe_s11'],['psvaja_s11'],['psvutr_s11'],['utrfey_s11'],['feypsv_s11'],['utraz_s11'],['ajatwe_s11'],['utrtwe_f11'],\
                  ['utrfey_s11'],['feytwe_f11'], ['azutr_f11'], ['feypsv_f11']]

events_list_for_all = [['azpsv_f11'],['tweaz_f11'],['psvaja_f11'],['azfey_f11'],['ajatwe_f11'],['ajaaz_f11'],['psvutr_f11'],['ajafey_f11'],\
            ['twepsv_f11'],['utraja_f11'],['azutr_f11'],['feypsv_f11'],['utrtwe_f11'],['utrfey_f11'],['feytwe_f11'],['utrfey_f12'],\
            ['ajaaz_f12'],['psvaz_f12'],['utrpsv_f12'],['psvfey_f12'],['ajatwe_f12'],['ajautr_f12'],['tweaz_f12'],['feyaja_f12'],['twefey_f12'],\
            ['utrtwe_f12'],['azfey_f12'],['ajapsv_f12'],['utraz_f12'],['psvtwe_f12'],['ajafey_s11'],['utraja_s11'],['twefey_s11'],['utrtwe_s11'],\
            ['azpsv_s11'],['aztwe_s11'],['psvaja_s11'],['ajaaz_s11'],['psvutr_s11'],['twepsv_s11'],['feyaz_s11'],['utrfey_s11'],['feypsv_s11'],['utraz_s11'],\
            ['ajatwe_s11'],['azaja_s12'],['utrpsv_s12'],['feyaja_s12'],['ajautr_s12'],['utraz_s12'],['tweutr_s12'],['psvfey_s12'],['psvtwe_s12'],['feyutr_s12'],\
            ['twefey_s12'],['ajapsv_s12'],['aztwe_s12'],['psvaz_s12'],['feyaz_s12'],['tweaja_s12']]

labels = ['before'] # it can include any others as well like: during, after, etc.






swa = SingleWordAnalysis(tweets_file_big_temp, event_names_all, event_times_all, event_places)
#swa.load_train(train_events) #gets a list and make a Blend, aggregated, time serie
#swa.load_test(test_events)

swa.crea_event_objs_for(labels, crea_event_objs_for_all) # just this list, restricted


same_count_control = 0
w_ĺist = []

def test_by_index(tst_indexno, least_wc):
  for least_wc in [least_wc]:

    train_events = [l[0] for l in all_events_list if l != all_events_list[tst_indexno]]
    test_event = all_events_list[tst_indexno]
    print('Length of Train and Test event lists:',len(train_events), len(test_event))
    print('Train events:', train_events,'Tst event:', all_events_list[tst_indexno])

    w_list = swa.get_train_test_word_counts(least_wc, labels, [train_events, test_events_list[tst_indexno]])
    swa.calc_euc_dist_w_list_random_fast_normalizedByHighest_t_serie(w_list, labels, [train_events, test_event], minueTimeFrame, daycountback)


def test_by_index_trn01(trn_events, tst_event, least_wc, ts_type, k=1):
  
  w_list = swa.get_train_words(least_wc, labels, trn_events)
  w_list2 = swa.get_TrnTstIntersect_words(least_wc, labels, trn_events, tst_event)
  print('Wtrain and Wtrain-test Length, wthreshold:',len(w_list), len(w_list2), least_wc)
  
  swa.calc_by_vectors2([w_list,w_list2], labels, [trn_events, tst_event], minueTimeFrame, daycountback, ts_type, least_wc, k)
    

def test_by_index_tfidf(trn_events, tst_event, least_wc, ts_type, k=1):

    w_list = swa.get_train_words(least_wc, labels, trn_events)
    w_list2 = swa.get_TrnTstIntersect_words(least_wc, labels, trn_events, tst_event)
    print('Wtrain and Wtrain-test Length, wthreshold:',len(w_list), len(w_list2), least_wc)
  
    swa.calc_by_vectors_tfidf2([w_list, w_list2], labels, [trn_events, tst_event], minueTimeFrame, daycountback, ts_type, least_wc, k)

def get_tweets_of_timeframe():
  for i in range(0,170):
    print('\n----------------------range is:', i, i+1)
    print(*swa.get_event_tweets_from_to('before', all_events_list[indexno][0], i+1, i), sep='\n')



def get_rand(num, rang):
  '''(int, int) -> list
   - num: number of random integers
   - rang: 0-range of the random numbers

   Returns a list of random numbers in the range of 0-rang, length is num!

  '''
  rands = []
  for i in range(num):
      rands.append(randrange(60))
  return rands

#exit()
#test_by_index_trn01(indexno, w_count_threshold, 'normalized_w_tseries')
#test_by_index_trn01(indexno, w_count_threshold, 'smoothed_w_tseries')
#test_by_index_tfidf(indexno, w_count_threshold, 'normalized_w_tseries')



edev_indexlist = [21, 55, 52, 35, 16, 27, 13, 39, 40]
edev_list = [events_list_for_all[i] for i in edev_indexlist]
trnevents = [l[0] for l in events_list_for_all if l not in edev_list and l != events_list_for_all[indexno]]
print('\nlen of all events:', len(events_list_for_all),'\n', events_list_for_all)
print('\nlen of trne:', len(trnevents),'\n', trnevents)
print('\n len of dev-e indexes:', len(edev_indexlist),'\n', edev_indexlist)
print('\n len of dev-events:',len(edev_list), edev_list)
print('Test event is:',events_list_for_all[indexno])

if indexno not in edev_indexlist:
  for tstype in ['normalized_w_tseries', 'smoothed_w_tseries']:

    test_by_index_tfidf(trnevents, events_list_for_all[indexno], w_count_threshold, tstype, 16)
    test_by_index_trn01(trnevents, events_list_for_all[indexno], w_count_threshold, tstype, 16)


exit()


for tstype in ['normalized_w_tseries', 'smoothed_w_tseries']:
  for wcthreshold in [249, 149]: # should be sorted for a good performance at the beginning.
    for e in edev_list:

      print('***********************************************************************')
      print('Test Event, word threshold, tstype:', e, wcthreshold, tstype)
      print('***********************************************************************')
      
      test_by_index_tfidf(trnevents, e, wcthreshold, tstype, 16)
      test_by_index_trn01(trnevents, e, wcthreshold, tstype, 16)
      

exit()

for e in edev_list:

  print('***********************************************************************')
  print('Test Event, word threshold, tstype:', e, w_count_threshold , "smoothed_w_tseries")
  print('***********************************************************************')
      
  test_by_index_tfidf(trnevents, e, w_count_threshold, 'smoothed_w_tseries', 16)
  test_by_index_trn01(trnevents, e, w_count_threshold, 'smoothed_w_tseries', 16)


exit()


  # Get parameters from command line

test_by_index_tfidf(indexno, w_count_threshold,'normalized_w_tseries', 16)
print('Results of normalized tfidf')

test_by_index_tfidf(indexno, w_count_threshold,'smoothed_w_tseries', 16)
print('Results of smoothed tfidf')

test_by_index_trn01(indexno, w_count_threshold, 'normalized_w_tseries', 16)
print('Results of normalized binary')


test_by_index_trn01(indexno, w_count_threshold, 'smoothed_w_tseries', 16)
print('Results of smoothed binary')


exit()

print('Eliminate words that do not have peaks above 5. std:....')
t2 = time.time()
test_by_index_tfidf(indexno, w_count_threshold,'smoothed_w_tseries', k, 5)
print('Func optim. time:', time.time() - t2)

print('Eliminate words that do not have peaks above 6. std:....')
t2 = time.time()
test_by_index_tfidf(indexno, w_count_threshold,'smoothed_w_tseries', k, 6)
print('Func optim. time:', time.time() - t2)


print('Eliminate words that do not have peaks above 7. std:....')
t2 = time.time()
test_by_index_tfidf(indexno, w_count_threshold,'smoothed_w_tseries', k, 7)
print('Func optim. time:', time.time() - t2)

print('Do not eliminate any word...')
t3 = time.time()
test_by_index_tfidf(indexno, w_count_threshold,'smoothed_w_tseries', k, 0)
print('Func optim. time:', time.time() - t3)

exit()

t0 = time.time()
test_by_index_tfidf0(indexno, w_count_threshold,'smoothed_w_tseries')
print('Func. 0 time:', time.time() - t0)

t00 = time.time()
test_by_index_tfidf0(indexno, w_count_threshold,'smoothed_w_tseries')
print('Func. 0 time:', time.time() - t00)

t1 = time.time()
test_by_index_tfidf(indexno, w_count_threshold,'smoothed_w_tseries', 2)
print('Func optim. time:', time.time() - t1)



# test_by_index_tfidf(indexno, w_count_threshold,'smoothed_w_tseries', 2)
# print('Func optim. time:', time.time() - t1)


#tserie_type = 'smoothed_w_tseries'
#tserie_type = 'normalized_w_tseries'




exit()

test_by_index(indexno, 50)





# devset
# ajautr_f12 : 4761
# ajapsv_s12 : 9672
# psvtwe_s12 : 2705
# aztwe_s11 : 706
# ajaaz_f12 : 6039
# ajapsv_f12 : 11097
# utrfey_f11 : 1267
# twepsv_s11 : 3103
# feyaz_s11 : 851
#[['ajautr_f12'], ['ajapsv_s12'], ['psvtwe_s12'], ['aztwe_s11'], ['ajaaz_f12'], ['ajapsv_f12'], ['utrfey_f11'], ['twepsv_s11'], ['feyaz_s11']]

#swa.calc_euc_dist_w_list_normalized_random(w_list, labels, [train_events, test_events], minueTimeFrame, daycountback)
#swa.calc_euc_dist_w_list_normalized(w_list, labels, [test_events,train_events], minueTimeFrame, daycountback)
#smoothed
#swa.calc_euc_dist_w_list_random(w_list, labels, [train_events, test_events], minueTimeFrame, daycountback,10) #Actual one, before fast    
#swa.calc_euc_dist_w_list(w_list, labels, [test_events,train_events], minueTimeFrame, daycountback)
#same_count_control = len(w_list)

#swa.calc_euc_distance_w_list(['morgen', 'zondag'], labels, crea_event_objs_for, minueTimeFrame, 8)


#w_list = [] # put what ever you want in it.
#w_list = swa.get_intersec_word_counts('before', 'tweaja','feyaz', 1)
#for c_e in crea_event_objs_for:
#swa.plot_word_list_of_label_of_event(w_list, 'before', c_e, minueTimeFrame, 8)


#plot words for the events listed in crea_event_objs_for list
# for c_e in crea_event_objs_for:
#   swa.plot_words_of_label_of_event('before', c_e, minueTimeFrame, 8)


# Event based, word graphs
# for w in ['enschede', 'twente','ajax']:
#   swa.plot_word_event_based(w,'before', 'tweaja', minueTimeFrame, 8) # word, label, event_name, minutesForFrame, day back count


# swa.count_words() # order of these mathods should be preserved.
# #swa.get_tweetCountPerEvent()
# swa.calc_words_freq()
# swa.calc_words_relative_freq()
#swa.plot_word('ticket', 60, 8, True, True) # for the word 'de',x min periods, y days back, Count Tweets, running_average


# Produce many variations for a word:ticket
# for x in reversed([15, 30, 60, 120]):
#   for b in [True, False]:
#     swa.plot_word('ticket', x, 8, True, b)

# plot_words = ['de', 'een']
# # ['matchday', 'weekend', 'amsterdam','spelersbus', 'morge','morgen', 'klaarmaken', 'hoelaat', 'bussen', 'beschikbaar', 'verkoop', \
# #    'opstellingen','voorspel', 'morgenavond', 'vanaaf', 'kaartje','tickets',zenuwontsteking']

# for w in plot_words:
#   print(w)
#   swa.plot_word(w, 120, 8, True, True)

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
#3 -2012-05-06 14:30:00 ['rodutr'(130), 'excpsv(616)', 'azgro'(242), 'rjcfcu'(4), 'azagro'(0),
# 'adogra'(361), 'rjcutr'(40), 'vvvtwe'(338), 'nacrkc'(311),
#  'vitaja'(1056) : 6 may 14.30, 'heefey'(3168), 'rodfcu'(2)]
#

# [["heefey"],["adogra"],["excpsv"],["azgro"],["rjcfcu","rodfcu","rjcutr","rodutr"],["nacrkc"],["vitaja"],["vvvtwe"]]

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
# First Data: events and times for soccer match set - 65.000 tweets
#event_names=['tweaja','fcuexc','utrexc','grohee', \
#              'psvvvv','fctrod','twerod','fctrjc', \
#              'twerjc','feynac','necgra','ajaher', \
#              'rkcado','vitaz', 'vitaza','excnec', \
#              'aztwe','azatwe', 'rodfey','rjcfey', \
#              'nacher','rkcpsv','heeaja','grafcu', \
#              'grautr','vvvvit','adogro','psvaz', \
#              'psvaza','nechee','feyexc','twenac',\
#              'grorod','grorjc','utrvvv','fcuvvv', \
#              'ajagra','vitado','herrkc','nacrjc',\
#              'nacrod','heevit', 'rkcutr','rkcfcu',\
#              'graher','exctwe','adofey','azavvv', \
#              'azvvv','psvnec','ajagro','grogra', \
#              'herhee','fcunac','utrnac','vitexc',\
#              'vvvado','rodpsv','feyaza','feyaz', \
#              'necrkc','feyher','necaza','necaz', \
#              'twehee','gronac','rkcrjc','rkcrod',\
#              'fcuvit','utrvit','graexc','ajavvv', \
#              'psvado','heefey','adogra','excpsv',\
#              'azagro','azgro', 'rjcfcu','rjcutr',\
#              'rodfcu','rodutr','nacrkc','vitaja', \
#              'vvvtwe','necvit','rkcfct','rkctwe',\
#              'vitnec','fctrkc','twerkc','fcdgra',\
#              'wiispa','helfce','sccvvv','grafcd', \
#              'spawii','fcehel','vvvscc','rkcvit',\
#              'vitrkc','fcdwii','helvvv','wiifcd','vvvhel'] # make it automatic
# event_times = [datetime.datetime(2012,4,29,14,30,0), datetime.datetime(2012,3,30,20,0,0),datetime.datetime(2012,3,30,20,0,0),datetime.datetime(2012,3,31,18,45,0),\
#                datetime.datetime(2012,3,31,19,45,0),datetime.datetime(2012,3,31,19,45,0),datetime.datetime(2012,3,31,19,45,0),datetime.datetime(2012,3,31,19,45,0),\
#                datetime.datetime(2012,3,31,19,45,0),datetime.datetime(2012,3,31,20,45,0),datetime.datetime(2012,4,1,14,30,0),datetime.datetime(2012,4,1,14,30,0),\
#                datetime.datetime(2012,4,1,14,30,0),datetime.datetime(2012,4,1,16,30,0),datetime.datetime(2012,4,1,16,30,0),datetime.datetime(2012,4,10,20,0,0),\
#                datetime.datetime(2012,4,11,19,0,0),datetime.datetime(2012,4,11,19,0,0),datetime.datetime(2012,4,11,20,0,0),datetime.datetime(2012,4,11,20,0,0),\
#                datetime.datetime(2012,4,11,20,0,0),datetime.datetime(2012,4,11,20,0,0),datetime.datetime(2012,4,11,21,0,0),datetime.datetime(2012,4,12,19,0,0),\
#                datetime.datetime(2012,4,12,19,0,0),datetime.datetime(2012,4,12,20,0,0),datetime.datetime(2012,4,12,21,0,0),datetime.datetime(2012,4,14,18,45,0),\
#                datetime.datetime(2012,4,14,18,45,0),datetime.datetime(2012,4,14,19,45,0),datetime.datetime(2012,4,14,19,45,0),datetime.datetime(2012,4,14,20,45,0),\
#                datetime.datetime(2012,4,15,12,30,0),datetime.datetime(2012,4,15,12,30,0),datetime.datetime(2012,4,15,14,30,0),datetime.datetime(2012,4,15,14,30,0),\
#                datetime.datetime(2012,4,15,14,30,0),datetime.datetime(2012,4,15,14,30,0),datetime.datetime(2012,4,15,16,30,0),datetime.datetime(2012,4,20,20,0,0),\
#                datetime.datetime(2012,4,20,20,0,0),datetime.datetime(2012,4,21,18,45,0),datetime.datetime(2012,4,21,19,45,0),datetime.datetime(2012,4,21,19,45,0),\
#                datetime.datetime(2012,4,21,19,45,0),datetime.datetime(2012,4,21,20,45,0),datetime.datetime(2012,4,22,12,30,0),datetime.datetime(2012,4,22,14,30,0),\
#                datetime.datetime(2012,4,22,14,30,0),datetime.datetime(2012,4,22,14,30,0),datetime.datetime(2012,4,22,16,30,0),datetime.datetime(2012,4,27,20,0,0),\
#                datetime.datetime(2012,4,28,18,45,0),datetime.datetime(2012,4,28,19,45,0),datetime.datetime(2012,4,28,19,45,0),datetime.datetime(2012,4,28,19,45,0),\
#                datetime.datetime(2012,4,28,20,45,0),datetime.datetime(2012,4,29,12,30,0),datetime.datetime(2012,4,29,14,30,0),datetime.datetime(2012,4,29,14,30,0),\
#                datetime.datetime(2012,4,29,16,30,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),\
#                datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),\
#                datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,2,20,0,0),\
#                datetime.datetime(2012,5,2,20,0,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),\
#                datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),\
#                datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,6,14,30,0),\
#                datetime.datetime(2012,5,6,14,30,0),datetime.datetime(2012,5,10,19,0,0),datetime.datetime(2012,5,10,21,0,0),datetime.datetime(2012,5,10,21,0,0),\
#                datetime.datetime(2012,5,13,14,30,0),datetime.datetime(2012,5,13,16,30,0),datetime.datetime(2012,5,13,16,30,0),datetime.datetime(2012,5,10,19,0,0),\
#                datetime.datetime(2012,5,10,20,0,0),datetime.datetime(2012,5,10,20,0,0),datetime.datetime(2012,5,10,21,0,0),datetime.datetime(2012,5,13,12,30,0),\
#                datetime.datetime(2012,5,13,14,30,0),datetime.datetime(2012,5,13,14,30,0),datetime.datetime(2012,5,13,16,30,0),datetime.datetime(2012,5,17,20,45,0),\
#                datetime.datetime(2012,5,20,16,30,0),datetime.datetime(2012,5,17,12,30,0),datetime.datetime(2012,5,17,14,30,0),datetime.datetime(2012,5,20,12,30,0),datetime.datetime(2012,5,20,14,30,0)]

#



