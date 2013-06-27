#! /usr/bin/env python

import lineconverter
import codecs
import argparse

parser = argparse.ArgumentParser(description = "Program that can be used to change or make additions to any file with (possibly column-based) lines with a consistent format")
parser.add_argument('-i', action = 'store', required = True, help = "The input file.")  
parser.add_argument('-o', action = 'store', required = True, help = "The output file.")
parser.add_argument('-d', action = 'store', default = "\t", help = "For columned lines, specify the delimiter between columns (default = \'\\t\').")
parser.add_argument('-e', action = 'store', required = False, help = "An extra file name (needed for time deletion and the keepfile for extraction.")
parser.add_argument('-a', action = 'store', choices = ["add","replace","delete","extract","add_time"], help = "Choose the action to perform.")

args = parser.parse_args() 
infile = args.i
outfile = codecs.open(args.o,"w","utf-8")
delimiter = args.d
action = args.a
extra = args.e

lineconvert = lineconverter.Lineconverter(infile,delimiter)
if action == "add":
    extra = raw_input("Please give the string to add to each line...\n")
    place = raw_input("Please specify the column before which the string should be added as a new field (for addition behind the last column, give \'back\')...\n")
    lineconvert.add_string(extra,place)

elif action == "replace":
    def repl():
        replace = raw_input("Please give the replacing text...\n")
        typ = raw_input("fixed column or match? (c/m)\n")
        if typ == "c":
            column = int(raw_input("Please give the column to replace...\n"))
            match = raw_input("Please give the values that need to be replaced (seperate by a \',\' without spaces in the case of several matches, only typing ENTER will lead to a replacement of the given column in every line)...\n")
            matchlist = match.split(",")
            lineconvert.replace_string(replace,c = column,m = match) 
        else:
            match = raw_input("Please give the values that need to be replaced (seperate by a \',\' without spaces in the case of several matches, only typing ENTER will lead to a replacement of the given column in every line)...\n")
            matchlist = match.split(",")
            lineconvert.replace_string(replace,m = match) 
        again = raw_input("Do you want to replace another type of field? (y/n) \n")
        if again == "y":
            repl()
        elif again == "n":
            print "writing to file..."
        else:
            print "no \"y\" specified, writing to file..."
    
    repl()

elif action == "add_time":
    datecolumn = int(raw_input("Please specify the column in which the date is given...\n"))
    timecolumn = int(raw_input("Please specify the column in which the time is given...\n"))
    hours = int(raw_input("Please specify the amount of hours added...\n"))
    addition = raw_input("Is the new time added or is it replacing the given date and time? (give either \'append\' or \'replace\')...\n")
    datetype = raw_input("Is the date given in EU-style or VS-style? (give either \'eu\' or \'vs\')...\n")
    lineconvert.add_time(hours,datecolumn,timecolumn,addition,datetype)

elif action == "delete":
    string_deleted = raw_input("Specify the string to be deleted in each line\n")
    lineconvert.delete_string(string_deleted)    

elif action == "extract":
    size = int(raw_input("Please give the number of lines to extract...\n"))
    keep_out = codecs.open(extra,"w","utf-8")
    extracted_lines = lineconvert.extract_sample(size)
    for line in extracted_lines:
        outfile.write(line + "\n")
    outfile.close()
    for line in lineconvert.lines:
        keep_out.write(line + "\n")
    keep_out.close()
    
    exit()
    
for line in lineconvert.lines:
    outfile.write(line + "\n")

outfile.close()

