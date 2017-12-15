import numpy as np
from numpy import genfromtxt
import math

def read_dataset(filePath,delimiter='\t'):
	return genfromtxt(filePath, delimiter=delimiter)

# 0.asin, 1.avgStar, 2.Summary_PosScore, 3.Summary_NegScore, 
# 4.SummAvgLen, 5.Review_PosScore, 6.Review_NegScore, 7.ReviewAvgLen, 8.reviewCount
def getClassN(dataset, N):
	C = []
	for item in dataset:
		if int(round(item[1])) == N:
			C.append(item[2:4]+item[5:7])
			# C.append(item[2:])
	return np.array(C)

def estimateGaussian(dataset):
	mu = np.mean(dataset, axis=0)
	sigma = np.cov(dataset, rowvar=0)
	return mu, sigma

def pdf(x, mu, sigma):
	x = np.array(x)
	S = np.linalg.det(sigma)

	res = (math.e ** ((-1.0/2) * np.dot(np.dot((x-mu),np.linalg.inv(sigma)), (x-mu).T))) / (2*math.pi * math.sqrt(abs(S)))
	return res

def test(filename, mu, sigma):
	rightCaseNum = 0.0
	totalCaseNum = 0.0
	testfile = open(filename, 'r')
	testData = read_dataset(filename)

	for item in testData:
		star = item[1]		# float
		totalCaseNum += 1
		PDF = []

		for i in xrange(5):
			PDF.append(pdf(item[2:4]+item[5:7], mu[i], sigma[i]))
			# PDF.append(pdf(item[2:], mu[i], sigma[i]))

		maxPDF = max(PDF)
		for i in xrange(5):
			if maxPDF == PDF[i]:
				if math.floor(star) <= (i+1) <= math.ceil(star):
					rightCaseNum += 1
				break
	print rightCaseNum/totalCaseNum

	testfile.close()

def predict(filename, mu, sigma):
	inputfile = open(filename, 'r')
	outputfile = open("../dataset/productScore/productScore_GA.csv", 'w')
	process = 0

	for line in inputfile:
		if line[0] == "#":
			continue

		process += 1
		if process % 10000 == 0:
			print process/10000

		item = line.split("\t")
		# preprocessing, to float
		for i in xrange(1,len(item)):
			item[i] = float(item[i])
		PDF = []
		for i in xrange(5):
			tmp = np.array(item[2:4]) + np.array(item[5:7])
			PDF.append(pdf(tmp, mu[i], sigma[i]))
			# PDF.append(pdf(item[2:], mu[i], sigma[i]))

		maxPDF = max(PDF)
		for i in xrange(5):
			if maxPDF == PDF[i]:
				# asin, predict star, real_avgStar ,reviewCount
				outputfile.write(item[0] + ',' + str(i+1) + ',' + str(item[1]) + ',' + str(int(item[-1])) + '\n')
				# print str(item[0]) + ',' + str(i+1)
				break

	outputfile.close()
	inputfile.close()


trainSet = read_dataset("../dataset/reviewsData/Reveiew_statistic_train.txt")
# 0.asin, 1.avgStar, 2.Summary_PosScore, 3.Summary_NegScore, 
# 4.SummAvgLen, 5.Review_PosScore, 6.Review_NegScore, 7.ReviewAvgLen, 8.reviewCount

mu = []
sigma = []

for i in xrange(5):
	mu_i, sigma_i = estimateGaussian(getClassN(trainSet, i+1))
	mu.append(mu_i)
	sigma.append(sigma_i)


# test("../dataset/reviewsData/Reveiew_statistic_test.txt", mu, sigma)
predict("../dataset/reviewsData/Reveiew_statistic.txt", mu, sigma)




