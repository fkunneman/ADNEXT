
import codecs
import re
import datetime
import random


# Class to convert the lines in a file in a number of ways and/or make a filtering of these.
class Lineconverter():

    # Give the file with lines and the standard delimiter between fields on a line (also if there is 
    #    only one field)
    def __init__(self,lines,delimiter):
        self.lines = []
        for line in lines:
            self.lines.append(line.strip())
        self.delimiter = delimiter

    # Add the same string to the back or front of each line (argument [place] can be 'front' or 'back')
    def add_string(self,string,place):
        newlines = []
        for line in self.lines:
            tokens = line.split(self.delimiter)
            if place == "back":
                tokens.append(string)
            else:
                tokens.insert(int(place),string)
            newline = self.delimiter.join(tokens)
            newlines.append(newline)
        
        self.lines = newlines

    # Add an id to the start of lines by enumeration
    def add_id(self):
        newlines = []

        for i,line in enumerate(self.lines):
            newline = str(i) + "\t" + line
            newlines.append(newline)

        self.lines = newlines

    # replace a specified field ([column]) in a line with a new string ([replace]) if it matches one of the 
    #    strings in [match] (when [match] == [], any string is replaced)
    def replace_string(self,replace,c,m = []):
        newlines = []
        for line in self.lines:
            tokens = line.split(self.delimiter)
            if type(c) == int:
		if len(m) == 0 or tokens[c] in m:
                    new_tokens = tokens
                    new_tokens[c] = replace
                    newline = self.delimiter.join(new_tokens)
                    newlines.append(newline)
                else:
                    newlines.append(line)
            else:
                for i,t in enumerate(tokens):
                    if t in m:
                        tokens[i] = replace
                newline = self.delimiter.join(tokens)
                newlines.append(newline)    
        self.lines = newlines
    
    def delete_string(self,string, column):
        newlines = []
        for line in self.lines:
            tokens = line.split(self.delimiter)
            if re.search(string,tokens[column]):
                tokens[column] = re.sub(string,"",tokens[column])
            newlines.append(self.delimiter.join(tokens))
        self.lines = newlines

    # for lines with temporal characteristics (especially describing an event), add an amount of hours to the date and time, and either append the new date and time to the line, or replace the current ones
    def add_time(self,value,datecolumn = 1,timecolumn = 2, add = "append", datetype = "eu"):
        newlines = []
        for line in self.lines:
            tokens = line.split(self.delimiter)
            date = tokens[datecolumn]
            time = tokens[timecolumn]
            dateparts = date.split("-")
            timeparts = time.split(":")
            if datetype == "eu":
                date_time = datetime.datetime(int(dateparts[2]),int(dateparts[1]),int(dateparts[0]),int(timeparts[0]),int(timeparts[1]),0)                
                new_date_time = date_time + datetime.timedelta(hours=value)        
            elif datetype == "vs":
                date_time = datetime.datetime(int(dateparts[0]),int(dateparts[1]),int(dateparts[2]),int(timeparts[0]),int(timeparts[1]),0)                
                new_date_time = date_time + datetime.timedelta(hours=2)                            
            if datetype == "eu":    
                new_date = str(new_date_time.day) + "-" + str(new_date_time.month) + "-" + str(new_date_time.year)    
            elif datetype == "vs":
                new_date = str(new_date_time.year) + "-" + str(new_date_time.month) + "-" + str(new_date_time.day)    
            new_time = str(new_date_time.hour) + ":" + str(new_date_time.minute)
        
            if add == "append":
                tokens.extend([new_date,new_time])
            elif add == "replace":
                tokens[datecolumn] = new_date
                tokens[timecolumn] = new_time
            new_line = self.delimiter.join(tokens)
            newlines.append(new_line)
        self.lines = newlines
        
    def extract_sample(self,size):
        print "Extracting sample..."
        keep_lines = []
        extracted = []
        num_lines = len(self.lines)
        sample = sorted(random.sample(range(num_lines), int(size)))      
      
        print "Writing..."
        for i in sample:
            extracted.append(self.lines[i])
            
        print "Deleting..."
        for offset, index in enumerate(sample):
            index -= offset
            del self.lines[index]
                                 
        return extracted
        
