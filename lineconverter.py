
import codecs
import re
import datetime
import random
#from pattern.nl import parse, pprint, sentiment

""" 
Class to convert the lines in a file in a number of ways and/or make a 
filtering of these.
"""
class Lineconverter():
	# Give the file with lines and the standard delimiter between fields 
	#    on a line (also if there is only one field)
	def __init__(self,lines,header):
		if header:
			self.lines = lines[1:]
			self.header = lines[0]
		else:
			self.header = False
			self.lines = lines

	# Add the same string to the back or front of each line 
	#   (argument [place] can be 'front' or 'back')
	def add_string(self,string,place):
		for line in self.lines:
			if place == "back":
				line.append(string)
			else:
				line.insert(place,string)

	def add_twitter_url(self,column_1,column_2):
		if self.header:
			self.header.append("#tweet_url")
		for line in self.lines:
			try:
				line.append("https://twitter.com/" + line[column_1] + "/status/" + line[column_2])
			except IndexError:
				print("index for twitter url non existant")
				continue

	def add_sentiment(self,column):
		if self.header:
			self.header.extend(["#polarity","#subjectivity"])
		i = 0
		while i < len(self.lines):
			line = self.lines[i]
#			try:
		#		senti = sentiment(line[column])
		#		line.extend([str(senti[0]),str(senti[1])])
		#		i+=1
		#	except:
		#		if i == len(self.lines)-1 and len(line) == 1:
		#			del self.lines[-1]
		#		else:
		#			print(i,line,column,"sentiment text column not correct")
		#			quit()

	def count_punct(self,column):
		if self.header:
			self.header.extend(["#excl_count","#quest_count"])
		for line in self.lines:
			try:
				text = line[column]
				if re.search("!",text):
					line.append(len(re.findall("!",text)))
				else:
					line.append(0)
				if re.search("\?",text):
					line.append(len(re.findall("\?",text)))
				else:
					line.append(0)
			except:
				print(line,"textcolumn incorrect, quitting")
				quit()

	def add_id(self,start_id = 0):
		for i,line in enumerate(self.lines):
			line.insert(0,str(i + start_id))

	# replace a specified field ([column]) in a line with a new string 
	#   ([replace]) if it matches one of the strings in [match] 
	#   (when [match] == [], any string is replaced)
	def replace_string(self,replace,c,m = []):
		for line in self.lines:
			if len(m) == 0 or line[c] in m:
				line[c] = replace
			else:
				for i,t in enumerate(line):
					if t in m:
						line[i] = replace

	def delete_string(self,blacklist,column):
		i = 0
		while i < len(self.lines):
			line = self.lines[i]
			black = False
			sequence = line[column].strip().split(" ")
			for w in sequence:
				for string in blacklist:
					if re.match(string,w,re.IGNORECASE):
						black = True
			if black:
				del self.lines[i]
			else:
				i+=1

	# for lines with temporal characteristics (especially describing an 
	#    event), add an amount of hours to the date and time, and either 
	#   append the new date and time to the line, or replace the current ones
	def add_time(self,value,datecolumn = 1,timecolumn = 2, add = "append", datetype = "eu"):
		for line in self.lines:
			date = line[datecolumn]
			time = line[timecolumn]
			dateparts = date.split("-")
			timeparts = time.split(":")
			if datetype == "eu":
				date_time = datetime.datetime(int(dateparts[2]),int(dateparts[1]),
					int(dateparts[0]),int(timeparts[0]),int(timeparts[1]),0)                
				new_date_time = date_time + datetime.timedelta(hours=value)        
			elif datetype == "vs":
				date_time = datetime.datetime(int(dateparts[0]),int(dateparts[1]),
					int(dateparts[2]),int(timeparts[0]),int(timeparts[1]),0)                
				new_date_time = date_time + datetime.timedelta(hours=2)                            
			if datetype == "eu":    
				new_date = str(new_date_time.day) + "-" + str(new_date_time.month) + "-" + \
					str(new_date_time.year)    
			elif datetype == "vs":
				new_date = str(new_date_time.year) + "-" + str(new_date_time.month) + "-" + \
					str(new_date_time.day)    
			new_time = str(new_date_time.hour) + ":" + str(new_date_time.minute)

			if add == "append":
				line.extend([new_date,new_time])
			elif add == "replace":
				line[datecolumn] = new_date
				line[timecolumn] = new_time
		
	def filter_string_end(self,key,column):

		def has_end(sequence):
			try: 
				if re.match(sequence[-1],key,re.IGNORECASE):
					return True          
				elif re.search("http://",sequence[-1]) or re.search("#",sequence[-1]):
					return has_end(sequence[:-1])
				else:
					return False
			except:
				return False 

		i = 0
		while i < len(self.lines):
			line = self.lines[i]
			text = line[column]
			seq = text.strip().split(" ")
			if has_end(seq):
				i+=1
			else:
				del self.lines[i]

	def extract_lines(self,keys,column):
		i = 0
		while i < len(self.lines):
			line = self.lines[i]
#                        print(line[column])
			text = line[column]
			if text in keys:
				print("YES",line[column]) 
				i += 1
			else:
				del self.lines[i]

	def convert_datetime(self):
		month = {"Jan":"01", "Feb":"02", "Mar":"03", "Apr":"04", "May":"05", "Jun":"06", "Jul":"07", "Aug":"08", "Sep":"09", "Oct":"10", "Nov":"11", "Dec":"12"}
		date_time = re.compile(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d+) (\d{2}:\d{2}:\d{2}) \+\d+ (\d{4})")
		i = 0
		while i < len(self.lines):
			line = self.lines[i]
			for j,column in enumerate(line):
				if date_time.search(column):
					dtsearch = date_time.search(column).groups()
					date = dtsearch[1] + "-" + month[dtsearch[0]] + "-" + dtsearch[3]
					time = dtsearch[2]
					self.lines[i][j] = date
					self.lines[i].insert(j+1,time)
					continue
			i += 1

	def sample(self,sample_size,sample_method,sample_type="down",return_sample=False):
		num_lines = len(self.lines)
		sample = []
		if sample_method == "steps":
			i = sample_size
			while i < len(self.lines):
				sample.append(self.lines[i])
				i += sample_size
			self.lines = sample
		else:
			if sample_type == "up":
				while sample_size > num_lines:
					sample.extend(range(num_lines))
					sample_size -= num_lines
			sample.extend(sorted(random.sample(range(num_lines), sample_size)))
			if return_sample:
				sample_out = [self.lines[i] for i in sample]
				return sample_out
			else:
				if sample_type=="down": 
					for offset, index in enumerate(sample):
					   index -= offset
					   del self.lines[index]
				elif sample_type=="up":
					for i in sample:
						self.lines.append(self.lines[i]) 
