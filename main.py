import sys
import os
import re
import string
import math

def computeConfusionMatrix(predicted, groundTruth, nAuthors):
	confusionMatrix = [[0 for i in range(nAuthors+1)] for j in range(nAuthors+1)]
	for i in range(len(groundTruth)):
		confusionMatrix[predicted[i]][groundTruth[i]] += 1
	return confusionMatrix

def outputConfusionMatrix(confusionMatrix,nAuthors):
	columnWidth = nAuthors
	print(str(' ').center(columnWidth),end=' ')
	for i in range(1,len(confusionMatrix)):
		print(str(i).center(columnWidth),end=' ')
	print()
	for i in range(1,len(confusionMatrix)):
		print(str(i).center(columnWidth),end=' ')
		for j in range(1,len(confusionMatrix)):
			print(str(confusionMatrix[j][i]).center(columnWidth),end=' ')
		print()

def populateStopWords():
	stopWords = []
	with open('stopwords.txt', "r", encoding="UTF-8", errors="ignore") as inputFile1:
		for line in inputFile1:
			if (line != '\n'):
				stopWords.append(line.rstrip())
	return stopWords

def stripWhitespace(inputString):
	return re.sub("\s+", " ", inputString.strip())

def tokenize(inputString):
	whitespaceStripped = stripWhitespace(inputString)
	punctuationRemoved = "".join([x for x in whitespaceStripped
								  if x not in string.punctuation])
	lowercased = punctuationRemoved.lower()
	return lowercased.split()

def main(pathname):
	stopWords = populateStopWords()
	stopwords_cleaned = []
	for a in stopWords:
		if a not in stopwords_cleaned:
			stopwords_cleaned.append(a)
	result = {}
	filenames = os.listdir(pathname)
	Nc = {}
	N = 0
	for b in filenames:
		if b[1] == 't':
			N = N+1
			dashloc = b.find('-')
			author = b[6:dashloc]
			if author in Nc:
				temp = Nc[author]
				temp.append(b)
				Nc[author] = temp
			else:
				Nc[author] = [b]
	authors = list(Nc.keys())
	authors.sort()
	Nci_dict = {}
	for c in stopwords_cleaned:
		for d in authors:
			examples = Nc[d]
			Nci = 0
			for e in examples:
				words = []
				with open(pathname+e, "r", encoding="UTF-8", errors="ignore") as inputFile2:
					for line in inputFile2:
						words.extend(tokenize(line))
				if c in words:
					Nci = Nci+1
			Nci_dict[(c,d)] = Nci
	for f in filenames:
		if f[1] == 's':
			curr_file = f
			tokens = []
			with open(pathname + f, "r", encoding="UTF-8", errors="ignore") as inputFile3:
				for line in inputFile3:
					tokens.extend(tokenize(line))
			currentMax = float('-inf')
			currentClass = ''
			for h in authors:
				nc = len(Nc[h])
				temp = math.log(nc/N,2)
				temp2 = 1
				for i in stopwords_cleaned:
					Nci = Nci_dict[(i, h)]
					if i in tokens:
						temp2 = temp2 * ((Nci + 1) / (nc + 2))
					else:
						temp2 = temp2 * (1 - (Nci + 1) / (nc + 2))
				temp = temp + math.log(temp2,2)
				if temp > currentMax:
					currentMax = temp
					currentClass = h
			predict_label = currentClass  # Suppose you get result 0-index result, corresponding to author 1
			result[pathname[14:] + curr_file] = 'Author' + predict_label  # Key: Filename; Value: Author. Example: “problemA/Asample01.txt”: “Author03”
	CCE = []
	for j in stopwords_cleaned:
		cce = 0
		for k in authors:
			temp = 1
			nc = len(Nc[k])
			Nci = Nci_dict[(j, k)]
			temp = temp * nc/N
			temp = temp * ((Nci + 1) / (nc + 2))
			temp = temp * math.log((Nci + 1) / (nc + 2),2)
			cce = cce - temp
		CCE.append((j,cce))
	CCE = sorted(CCE, key=lambda x: x[1], reverse = True)
	return result, CCE,authors


if __name__ == "__main__":
	truth = {}
	inputFile4 = open('ground_truth.txt', "r", encoding="UTF-8", errors="ignore")
	for row in inputFile4:
		line = row.split()
		if (len(line) < 2):
			continue
		if line[0][:9] == sys.argv[1][14:]:
			truth[line[0]] = line[1]
	result,CCE,authors = main(sys.argv[1])
	samples = list(result.keys())
	samples.sort()
	predictedAuthorIdNum = []
	groundTruthAuthorIdNum = []
	correctprediction = 0
	for x in samples:
		predictedAuthorIdNum.append(int(result[x][6:]))
		groundTruthAuthorIdNum.append(int(truth[x][6:]))
		if result[x] == truth[x]:
			correctprediction = correctprediction + 1
	nAuthors = len(authors)
	print("Problemset: "+sys.argv[1])
	print("Accuracy = " + str(correctprediction / len(samples)))
	print()
	print("Confusion Matrix (Vertical = Predicted, Horizontal = Actual):")
	outputConfusionMatrix(computeConfusionMatrix(groundTruthAuthorIdNum, predictedAuthorIdNum, nAuthors), nAuthors)
	print()
	print("Feature Ranking:")
	for l in range(20):
		print(CCE[l][0] + ": " + str(CCE[l][1]))



