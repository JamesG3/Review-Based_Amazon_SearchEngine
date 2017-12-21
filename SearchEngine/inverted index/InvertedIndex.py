import json
productFile = open("../../ML/dataset/prodcutData/productMeta.json", 'r')
pgTableFile = open("../data/pgTable.txt", 'w')

InvertIndex = {}		# term: [pgID1, pgID2, ...]
pgID = 0
progress = 0

for line in productFile:
	progress += 1
	
	l = json.loads(line)
	try:
		asin = l['asin']
		title = l['title']
	except:
		continue

	currTerm = ""
	for c in title:
		if not c.isalnum():
			if currTerm == "":
				continue

			currTerm = currTerm.lower()
			
			if currTerm not in InvertIndex:
				InvertIndex[currTerm] = []

			if InvertIndex[currTerm] and InvertIndex[currTerm][-1] == pgID:
				continue

			InvertIndex[currTerm].append(pgID)
			currTerm = ""
		
		else:
			currTerm += c

	if currTerm != "":
		currTerm = currTerm.lower()
		if currTerm not in InvertIndex:
			InvertIndex[currTerm] = []

		if not (InvertIndex[currTerm] and InvertIndex[currTerm][-1] == pgID):
			InvertIndex[currTerm].append(pgID)

	pgTableFile.write(','.join([str(pgID), asin, title.replace("\n", "")]))
	pgTableFile.write('\n')
	pgID += 1
	
	if progress%100000 == 0:
		print str(float(progress/100000)/94)

pgTableFile.close()
productFile.close()



print "writing InvertIndex..."
InvertIndexFile = open("../data/InvertIndex.txt",'w')
for key in InvertIndex:
	InvertIndexFile.write(str(key) + ':' + ','.join([str(i) for i in InvertIndex[key]]))
	InvertIndexFile.write('\n')
InvertIndexFile.close()

