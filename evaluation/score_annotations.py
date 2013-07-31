#!/usr/bin/env python

import argparse
import gen_functions
import annotation_calcs
import xlwt

parser = argparse.ArgumentParser(description = "Program to read in annotations and output specified calculations and visualisations (default is only precision)")

parser.add_argument('-i', action = 'store', required = True, help = "the input file")
parser.add_argument('-f', action = 'store', default = "excel", help = "specify the format of the input file (default is excel)")
#parser.add_argument('-o', action = 'store', required = False, help = "the output file (for the positive precision score and cohens kappa)")
parser.add_argument('--header', action = 'store_true', help = "specify if the exceltab(s) contain a header")
parser.add_argument('--ck', action = 'store_true', help = "specify to calculate cohen's kappa")
parser.add_argument('--ka', action = 'store_true', help = "specify to calculate krippendorff's alpha")
#parser.add_argument('-c', action = 'store', nargs = '+', default = [0], help = "[OPTIONAL] if specific columns in a file need to be processed, specify them (one integer denotes every column from this point onwards)")
#parser.add_argument('-d', action='store_true', help = "choose for a prudent scoring (annotations with doubt are not taken as positive)")
parser.add_argument('-p', action='store', required = False, nargs = '+', help = "[OPTIONAL] for a precision-at-curve, specify the index in the giveN order of excel sheets (just 0 for txt) and the name of the output file")
parser.add_argument('-s', action = 'store', nargs = '+', required = False, help = "[EXCEL] specify indexes of the excel sheets to be processed")

args = parser.parse_args()
# outfile = open(args.o,"w")
#precision_at = args.p

# retrieve annotation sets
annotation_values = gen_functions.excel2lines(args.i,args.s,args.header)

# calculate and output scores
for i,sheet in enumerate(annotation_values):
    if args.p and int(args.p[0]) == i: 
        precision = annotation_calcs.calculate_precision(sheet,args.p[1])
    else:
        precision = annotation_calcs.calculate_precision(sheet)
    for entry in precision:
        print "Precision " + str(entry[0]) + ":",entry[1]
    if args.ck:
        cohens_kappa = annotation_calcs.calculate_cohens_kappa(sheet)
        print "Cohen's Kappa:",cohens_kappa
    if args.ka:
        krippendorff = annotation_calcs.calculate_krippendorffs_alpha(sheet)
        print "Krippendorff's Alpha:",krippendorff
        
    
