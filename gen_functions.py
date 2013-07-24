#! /usr/bin/env python

import xlrd

def make_chunks(lines,size):
    chunks=[]
    i=0
    remains = len(lines)
    while remains > size:
        chunks.append(lines[i:(i+size)])
        i += size
        remains = len(lines[i:])
    chunks.append(lines[i:])
    return chunks

def excel2lines(file_name,sheet_indexes,header = False):
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
            for value in sheet.row_values(rownum):
                try:
                    if int(value) in range(2):
                        values.append(int(value))
                except ValueError:
                    continue
            if num_annotators:
                if len(values) != num_annotators:
                    print "number of annotation values on line is not consistent; check the inputfile. Exiting..."
                    exit()
            else:
                num_annotators = len(values)
            sheetlines.append(values)
        #each sheet is a list of lists
        lines.append(sheetlines)

    return lines
 