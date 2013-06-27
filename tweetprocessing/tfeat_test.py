
import sys
import tweetsfeatures

frogged_tweets = sys.argv[1]
events = sys.argv[2]
outfile = sys.argv[3]

print "init"
collect = tweetsfeatures.Tweetsfeatures(frogged_tweets)
print "set tweets"
collect.set_tweets_one_line()
print "add ngrams"
collect.add_ngrams()
print "generate time label"
collect.generate_time_label(events,"\t","hour","category")
print "write to file"
collect.features2sparse(outfile)
