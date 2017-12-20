import json
import math

# load adj and adv lexicon
lexicon = {}
lexiconSize = 0
lexiconFile = open("../dataset/emotion/NRC/NRClexicon2.0.txt",'r')
for line in lexiconFile:
	lexicon[line.split(",")[0]] = lexiconSize
	lexiconSize += 1
lexiconFile.close()


# get matrix file
file = open("../dataset/reviewsData/kcore_5.json",'r')
sizeCounter = 0
sizeLimit = 10000			# larger than 8000 has better performance

# statistic lists, collect data
countClass = [0.0 for i in xrange(5)]		# counter for star 1 to 5
countX1 = [0.0 for i in xrange(lexiconSize)]		# for class = 1, count +
countX2 = [0.0 for i in xrange(lexiconSize)]		# for class = 2
countX3 = [0.0 for i in xrange(lexiconSize)]		# for class = 3
countX4 = [0.0 for i in xrange(lexiconSize)]		# for class = 4
countX5 = [0.0 for i in xrange(lexiconSize)]		# for class = 5
countX = [countX1, countX2, countX3, countX4, countX5]

print "collecting data..."

for line in file:
	l = json.loads(line)
	star = int(l["overall"])
	words = (l["reviewText"] + " " + l["summary"]).split(" ")
	flag = 0

	# if len(words) < 6:			# length of review
	# 	continue
	
	# preprocessing review -> lowercase
	for i in xrange(len(words)):
		if words[i] and not words[i][-1].isalnum():
			words[i] = words[i][:-1]
		words[i] = words[i].lower()
	
	for word in set(words):
		# if word and not word[-1].isalnum():
		# 	word = word[:-1]

		if word in lexicon:
			flag = 1
			index = lexicon[word.lower()]
			countX[star-1][index] += 1
		
	if flag == 0:		# if no word in lexicon, skip this review
		continue

	countClass[star-1] += 1
	sizeCounter += 1
	if sizeCounter%sizeLimit == 0:
		break

file.close()


# calculate probablities
PC = [count/sizeLimit for count in countClass]
PxC1 = [[0.0]*2 for i in xrange(lexiconSize)]			# [0, 1]
PxC2 = [[0.0]*2 for i in xrange(lexiconSize)]
PxC3 = [[0.0]*2 for i in xrange(lexiconSize)]
PxC4 = [[0.0]*2 for i in xrange(lexiconSize)]
PxC5 = [[0.0]*2 for i in xrange(lexiconSize)]
PxC = [PxC1, PxC2, PxC3, PxC4, PxC5]			# likelihood

for i in xrange(lexiconSize):
	for j in xrange(5):
		PxC[j][i][1] = (countX[j][i] + 0.01) / (countClass[j] + 0.02)	# appear likelihood
		PxC[j][i][0] = 1 - PxC[j][i][1]

# test on training data
def testFunction(filename):
	print "start testing..."

	testFile = open(filename, 'r')
	test_sizeCounter = 0
	test_sizeLimit = 3000		# test sample size
	test_startFrom = 10000
	test_endPoint = test_startFrom + test_sizeLimit

	def calculate(PC, PxC):
		S = 0.0
		for item in PxC:
			S += math.log(item)

		return S*0.65 + math.log(PC)	# maybe 0.65 has better performance

	totalCaseNum = 0.0
	rightCaseNum = 0.0

	for line in testFile:
		if test_sizeCounter < test_startFrom:
			test_sizeCounter += 1
			continue

		tmpPxC1 = [0.0 for i in xrange(lexiconSize)]
		tmpPxC2 = [0.0 for i in xrange(lexiconSize)]
		tmpPxC3 = [0.0 for i in xrange(lexiconSize)]
		tmpPxC4 = [0.0 for i in xrange(lexiconSize)]
		tmpPxC5 = [0.0 for i in xrange(lexiconSize)]
		tmpPxC = [tmpPxC1, tmpPxC2, tmpPxC3, tmpPxC4, tmpPxC5]

		TryC1 = 0.0			
		TryC2 = 0.0	
		TryC3 = 0.0
		TryC4 = 0.0
		TryC5 = 0.0
		TryC = [TryC1, TryC2, TryC3, TryC4, TryC5]

		l = json.loads(line)
		flag = 0

		star = int(l["overall"])
		words = (l["reviewText"] + " " + l["summary"]).split(" ")
		wordDic = {}	# store the terms from [words] which are in lexicon

		if len(words) < 20:		# length of review (16-20 is acceptable)
			continue

		for i in xrange(len(words)):
			if words[i] and not words[i][-1].isalnum():
				words[i] = words[i][:-1]
			if words[i].lower() in lexicon:
				flag = 1
				if words[i].lower() not in wordDic:
					wordDic[words[i].lower()] = 1
		if flag == 0:		# if no word in lexicon, skip this review
			continue
		
		totalCaseNum += 1

		for word in lexicon:		# traverse all terms in lexicon
			index = lexicon[word]
			if word in wordDic:
				j = 1		# appear
			else:
				j = 0		# not appear
			
			for k in xrange(5):
				tmpPxC[k][index] = PxC[k][index][j]

		for i in xrange(5):
			TryC[i] = calculate(PC[i], tmpPxC[i])

		MaxC = max(TryC)
		for i in xrange(5):
			if TryC[i] == MaxC:
				if abs(i+1 - star) <= 1:		# soft margin: 3, 4, 5 are all considered right for label 4
				# if i+1 == star:				# hard margin
					rightCaseNum += 1
			
		test_sizeCounter += 1
		if test_sizeCounter == test_endPoint:
			break

	testFile.close()

	print rightCaseNum/totalCaseNum


def predict():
	print "start prediction..."

	inputFile = open("../dataset/reviewsData/kcore_5.json", 'r')			# test on musical dataset
	outputFile = open("../dataset/productScore/productScore_NB.csv", 'w')
	
	def calculate(PC, PxC):
		S = 0.0
		for item in PxC:
			S += math.log(item)

		return S*0.65 + math.log(PC)	# maybe 0.65 has better performance

	progress = 0
	product = ""

	for line in inputFile:
		tmpPxC1 = [0.0 for i in xrange(lexiconSize)]
		tmpPxC2 = [0.0 for i in xrange(lexiconSize)]
		tmpPxC3 = [0.0 for i in xrange(lexiconSize)]
		tmpPxC4 = [0.0 for i in xrange(lexiconSize)]
		tmpPxC5 = [0.0 for i in xrange(lexiconSize)]
		tmpPxC = [tmpPxC1, tmpPxC2, tmpPxC3, tmpPxC4, tmpPxC5]

		TryC1 = 0.0			
		TryC2 = 0.0	
		TryC3 = 0.0
		TryC4 = 0.0
		TryC5 = 0.0
		TryC = [TryC1, TryC2, TryC3, TryC4, TryC5]

		progress += 1
		if progress%10000 == 0:
			print progress/10000
		
		try:
			l = json.loads(line)
			flag = 0

			if product == "":
				product = l["asin"]
				totalStar = 0.0
				reviewCount = 0
			elif l["asin"] != product:
				if reviewCount == 0:		# for other languages, reviewCount might be 0
					AvgStar = 0
					outputFile.write(product + ',' + str(AvgStar) + ',' + str(reviewCount) + '\n')
					product = l["asin"]
					totalStar = 0.0
					reviewCount = 0

				else:
					AvgStar = totalStar/reviewCount
					outputFile.write(product + ',' + str(AvgStar) + ',' + str(reviewCount) + '\n')
					product = l["asin"]
					totalStar = 0.0
					reviewCount = 0

			words = (l["reviewText"] + " " + l["summary"]).split(" ")
			wordDic = {}	# store the terms from [words] which are in lexicon

			# if len(words) < 20:		# length of review (16-20 is acceptable)
			# 	continue

			for i in xrange(len(words)):
				if words[i] and not words[i][-1].isalnum():
					words[i] = words[i][:-1]
				if words[i].lower() in lexicon:
					flag = 1
					if words[i].lower() not in wordDic:
						wordDic[words[i].lower()] = 1
			if flag == 0:		# if no word in lexicon, skip this review
				continue

			reviewCount += 1

			for word in lexicon:		# traverse all terms in lexicon
				index = lexicon[word]
				if word in wordDic:
					j = 1		# appear
				else:
					j = 0		# not appear
				for k in xrange(5):
					tmpPxC[k][index] = PxC[k][index][j]
			for i in xrange(5):
				TryC[i] = calculate(PC[i], tmpPxC[i])

			MaxC = max(TryC)
			for i in xrange(5):
				if TryC[i] == MaxC:
					totalStar += (i+1)
					break
		except Exception as e:
			print e
			pass
		

	inputFile.close()
	outputFile.close()




# testFunction("../dataset/reviewsData/kcore_5.json")
predict()













