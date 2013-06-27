
import sys

line = sys.argv[1]
		
tokens = line.split("\t")
text = tokens[6].strip()
user = tokens[5]
date = tokens[2]
time = tokens[3]	
dateparse = parse_date.search(date).groups()
timeparse = parse_time.search(time).groups()
dt = datetime.datetime(int(dateparse[0]),int(dateparse[1]),int(dateparse[2]),int(timeparse[0]),int(timeparse[1]),0)
id_long = tokens[0]

s_zeronum = 6-len(str(fileindex))
i = 0
s_filenum = str(fileindex) + ".txt"
while i < s_zeronum:
	s_filenum = "0" + s_filenum
	i += 1
filename = tks_tweets_file_name + "/" + prefix + s_filenum
outfilename = filesdir + filename
outfile = codecs.open(outfilename,"w","utf-8")

new_text = []
if ngrams:	
	tokens = text.split(" ")
	temp_lines = []	
	for token in tokens:
		token = re.sub("[\.,\?!;\'\":]","",token)
		if not token == "":
			temp_lines.append(token)	
			if token in weights:
				new_text.append("intensifier")
				print "intensifier: " + token + " " + outfilename
	temp_lines.append("<s>")
	temp_lines.insert(0,"<s>")
	for i,token in enumerate(temp_lines[1:len(temp_lines)-1]):
		unigram = "\"" + token + "\""
		new_text.append(unigram)
	for i,token in enumerate(temp_lines[:len(temp_lines)-1]):
		bigram = "\"" + token + "_" + temp_lines[i+1] + "\""
		new_text.append(bigram)
	for i,token in enumerate(temp_lines[:len(temp_lines)-2]):
		trigram = "\"" + token + "_" + temp_lines[i+1] + "_" + temp_lines[i+2] + "\""
		new_text.append(trigram)

	for tt in new_text:
		if not (filtword and re.search(filtword,tt)):		
			outfile.write(tt + "\n")

else:
	tokens = text.split(" ")
	for token in tokens:
		token = re.sub("[\.,\?!;\'\":]","",token)
		if token in weights:
			outfile.write("intensifier ")
	outfile.write(text)

if filttweet and re.search(filttweet,text):
	print text
	classfile.write(filename + " " + filttweetlabel + "\n")
else:
	classfile.write(filename + " " + label + "\n")
		metafile.write(filename + " " + str(id_long) + " " + str(dt) + " " + user + "\n")
		fileindex += 1
	except IndexError:
		print str(fileindex) + " IE"
		continue
