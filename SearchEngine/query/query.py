import struct
import math
import time
import S9Compressor as S9


lexicon = {}				# term: head, tail, # of docs
pagetable = {}				# docid: position for url line

iiLists = []				# [all data for term1], [all data for term2]
termList = []				# term1, term2, ..
lexiconList = []			# [term1's lexicon], [term2's],...

metaDataList = []			# [[t1's block1 meta], [t1's block2 meta]], [[t2's],[t2's]]
productScore = {}

iiCache = {}				# store the current decompressed chunk, [[current SUM, cursor], [the decompressed chunk]]

lp = []						# [block#, chunk#, iiPosition], [block#, chunk#, iiPosition]


def lexPrepare():
	print "loading lexicon..."
	lexFile = open('../data/Lexicon.txt','r')
	for line in lexFile:
		lexInfo = line.split(':')
		lexicon[lexInfo[0]] = [int(item) for item in lexInfo[1].split(',')]

	lexFile.close()
	return

def scorePrepare():
	print 'loading score..'
	scoreFile = open("../../ML/dataset/productScore/productScore.csv")
	# asin, NBscore(float), GAscore(integer), orig average score, review count
	for line in scoreFile:
		l = line.split(",")
		if l[1] == '':
			l[1] = -1
		productScore[l[0]] = [float(x) for x in l[1:]]

	scoreFile.close()
	return


def pagetbPrepare():		# only save the docid and it's position, using seek later. saving memory, fast.
	print "loading pagetable..."
	pageFile = open('../data/pgTable.txt', 'r')

	position = 0
	for line in pageFile:
		l = line.split(',')
		pageId = int(l[0])
		pagetable[pageId] = [l[1], position]			# asin, position in pagetable
		position += len(line)
	pageFile.close()
	return

def checkValid(queryList):		# check whether the input query is valid, if valid, return the filtered termlist
	cleanTerm = []
	for term in queryList:
		if term == "":
			continue
		if not str.isalnum(term):
			return 0
		else:
			cleanTerm.append(term.lower())
	return list(set(cleanTerm))			# keep one term if repeat

def sort(termList, lexiconList, sortHelper):	# sort(asc) termList and lexiconList base on the size of inverted index, prepare for DAAT
	sortHelper.sort()
	newTermList = []
	newLexiconList = []

	for pair in sortHelper:
		newTermList.append(termList[pair[-1]])
		newLexiconList.append(lexiconList[pair[-1]])
	return newTermList, newLexiconList

def openList(head, tail):			# load the compressed inverted index list into iiLists
	global iiLists
	iiFile = open("../data/BinInvertIndex.txt",'r')
	iiFile.seek(head*4,0)
	tmpii = []						# might contain several blocks
	counter = tail - head
	for number in iter(lambda: iiFile.read(4)[::-1], ''):
		if counter == 0:
			break
		counter -= 1
		integer_value = struct.unpack('<I', number)[0]
		tmpii.append(integer_value)
	
	iiLists.append(tmpii)
	return


def closeList():
	del iiLists[:]
	del termList[:]
	del lexiconList[:]
	del lp[:]
	del metaDataList[:]
	iiCache.clear()
	return

def getMetadata():				# load metadata for all blocks of each term
	for i in xrange(len(termList)):
		L = lexiconList[i][1] - lexiconList[i][0]
		currL = 0				# initialize as 1, for the size of metadata in 1st block
		headers = []

		while currL != L:
			currentHeader = []
			headSize = iiLists[i][currL]
			currL += 1
			currentHeader = iiLists[i][currL : currL+headSize*2]
			headers.append(currentHeader)

			for j in xrange(1, headSize*2,2):
				currL += currentHeader[j]
			
			currL += headSize*2
		metaDataList.append(headers)		# store headers for each term into a global list

	return

# decompress, cache,
def getnexGEQ(i, chunksize, iiPosition, did, iscached):
	global iiLists
	chunk = iiLists[i][iiPosition: iiPosition+chunksize]
	
	if iscached == 0:			# if not in the current cache
								# init or replace the cache
		iiCache[i] = [[0, 0],S9.decoder(chunk)]	# [SUM, cursor], chunk
		# print iiCache

	SUM, cursor = iiCache[i][0][0], iiCache[i][0][1]
	for j in xrange(cursor, len(iiCache[i][1])):
		if SUM >= did:
			iiCache[i][0][0], iiCache[i][0][1] = SUM, j
			# print SUM
			return SUM
		else:
			SUM += iiCache[i][1][j]
			# print SUM


def nextGEQ(i, did):		# check the next docid >= did, in inverted index for term i
	global lp

	headers = metaDataList[i]	# get headers for term i
	if len(lp) == i:		# need add a new listpointer, initialize
		iiPosition = 0
		for j in xrange(len(headers)):		# read each block's header in headers
			iiPosition += 1					# for the metadata size
			header = headers[j]
			iiPosition += len(header)		# for header size in current block

			for k in xrange(0, len(header), 2):
				if header[k] >= did:
					lp.append([j, k/2, iiPosition])	# record current position (block#, chunk#, iiPosition)
					return getnexGEQ(i, header[k+1], iiPosition , did, 0)		# return the docid >= did
				else:
					iiPosition += header[k+1]	# add the size of the skipped chunk
		return				# if this term doesn't have larger docid, return None
		

	else:
		currentlp = lp[i]	# read lp, locate the last read information
		iiPosition = currentlp[-1]
		blockPos = currentlp[0]
		chunkPos = currentlp[1]
		if headers[blockPos][chunkPos*2] >= did:	# same chunk in the cache
				# actually chunksize and iiPosition are not used in this situation
			chunksize = headers[blockPos][chunkPos*2+1]
			# print chunksize
			return getnexGEQ(i, chunksize, iiPosition , did, 1)	# read the cached list directly

		for j in xrange(blockPos, len(headers)):		# not same chunk in the cache
			header = headers[j]
			if j != blockPos:				# add header size for each block
				iiPosition += 1
				iiPosition += len(header)

			for k in xrange((chunkPos+1)*2, len(header),2):		# find from next chunk
				if header[k] >= did:
					lp[i] = [j, k/2, iiPosition]
					return getnexGEQ(i, header[k+1], iiPosition, did, 0)
				else:
					iiPosition += header[k+1]

		return			# if cannot find, return None


def PgScore(did):				# return ML based score
	def score(score, reviewNum):
		return score * (1/(1+math.e**(-0.1*reviewNum)))			# using sigmoid function to punish base on number of reviews

	asin = pagetable[did][0]
	if asin not in productScore:
		return -1
	else:
		# NBscore, GAscore, orig average score, review count
		data = productScore[asin]
		if data[0] == -1:
			return score(data[1], data[3]), data[2], data[3], data[0], data[1]			# score, orig avg score, review count, NBscore, GAscore
		else:
			return score(0.8*data[0]+0.2*data[1], data[3]), data[2], data[3], data[0], data[1]


def getDocRankList():			# conjunctive operation
	global metaDataList
	global termList
	docRankList = []			# [PgScore, did], [PgScore, did]
	termNum = len(termList)
	# print termList

	did = 1			# solve the initialize corner case
	flag = 0			# 0: normal, 1: need to find larger did, 2: no more did, exit
	maxDocID = metaDataList[0][-1][-2]		# get maxDocID for the first term
	
	while did <= maxDocID:
		did = nextGEQ(0, did)	
		if did is None:				# no more pages to be found
			# print 1
			break

		for i in xrange(1, termNum):
			nextdid = nextGEQ(i, did)
			if nextdid is None:		# no more pages to be found
				flag = 2			# exit code
				break
			if nextdid > did:
				flag = 1
				break
	
		if flag == 1:			# if not in intersection, find term0's next did
			did = nextdid
			flag = 0
			continue

		elif flag == 2:
			# print 2
			break

		else:				# when did contains all terms
			pgScore = PgScore(did)
			
			if pgScore == -1:
				did += 1
				continue

			docRankList.append([pgScore[0], pgScore[1], pgScore[2], pgScore[3], pgScore[4], did])
			did += 1

	docRankList.sort(reverse = True)
	
	return docRankList[:20]		# get top 20


def getUrl(docRankList):
	urlList = []
	for doc in docRankList:
		asin = pagetable[doc[-1]][0]
		urlList.append("http://www.amazon.com/dp/" + asin)		# url line
	return urlList
	
def getTitle(did):
	pgTbFile = open("../data/pgTable.txt", 'r')
	position = pagetable[did][1]
	pgTbFile.seek(position, 0)
	line = pgTbFile.readline()
	l = line.split(",")
	pgTbFile.close()
	return ','.join(l[2:])[:-1]


def main():
	global termList
	global lexiconList
	

	while True:
		query = raw_input('Type words for searching: ')
		flag = 0			# 0: normal, 1: not found query
		
		if query == 'exit()':
			print "Release memory..."
			break


		startTime = round(time.time()*1000)

		queryList = query.split(" ")
		cleanTerm = checkValid(queryList)
		if not cleanTerm:
			print "your input is not valid, try again with only letters or numbers"
		else:
			listIndex = 0
			sortHelper = []

			for term in cleanTerm:
				if term in lexicon:
					termList.append(term)
					lexiconList.append(lexicon[term])
					sortHelper.append([lexicon[term][-1], listIndex])
					listIndex += 1
				else:
					print "at least one word in the query doesn't exist"
					flag = 1		# query doesn't exist
					closeList()
					break

			if flag == 1:		# query doesn't exist
				continue

			sortedList = sort(termList, lexiconList, sortHelper)		# prepare sored inverted index list
			termList, lexiconList = sortedList[0], sortedList[1]

			for item in lexiconList:
				openList(item[0],item[1])		# load iilists(head, tail)

			getMetadata()		# for each term, get and load all metadata from all blocks

			docRankList = getDocRankList()
			urlList = getUrl(docRankList)
			
			if len(docRankList) != 0:
				endTime1 = round(time.time()*1000)
				print "You use " + str(float((endTime1-startTime))/1000) + " seconds."

				print "============RESULT============"
				for i in xrange(len(docRankList)):
					print str(i) + ": " + urlList[i]
					print "Title: " + getTitle(docRankList[i][-1])
					print "------------------------------"
					print "Product(ML) Score: " + str(docRankList[i][0])
					print "number of reviews: " + str(docRankList[i][2])
					print "------------------------------"					
					print "original average star: " + str(docRankList[i][1])
					print "NBscore: " + str(docRankList[i][3])
					print "GAscore: " + str(docRankList[i][4])
					print "==============================\n"
			else:
				print "oops, the queried terms cannot be found together in any page."
			
			closeList()					# clear all relevant lists after each query
	closeList()
	print "\nBye."				
	return


lexPrepare()
pagetbPrepare()
scorePrepare()
main()