file = open("SentiWordNet_3.0.0_20130122.txt", 'r')
outputfile = open("SentiWord.txt",'a')
dic = {}

counter = 0
for line in file:
	if line[0] == "#":
		continue
	counter += 1
	l = line.split("\t")[1:5]
	
	wordlist = [word[:-2] for word in l[-1].split(" ")]
	

	if l[1] == l[2] == '0':
		continue

	print l
	print wordlist
	for word in wordlist:
		if word in dic:
			dic[word][0].append(float(l[1]))	# PosScore
			dic[word][1].append(float(l[2]))	# NegScore
		else:
			if word.isalnum():
				dic[word] = [[float(l[1])],[float(l[2])]]


	# if counter == 100:
	# 	break
print dic
outputfile.write("# word\tAvgPosScore\tAvgNegScore\n")
for word in dic:
	outputfile.write(word + "\t" + str(sum(dic[word][0])/len(dic[word][0])) + "\t" + str(sum(dic[word][1])/len(dic[word][1])) + "\n")

file.close()
outputfile.close()