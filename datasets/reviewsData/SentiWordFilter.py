import json
# remove those terms which never appear in review data

# load lexicon
lexFile = open("../emotion/SentiWord/SentiWord.txt",'r')

lexicon = {}
for line in lexFile:
	if line[0] == "#":
		continue
	l = line.split("\t")
	lexicon[l[0]] = [0, l[1:]]		# [if exists in review, orig data]
lexFile.close()
print "lexicon is loaded."

counter = 0
for line in open("kcore_5.json", 'r'):
	counter += 1
	if counter%100000 == 0:
		print counter/100000
	if counter/100000 == 50:
		break

	review = json.loads(line)
	try:
		summary = review["summary"]
		review = review["reviewText"]
		for word in summary.split(" "):
			if word.lower() in lexicon:
				lexicon[word.lower()][0] = 1
		for word in review.split(" "):
			if word.lower() in lexicon:
				lexicon[word.lower()][0] = 1
	except:
		pass

lexFile.close()

newlexFile = open("../emotion/SentiWord/briefSentiWord.txt",'a')
newlexFile.write("# word\tAvgPosScore\tAvgNegScore\n")

for word in lexicon:
	if lexicon[word][0] == 1:
		newlexFile.write(word + '\t' + '\t'.join(lexicon[word][1]))

newlexFile.close()
	
