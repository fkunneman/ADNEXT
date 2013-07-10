#! /usr/bin/env python

import lineconverter
import codecs
import argparse
import gen_functions
from xlwt import *

parser = argparse.ArgumentParser(description = "Program that can be used to change or make additions to any file with (possibly column-based) lines with a consistent format")
parser.add_argument('-i', action = 'store', required = True, help = "The input file.")  
parser.add_argument('-o', action = 'store', required = True, help = "The output file.")
parser.add_argument('-d', action = 'store', default = "\t", help = "For columned lines, specify the delimiter between columns (default = \'\\t\').")
parser.add_argument('-e', action = 'store', required = False, help = "An extra file name (needed for time deletion and the keepfile for extraction).")
parser.add_argument('-a', action = 'store', required = False, choices = ["add","replace","delete","extract","add_time"], help = "Choose the action to perform.")
parser.add_argument('-s', action = 'store', required = False, help = "give a string as argument for add, replace or delete")
parser.add_argument('-c', action = 'store', required = False, help = "give the column as argument for add, replace (add is done before the column, no column means behind the last one, no column for replace means every column will be matches).")
parser.add_argument('--extract', action = 'store', required = False, help = "[EXTRACT] specify the number of lines to extract")
parser.add_argument('--replace', action = 'store', required = False, nargs='+', help = "[REPLACE] specify the strings to match for replacement.")
parser.add_argument('--excel', action = 'store_true', help = "Output lines in excel format")

args = parser.parse_args() 
infile = args.i
delimiter = args.d
action = args.a
extra = args.e

lineconvert = lineconverter.Lineconverter(infile,delimiter)
if action == "add":
    if args.c:
        place = int(args.c)
    else:
        place = "back"
    lineconvert.add_string(args.s,place)

elif action == "replace":
    if args.c:
        column = int(c)
        lineconvert.replace_string(args.s,c = column,m = args.replace) 
    else:
        lineconvert.replace_string(args.s,args.replace)

elif action == "add_time":
    datecolumn = int(raw_input("Please specify the column in which the date is given...\n"))
    timecolumn = int(raw_input("Please specify the column in which the time is given...\n"))
    hours = int(raw_input("Please specify the amount of hours added...\n"))
    addition = raw_input("Is the new time added or is it replacing the given date and time? (give either \'append\' or \'replace\')...\n")
    datetype = raw_input("Is the date given in EU-style or VS-style? (give either \'eu\' or \'vs\')...\n")
    lineconvert.add_time(hours,datecolumn,timecolumn,addition,datetype)

elif action == "delete":
    lineconvert.delete_string(args.s)

elif action == "extract":
    size = int(args.extract)
    extracted_lines = lineconvert.extract_sample(size)
    for line in extracted_lines:
        outfile.write(line + "\n")
    outfile.close()
    if args.e:
        keep_out = codecs.open(args.e,"w","utf-8")
        for line in lineconvert.lines:
            keep_out.write(line + "\n")
        keep_out.close()
    exit()
    
if args.excel:
    if len(lineconvert.lines) > 65535:
        chunk_len = 65534
        chunks = gen_functions.make_chunks(lineconvert.lines,chunk_len)
    else:
        chunks = [lineconvert.lines]
    outname = args.o.split("/")[-1].split(".")[0]
    book = Workbook()
    for x,chunk in enumerate(chunks):
        tab = book.add_sheet(outname + "_" + str(x))
        for i,line in enumerate(chunk):
            columns = line.split(args.d)
            for j,col in enumerate(columns):
                tab.write(i,j,col)
    book.save(args.o)
        
else:
    outfile = codecs.open(args.o,"w","utf-8")
    for line in lineconvert.lines:
        outfile.write(line + "\n")
    outfile.close()
