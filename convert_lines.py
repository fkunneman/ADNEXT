#! /usr/bin/env python

import lineconverter
import codecs
import argparse
import gen_functions
import re
import time_functions
from xlwt import *

parser = argparse.ArgumentParser(description = "Program that can be used to change or make "
    "additions to any file with (possibly column-based) lines with a consistent format")
parser.add_argument('-i', action = 'store', required = True, help = "The input file.")  
parser.add_argument('-o', action = 'store', required = True, help = "The output file.")
parser.add_argument('-d', action = 'store', default = "\t", 
    help = "For columned lines, specify the delimiter between columns (default = \'\\t\').")
parser.add_argument('-a', action = 'store', required = False, 
    choices = ["add","replace","convert_float","delete","delete_filematch","extract","add_time",
    "add_id","filter","twitter", "sentiment", "punct"], nargs = '+', 
    help = "Choose the actions to perform.")
parser.add_argument('-s', action = 'store', required = False, 
    help = "give a string as argument for add, replace, delete, filter or extract")
parser.add_argument('-c', action = 'store', required = False, nargs='+', type=int, 
    help = "give column numbers as argument for add, convert_float, replace, delete, sentiment, "
    "punct or extract (add is done before the column, no column means behind the last one, no "
    "column for replace means every column will be matches). provide column numbers for each "
    "\'action\' argument it applies to.")
parser.add_argument('--sample', action = 'store', required = False, nargs='+', 
    help = "sample lines, first specify the number of lines to sample, then specify the sample "
    "method (steps or random)")
parser.add_argument('--replace', action = 'store', required = False, nargs='+', 
    help = "[REPLACE] specify the strings to match for replacement.")
parser.add_argument('--filematch', action = 'store', required = False, nargs='+', 
    help = "[DELETE_FILEMATCH] give respectively the file and the column within the file to match")
parser.add_argument('--excel', action = 'store', type = int, nargs = '*', 
    help = "Output lines in excel format")
parser.add_argument('--sheets', action = 'store', nargs='+', type = int, default = [0], 
    help = "for multiple excel input sheets, specify the indexes")
parser.add_argument('--header', action='store_true', 
    help = "specify if file has header")
parser.add_argument('--append', action='store_true', 
    help = "choose to append output to an existing file (rather than a new file)")
parser.add_argument('--dt', action='store_true', 
    help = "choose to convert twitter date-time column)")

args = parser.parse_args() 

delimiter = args.d
if args.i[-3:] == "xls": 
    sheets = gen_functions.excel2lines(args.i,args.sheets)
    print "num_sheets",len(sheets)
    lines = []
    for sheet in sheets:
        for line in sheet:
            for i in range(len(line)):
                line[i] = re.sub("\n","",line[i])
            lines.append(line)
    print "num_lines",len(lines)
else:
    infile = codecs.open(args.i,"r","utf-8")
    lines_raw = infile.readlines()
    infile.close()
    lines = [x.strip().split(delimiter) for x in lines_raw]
    linelen = len(lines[0])
    if linelen > 1:
        i = 0
        while i < len(lines):
            line = lines[i]
            if len(line) == 1:
                lines[i-1][-1] = lines[i-1][-1] + " " + line[0]
                del lines[i]
            else:
                i+=1
    print "num_lines",len(lines)

actions = args.a
lineconvert = lineconverter.Lineconverter(lines,args.header)

if actions:
    if "add" in actions:
        if args.c:
            lineconvert.add_string(args.s,args.c.pop(0))
        else:
            place = "back"
        

    if "replace" in actions:
        if args.c:
            if args.replace:
                lineconvert.replace_string(args.s,c = args.c.pop(0),m = args.replace)
            else:
                lineconvert.replace_string(args.s,c = args.c.pop(0))
        else:
            lineconvert.replace_string(args.s,args.replace)

    if "add_time" in actions:
        datecolumn = int(raw_input("Please specify the column in which the date is given...\n"))
        timecolumn = int(raw_input("Please specify the column in which the time is given...\n"))
        hours = int(raw_input("Please specify the amount of hours added...\n"))
        addition = raw_input("Is the new time added or is it replacing the given date and time? "
            "(give either \'append\' or \'replace\')...\n")
        datetype = raw_input("Is the date given in EU-style or VS-style? "
            "(give either \'eu\' or \'vs\')...\n")
        lineconvert.add_time(hours,datecolumn,timecolumn,addition,datetype)

    if "add_id" in actions:
        if args.c:
            lineconvert.add_id(start_id = args.c.pop(0))
        else:
            lineconvert.add_id()

    if "delete" in actions:
        print "num lines before delete:",len(lineconvert.lines)
        lineconvert.delete_string([args.s], args.c.pop(0))
        print "num lines after delete",len(lineconvert.lines)

    if "delete_filematch" in actions:
        f = args.filematch[0]
        matchlist = []
        if f[-3:] == "xls": 
            mlines = gen_functions.excel2lines(f,[0])[0]
            for mline in mlines:
                match = re.sub("\n","",mline[int(args.filematch[1])])
                matchlist.append(match)
        else:
            matchfile = codecs.open(args.filematch[0],"r","utf-8")
            matchlines = infile.readlines()
            infile.close()
            for matchline in matchlines:
                tokens = matchline.strip().split(args.d)
                match = re.sub("\n","",tokens[int(args.filematch[1])])
                matchlist.append(match)
        print "num lines before delete:",len(lineconvert.lines)
        lineconvert.delete_string(matchlist, args.c)
        print "num lines after delete",len(lineconvert.lines)

    if "filter" in actions:
        lineconvert.filter_string_end(args.s,args.c.pop(0))

    if "extract" in actions:
        extractfile = codecs.open(args.s,"r","utf-8")
        matchstrings = [l.strip() for l in extractfile.readlines()]
        extractfile.close()
        #print(args.c)
        lineconvert.extract_lines(matchstrings,args.c.pop(0))
    if "sentiment" in actions:
        lineconvert.add_sentiment(args.c.pop(0))

    if "punct" in actions:
        lineconvert.count_punct(args.c.pop(0))

    if "twitter" in actions:
        lineconvert.add_twitter_url(args.c[0],args.c[1])

if args.dt:
    lineconvert.convert_datetime()

if args.sample:
    if len(args.sample) > 1 and args.sample[1] == "steps":
        sample_m = "steps"
        size = int(args.extract[0])
    else:
        sample_m = "random"
        size = len(lineconvert.lines) - int(args.sample[0]) 
    lineconvert.sample(size,sample_method = sample_m)
    
if args.excel:
    if len(lineconvert.lines) > 65535:
        num_chunks = int(len(lineconvert.lines) / 65534) + 1
        chunks = gen_functions.make_chunks(lineconvert.lines,nc = num_chunks)
    else:
        chunks = [lineconvert.lines]
    outname = args.o.split("/")[-1].split(".")[0]
    book = Workbook()
    algn1 = Alignment()
    algn1.wrap = 1
    style = XFStyle()
    style.alignment = algn1
    for x,chunk in enumerate(chunks):
        tabname = outname + "_" + str(x)
        if len(tabname) <= 25:
            tab = book.add_sheet(tabname)
        else:
            tab = book.add_sheet(outname[:23] + "_" + str(x))
        if args.header and x == 0:
            for j,col in enumerate(lineconvert.header):
                tab.write(0,j,col,style)
        for i,line in enumerate(chunk):
            if args.header and x == 0:
                i += 1
            for j,col in enumerate(line):
                if j in args.excel:
                    style.num_format_str = "general"
                    tab.write(i,j,col,style)
                else:
                    if re.search("LINEBREAK",col):
                        col = col.replace("LINEBREAK","\n")
                        style.alignment.wrap = 1
                        tab.write(i,j,col,style)
                    else:
                        try:
                            col = round(float(col),2)
                            style.num_format_str = "0.00"
                            tab.write(i,j,col,style)
                        except:
                            try:
                                col = int(col)
                                style.num_format_str = "0"
                                tab.write(i,j,col,style)
                            except:
                                try:
                                    col = time_functions.return_datetime(col)
                                    style.num_format_str = "dd-mm-yy"
                                    tab.write(i,j,col,style)
                                except:
                                    if re.match(r"\d{2}:\d{2}:\d{2}",col):
                                        style.num_format_str = 'hh:mm:ss'
                                        tab.write(i,j,col,style)
                                    else:
                                        if re.search("https://twitter.com",col):
                                            ucol = 'HYPERLINK(\"' + col + "\"; \"" + col + "\")"
                                            tab.write(i,j, Formula(ucol))
                                        else:
                                            style.num_format_str = "general"
                                            tab.write(i,j,col,style)

    book.save(args.o)
        
else:
    if args.append:
        outfile = codecs.open(args.o,"a","utf-8")
    else:
        outfile = codecs.open(args.o,"w","utf-8")
    for line in lineconvert.lines:
        outfile.write(delimiter.join(line) + "\n")
    outfile.close()
