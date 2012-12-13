

from TLangStatistics.wordcounts import SingleWordAnalysis #wordcounts

import sys


import argparse

parser = argparse.ArgumentParser(description = "calculate word statistics")

parser.add_argument('-e', action='store', required = True, help = 'File with eventtags, date and time, divided by a linebreak (for example \'grorod 15-04-2012 12:30\'')
parser.add_argument('-t', action='store', required = True, help = 'File with tweets in standard format')
parser.add_argument('-o', action='store', required = True, help = 'The name of the outputfile to write the coordinates to (extension .txt)')
parser.add_argument('-u', action='store', default = 'day', choices = ['day','hour','minute'], help = 'The unit of time by which the difference will be measured (one of \'day\', \'hour\' or \'minute\'')
parser.add_argument('--begin', action='store', type = int, required = True, help = 'The first unit of time of tweets related to an event to be counted (for example \'-7\' for 7 units before')
parser.add_argument('--end', action='store', type = int, required = True, help = 'The last unit of time of tweets related to an event to be counted (for example \'5\' for 5 units after')
parser.add_argument('--weekdays', action='store', nargs='+', default = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"], help = 'Restriction in the days of the week on which an event is held (default = all days)')
parser.add_argument('--timewindow', action='store', type = int, nargs=2, default = [0,24], help = 'Restriction in the window of time (in hours) within which an event may start on a day (default = all hours)')

args = parser.parse_args() 




dutch_words_file = "/home/ali-hurriyetoglu/Desktop/Python/resources/sonarfreqlist.txt"
stop_words_file = "/home/ali-hurriyetoglu/Desktop/Python/resources/dutch_stopwords.txt"
tweets_file_big = '/home/ali-hurriyetoglu/Desktop/Python/florian/tweets_matches_april_till_june_2012_frogged.txt'
tweets_file_small = '/home/ali-hurriyetoglu/Desktop/Python/florian/tagged_tweets_final_sample.txt'
tweets_file_big_temp = "/home/ali-hurriyetoglu/Desktop/Python/florian/frogged_tweets_league1112.txt"


self.swa = SingleWordAnalysis(tweets_file_big_temp, dutch_words_file, stop_words_file)
self.swa.count_words() # order of these mathods should be preserved.
self.swa.print_rest_words()
self.swa.calc_words_freq()
self.swa.calc_words_relative_freq()


class Menu:
	'''Display a menu and respond to choices when run.'''
	def __init__(self):

		dutch_words_file = "/home/ali-hurriyetoglu/Desktop/Python/resources/sonarfreqlist.txt"
		stop_words_file = "/home/ali-hurriyetoglu/Desktop/Python/resources/dutch_stopwords.txt"
		tweets_file_big = '/home/ali-hurriyetoglu/Desktop/Python/florian/tweets_matches_april_till_june_2012_frogged.txt'
		tweets_file_small = '/home/ali-hurriyetoglu/Desktop/Python/florian/tagged_tweets_final_sample.txt'
		tweets_file_big_temp = "/home/ali-hurriyetoglu/Desktop/Python/florian/frogged_tweets_league1112.txt"

		self.swa = SingleWordAnalysis(tweets_file_big_temp, dutch_words_file, stop_words_file)
		self.swa.count_words() # order of these mathods should be preserved.
		self.swa.print_rest_words()
		self.swa.calc_words_freq()
		self.swa.calc_words_relative_freq()
		
		self.choices = {
		"1": self.before_words_relfreq,
		"2": self.get_sorted_relfreq,
		"3": self.get_sorted_freq,
		"9": self.quit
		}

	def display_menu(self):
		print("""
		1. No function
		2. Get sorted relavant frequency...
		3. Get sorted freq
		9. Quit
		""")

	def run(self):
		'''Display the menu and respond to choices.'''
		while True:
			self.display_menu()
			choice = input("Enter an option: ")
			action = self.choices.get(choice)

			if action:
				action() # functions without/optional arguments can be called in this way.
			else:
				print("{0} is not a valid choice".format(choice))
	
	def before_words_relfreq(self):
		pass
		#self.swa.calc_words_relative_freq()

	def get_sorted_relfreq(self):
		self.swa.get_sorted_rel_freq()

	def get_sorted_freq(self):
		self.swa.calc_words_freq()


	def quit(self):
		print("Thank you for using Word Count Statistics Module.")
		sys.exit(0)

# Following code call Menu class.
# if __name__ == "__main__":
# 	Menu().run()