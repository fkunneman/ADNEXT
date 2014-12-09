
import os
import sys

classificationdir = sys.argv[1]
term = classificationdir.split("/")[-2]
print classificationdir,term

os.chdir(classificationdir)
os.system("rm " + term + "_richert.txt")
os.system("for x in *.json; do python ~/Software/ADNEXT/tweetprocessing/tweets_json_2_csv.py -i $x -o " + term + "_richert.txt; done")
os.system("python ~/Software/ADNEXT/convert_lines.py -i " + term + "_richert.txt -o " + term + "_richert.xls -a sentiment punct twitter -c 11 11 6 1 --excel 0 1 4 5 --header")
# os.system("python ~/Software/ADNEXT/convert_lines.py -i " + term + "_richer1.txt -o " + term + "_richer2.txt -a punct -c 11")
# os.system("python ~/Software/ADNEXT/convert_lines.py -i " + term + "_richer2.txt -o " + term + "_rich.xls -a twitter --excel")