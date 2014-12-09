#!/usr/bin/env python

import argparse
import gen_functions
import annotation_calcs
import xlwt

parser = argparse.ArgumentParser(description = "Program to read in annotations and output specified calculations and visualisations (default is only precision)")

parser.add_argument('-i', action = 'store', required = True, help = "the input file")
parser.add_argument('-f', action = 'store', default = "excel", help = "specify the format of the input file (default is excel)")
parser.add_argument('-o', action = 'store', help = "the output file")
parser.add_argument('--header', action = 'store_true', help = "specify if the exceltab(s) contain a header")
parser.add_argument('--ck', action = 'store_true', help = "specify to calculate cohen's kappa")
parser.add_argument('--ka', action = 'store_true', help = "specify to calculate krippendorff's alpha")
parser.add_argument('--fs', action = 'store_true', help = "specify to calculate mutual F-score")
#parser.add_argument('-c', action = 'store', nargs = '+', default = [0], help = "[OPTIONAL] if specific columns in a file need to be processed, specify them (one integer denotes every column from this point onwards)")
#parser.add_argument('-d', action='store_true', help = "choose for a prudent scoring (annotations with doubt are not taken as positive)")
parser.add_argument('-p', action='store', required = False, nargs = '+', help = "[OPTIONAL] for a precision-at-curve, specify the index in the given order of excel sheets (just 0 for txt) and the name of the output file")
parser.add_argument('-s', action = 'store', nargs = '+', required = False, help = "[EXCEL] specify indexes of the excel sheets to be processed")
parser.add_argument('-l', action = 'store_true', help = "specify if the number of annotations is not fixed")
parser.add_argument('-c', action = 'store_true', help = "specify if the value of annotations is not standard")
parser.add_argument('-r', action = 'store_true', help = "specify if the annotations are in an ordinal range")
args = parser.parse_args()

outfile = open(args.o,"w")

if args.c:
    c_dict = {"2":0,"1":1}

# retrieve annotation sets
if args.f == "txt":
    annotation_values = []
    infile = open(args.i)
    if args.c:
        for line in infile.readlines():
            annotation_values.append([c_dict[x] for x in line.strip().split("\t")])       
    else:
        for line in infile.readlines():
            # try:
            #     annotation_values.append([int(x) for x in line.strip().split("\t")])
            # except ValueError:
            annotation_values.append(line.strip().split("\t"))
    infile.close()
else:
    annotation_values = gen_functions.excel2lines(args.i,args.s,args.header,annotation=True)

annotation_values = [annotation_values]

# calculate and output scores
for i,sheet in enumerate(annotation_values):
    if args.r:
        wk = annotation_calcs.calculate_weighted_kappa(sheet)
        outfile.write("Weighted Kappa: " + str(wk[0]) + "\naverage: " + str(wk[1]) + "\nentries: " + str(wk[2]) + "\n\n")
    else:
        if args.p and int(args.p[0]) == i: 
            precision = annotation_calcs.calculate_precision(sheet,lax = args.l,plot = args.p[1])
        else:
            precision = annotation_calcs.calculate_precision(sheet,lax = args.l)
        for entry in precision:
            outfile.write("Precision " + str(entry[0]) + ":" + str(entry[1]) + "\n")
            print "Precision " + str(entry[0]) + ":",entry[1]
        outfile.write("\n")
        annotation_calcs.calculate_confusion_matrix(sheet)
        if args.ck:
            cohens_kappa = annotation_calcs.calculate_cohens_kappa(sheet)
            outfile.write("Cohen's Kappa: " + str(cohens_kappa) + "\n\n")
            print "Cohen's Kappa:",cohens_kappa
        if args.ka:
            krippendorff = annotation_calcs.calculate_krippendorffs_alpha(sheet)
            outfile.write("Krippendorff's Alpha: " + str(krippendorff) + "\n\n")
            print "Krippendorff's Alpha:",krippendorff
        if args.fs:
            mutual_fscore = annotation_calcs.calculate_mutual_fscore(sheet)
            outfile.write("Mutual F-score: " + str(mutual_fscore) + "\n")
            print "Mutual F-score:",mutual_fscore
