#! /usr/bin/env python

from __future__ import division
import math
import xlrd
import re
import datetime
import codecs
from collections import defaultdict

def make_chunks(lines,nc=16,t):
    chunks=[]
    size = int(len(lines)/nc)
    i=0
    #remains = len(lines)
    for j in range(nc-1):
        if t == "numbers":
            chunks.append((i,i+size))
        else:
            chunks.append(lines[i:(i+size)])
        i += size
    if t == "numbers":
        chunks.append(i,len(lines))
    else:
        chunks.append(lines[i:])
    return chunks

def excel2lines(file_name,sheet_indexes,header = False,annotation=False,date=False):
    lines = []
    num_annotators = False
    workbook = xlrd.open_workbook(file_name)
    #collect sheets
    if sheet_indexes:
        sheets = []
        for index in sheet_indexes:
            sheets.append(workbook.sheet_by_index(int(index)))
    else:
        sheets = workbook.sheets()
    #for each sheet
    for sheet in sheets:
        sheetlines = []
        if header:
            first_row = 1
        else:
            first_row = 0
        last_row = sheet.nrows
        #iterate the lines
        for rownum in range(first_row,last_row):
            values = []
            #collect annotation values
            if annotation:
                for value in sheet.row_values(rownum):
                    try:
                        if int(value) in range(2):
                            values.append(value)
                    except ValueError:
                        continue
                if num_annotators:
                    if len(values) != num_annotators:
                        print "number of annotation values on line is not consistent; check the inputfile. Exiting..."
                        exit()
                else:
                    num_annotators = len(values)
            else:
                rowvals = sheet.row_values(rownum)
                if date:
                    try:
                        rowvals[date] = datetime.date(*xlrd.xldate_as_tuple(sheet.cell_value(rownum,date), workbook.datemode)[:3])
                    except:
                        continue
                values = [unicode(x) for x in rowvals]
            sheetlines.append(values)
        #each sheet is a list of lists
        lines.append(sheetlines)

    return lines
 

def excel2columns(file_name):
    word_cat = {}
    workbook = xlrd.open_workbook(file_name)
    sheet = workbook.sheet_by_index(0)
    for column in range(sheet.ncols):
        values = sheet.col_values(column)
        header = values[0]
        for i,value in enumerate(values[1:]):
            if value == '':
                break
            word_cat[value] = header
    return word_cat    

def calculate_cosine_similarity(vector1,vector2):
    if len(vector1) != len(vector2):
        print str(len(vector1)) + " " + str(len(vector2)) 
        print "Cosine distance: no equal number of dimensions, terminating process."

    mag1 = 0
    mag2 = 0
    dotpr = 0
    for i,term_1 in enumerate(vector1):
        term_2 = vector2[i]
#        print term_1,term_2
        m1 = int(term_1) * int(term_1)
        m2 = int(term_2) * int(term_2)
        dp = int(term_1) * int(term_2)
#        print m1,m2,dp
        mag1 += m1
        mag2 += m2
        dotpr += dp

    #print mag1
#    print "\nsum dotpr",sum(dotpr)
#    print "sum mag1",sum(mag1)
#    print "sum mag2",sum(mag2)
#    print "sqrt sum mag1",math.sqrt(sum(mag1))
#    print "sqrt sum mag2",math.sqrt(sum(mag2))
#    print "mag multiply",math.sqrt(sum(mag1)) * math.sqrt(sum(mag2))
    #sdp = sum(dotpr)
    #sqm1 = math.sqrt(sum(mag1))
    #sqm2 = math.sqrt(sum(mag2))
    cosine_similarity = dotpr / (int(math.sqrt(mag1))*int(math.sqrt(mag2)))

    return cosine_similarity

def has_endhashtag(sequence,hashtags):
#    print sequence
    print hashtags
    if len(sequence) == 0:
       return False
    if sequence[-1] == ".":
#        print "dot-false"
        return False
    for h in hashtags:
        try:
            #print sequence[-1],h,len(sequence[-1].strip()),len(h.strip())
            if re.match(sequence[-1],h,re.IGNORECASE):
                #print "true"
                return True
        except:
#            print "charfalse"
            return False
    if re.search("URL",sequence[-1]) or re.search("#",sequence[-1]):
#        print "markerproceed"
        has_endhashtag(sequence[:-1],hashtags)
    else:
#        print "empty stop"
        return False

def read_lcs_files(partsfile,filesdir):
    #generate list of filenames
    parts = open(partsfile)
    filenames = []
    for line in parts.readlines():
        filenames.append(filesdir + line.split(" ")[0])
    parts.close()
    #generate list of wordsequences from file content
    featuresets = []
    for filename in filenames:
        txtfile = codecs.open(filename,"r","utf-8")
        features = []
        for line in txtfile.readlines():
            features.append(line.strip())
        featuresets.append(features)
        txtfile.close()
    return featuresets

def return_standard_deviation(v):
    mean = sum(v) / len(v)
    return round(math.sqrt(sum([((e-mean)*(e-mean)) for e in v]) / len(v)),2)
    

