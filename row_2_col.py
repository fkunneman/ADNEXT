
import sys
from collections import defaultdict

infile = open(sys.argv[1])
outfile = open(sys.argv[2],"w")
delimiter = sys.argv[3]
concatenate = int(sys.argv[4])

newlines = defaultdict(list)
for line in infile.readlines():
    tokens = line.strip().split(delimiter)
    newtokens = []
    i = 0
    while i < len(tokens):
        newtokens.append(str(sum([int(x) for x in tokens[i:i+concatenate]]))) 
        i += concatenate
    for i,token in enumerate(newtokens):
        newlines[i].append(token)
infile.close()

for line in sorted(newlines.keys()):
    print line
    outfile.write(",".join(newlines[line]) + "\n")
outfile.close()