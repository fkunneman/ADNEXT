import chardet
import sys

rawdata = open(sys.argv[1]).read()
result = chardet.detect(rawdata)
charenc = result['encoding']
print charenc