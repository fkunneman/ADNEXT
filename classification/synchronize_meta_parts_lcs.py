import sys
import codecs

parts = codecs.open(sys.argv[1],"r","utf-8")
meta_sample = codecs.open(sys.argv[2],"r","utf-8")
new_parts = codecs.open(sys.argv[3],"w","utf-8")
new_label = sys.argv[4]

file_names = []
for line in meta_sample.readlines():
    tokens = line.split("\t")
    file_names.append(tokens[0])
meta_sample.close()

for line in parts.readlines():
    tokens = line.split(" ")
    file_name = tokens[0]
    if file_name in file_names:
        tokens[1] = new_label + "\n"
    new_parts.write(" ".join(tokens))
    
parts.close()
new_parts.close()
