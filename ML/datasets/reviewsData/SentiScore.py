import json
# remove those terms which never appear in review data

# load lexicon
lexFile = open("./emotion/SentiWord/briefSentiWord50.txt",'r')

lexicon = {}
for line in lexFile:
	if line[0] == "#":
		continue
	l = line.split("\t")
	lexicon[l[0]] = [float(score) for score in l[1:]]		# word: [PosScore, NegScore]

lexFile.close()
print "lexicon is loaded."


outputfile = open("Reveiew_statistic.txt",'a')
outputfile.write("# asin\tavgStar\tSummary_PosScore\tSummary_NegScore\tSummAvgLen\tReview_PosScore\tReview_NegScore\tReviewAvgLen\treviewCount\n")
progress = 0
product = ""

for line in open("kcore_5.json", 'r'):
	progress += 1
	if progress%100000 == 0:
		print progress/100000

	l = json.loads(line)
	
	# try:
	if product == "":
		# intialize for next product
		product = l["asin"]
		reviewCount = 0
		totalStar = 0.0
		Review_totalLen = 0.0
		Summary_totalLen = 0.0
		Review_SentiCounter = 0.0001
		Summary_SentiCounter = 0.0001
		Review_PScore = 0.0
		Review_NScore = 0.0
		Summary_PScore = 0.0
		Summary_NScore = 0.0

	elif l["asin"] != product:
		PRODUCT = product
		AvgStar = str(totalStar/reviewCount)
		S_Pscore = str(Summary_PScore/Summary_SentiCounter)
		S_NScore = str(Summary_NScore/Summary_SentiCounter)
		S_AvgLen = str(Summary_totalLen/reviewCount)
		R_PScore = str(Review_PScore/Review_SentiCounter)
		R_NScore = str(Review_NScore/Review_SentiCounter)
		R_AvgLen = str(Review_totalLen/reviewCount)
		R_Count = str(reviewCount)
		outputfile.write("\t".join([PRODUCT, AvgStar, S_Pscore, S_NScore, S_AvgLen, R_PScore, R_NScore, R_AvgLen, R_Count]))
		outputfile.write("\n")
		# print "product: " + product
		# print "Summary_PScore: " + str(Summary_PScore/Summary_SentiCounter)
		# print "Summary_NScore: " + str(Summary_NScore/Summary_SentiCounter)
		# print "SumAvgLen: " + str(Summary_totalLen/reviewCount)
		# print "Review_PScore: " + str(Review_PScore/Review_SentiCounter)
		# print "Review_NScore: " + str(Review_NScore/Review_SentiCounter)
		# print "RevAvgLen: " + str(Review_totalLen/reviewCount)
		# print "AvgStar: " + str(totalStar/reviewCount)
		# print "reviewCount:" + str(reviewCount)
		# print "---------"

		# intialize for next product
		product = l["asin"]
		reviewCount = 0
		totalStar = 0.0
		Review_totalLen = 0.0
		Summary_totalLen = 0.0
		Review_SentiCounter = 0.0001
		Summary_SentiCounter = 0.0001
		Review_PScore = 0.0
		Review_NScore = 0.0
		Summary_PScore = 0.0
		Summary_NScore = 0.0

	summary = l["summary"]
	review = l["reviewText"]
	totalStar += float(l["overall"])
	
	reviewList = review.split(" ")
	summaryList = summary.split(" ")

	Review_totalLen += len(reviewList)
	Summary_totalLen += len(summaryList)
	reviewCount += 1

	for word in reviewList:
		if word and not word[-1].isalnum():
			word = word[:-1]
		if word.lower() in lexicon:
			Review_SentiCounter += 1
			Review_PScore += lexicon[word.lower()][0]
			Review_NScore += lexicon[word.lower()][1]

	for word in summaryList:
		if word and not word[-1].isalnum():
			word = word[:-1]
		if word.lower() in lexicon:
			Summary_SentiCounter += 1
			Summary_PScore += lexicon[word.lower()][0]
			Summary_NScore += lexicon[word.lower()][1]
	
	# except:
	# 	pass

outputfile.close()

# asin, avgStar, Review_PosScore, Review_NegScore, ReviewAvgLen, Summary_PosScore, Summary_NegScore, SummAvgLen, reviewCount
