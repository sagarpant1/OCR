#!/usr/bin/python
#
# ./ocr.py : Perform optical character recognition, usage:
#     ./ocr.py train-image-file.png train-text.txt test-image-file.png
# 
# Authors: (insert names here)
# (based on skeleton code by D. Crandall, Oct 2017)
#

""" *******************Write Up for the Part-2************************
Calculating the transition probability from reading the training file-
While reading the training file line by line, the algorithm reduces the noise by removing the POS tags and the punctuation mark with a following.(dot) 
with just the punctuation mark. Then it reads the line character by character and thus stores the count for each transition.
The algorithm maintains two dictionaries first one to store the count of transition from the previous character to the current character and the second one to store the count of transitions from the previous character to any character. This is further used to calculate the transition probability.

Calculating the emission probability-
This could b addressed in different ways:
1) Calculating the ratio of match/total character between the test and the train letters. This approach gives works fine for noise-less data but fails for data with a lot of noise.
2) Maximizing the hit/miss ratio. Hit count is calculated by counting the matches for each pixel such the character is an asterisk '*'. Miss count is calculated by counting the pixels which have different characters for test and train data. Space count to count the number of spaces in both the test and the
train image. If the number of space count is very large then it means that there's a space. Otherwise, find the character with the highest hit/miss ratio.

Calculating initial probability-
This is calculated while reading the train data. A dictionary is maintained to store the count of each character as the first character of the
sentence. This count is later divided by the total count of all characters which appear as the first character of the sentence to compute the probability.

Methods employed to achieve the desired output-

1)Simple Bayes- This was done by maximising the hit/miss ratio for each character in the test image. The entire image sequence was computed using the same approach and final sequence was printed. 

2)HMM Using VE- This was calculated by finding the probability of each character occurring as the first character of the sentence. The product of Emission probability and initial probability was computed for each character. This was further used while computing the probability of the second character. The probability of the second character was computed by multiplying the transition probability with the probability from the previous state and summing it over all the possible transitions
and then multiplying the emission probability. This product was maximized for each possible character occurrence at position 2 and so on.

3) HMM Using Viterbi- This was calculated by finding the probability of each character occurring as the first character of the sentence. The product of Emission probability and initial probability was computed for each character. This was further used while computing the probability of the second character. The probability of the second character was computed by multiplying the transition probability with the probability from the previous state and then multiplying it with the emission probability. This product was maximized for each possible character occurrence at position 2 and so on."""

from PIL import Image, ImageDraw, ImageFont
import sys

CHARACTER_WIDTH=14
CHARACTER_HEIGHT=25

ignoreList = ['ADJ', 'ADV', 'ADP', 'CONJ', 'DET', 'NOUN', 'NUM', 'PRON', 'PRT', 'VERB', 'X']
punctuationList = ['(', ')', ',', '"', '.', '-', '!', '?', '\'']
totalTransitionPerChar = {}
transitionProb = {}
initialProb = {}
totalInitialChars = 0
totalChars = 0
totalKeySum = 0
TRAIN_LETTERS="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789(),.-!?\"' "

def load_letters(fname):
    im = Image.open(fname)
    px = im.load()
    (x_size, y_size) = im.size
    result = []
    for x_beg in range(0, int(x_size / CHARACTER_WIDTH) * CHARACTER_WIDTH, CHARACTER_WIDTH):
        result += [ [ "".join([ '*' if px[x, y] < 1 else ' ' for x in range(x_beg, x_beg+CHARACTER_WIDTH) ]) for y in range(0, CHARACTER_HEIGHT) ], ]
    return result

def load_training_letters(fname):
    global TRAIN_LETTERS
    letter_images = load_letters(fname)
    return { TRAIN_LETTERS[i]: letter_images[i] for i in range(0, len(TRAIN_LETTERS) ) }

def readData(fileName):
    file = open(fileName, "r")
    count = 0
    for line in file:
	#if count > 100:
	#    break
	line = line.rstrip('\n')
	populateToDict(line.lower())
	count = count + 1

def populateToDict(line):
    line = removePOS(line)
    line = removePunctuation(line)
    global totalChars
    for i in range(0, len(line)):
	totalChars = totalChars + 1
	if i == 0:
	    prevChar = line[i]
	    updateInitialProb(line[i])
	else:
	    seq = prevChar + '->' + line[i]
  	    updateTransitionProbability(seq, prevChar)
	    prevChar = line[i]

def updateTransitionProbability(seq, prevChar):
    if seq in transitionProb:
    	count = transitionProb.get(seq) + 1
        transitionProb[seq] = count
    else:
    	transitionProb[seq] = 1
    if prevChar in totalTransitionPerChar:
    	totalTransitionPerChar[prevChar] = totalTransitionPerChar.get(prevChar) + 1
    else:
    	totalTransitionPerChar[prevChar] = 1

def isIgnoreWord(word):
    if word in ignoreList:
	return True
    return False

def checkPunctuation(ch):
    if ch in punctuationList:
	return True
    return False

def updateInitialProb(ch):
    global totalInitialChars
    totalInitialChars = totalInitialChars + 1
    if ch in initialProb:
	initialProb[ch] = initialProb.get(ch) + 1
    else:
	initialProb[ch] = 1

def simpleBayes(train_letters, test_letters):
    simpleBayesSeq = 'Simple: '
    for i in range(0, len(test_letters)):
	testChar = test_letters[i]
	maxProb = 0
	for key in train_letters:
	    hitCount = 1
            missCount = 1
	    spaceCount = 0
	    trainChar = train_letters.get(key)
	    for j in range(0, len(trainChar)):
		for k in range(0, len(trainChar[j])):
		    if testChar[j][k] == ' ' and testChar[j][k] == trainChar[j][k]:
			spaceCount = spaceCount + 1
		    elif testChar[j][k] == '*' and testChar[j][k] == trainChar[j][k]:
			hitCount = hitCount + 1
		    else:
			missCount = missCount + 1
	    if spaceCount > ((CHARACTER_WIDTH * CHARACTER_HEIGHT) - 5):
                probableChar = key
		break
	    if (float(hitCount)/missCount) > maxProb:
		maxProb = (float(hitCount)/missCount)
		probableChar = key
	simpleBayesSeq = simpleBayesSeq + probableChar
    return simpleBayesSeq

def hmmUsingVE(train_letters, test_letters):
    finalSeq = 'HMM VE: '
    probChar = ''
    tow1 = {}
    tow2 = {}
    totalSum = 0
    for key in totalTransitionPerChar:
	totalSum = totalSum + totalTransitionPerChar.get(key)
    for i in range(0, len(test_letters)):
	maxProb = 0
    	testChar = test_letters[i]
    	if i == 0:
	    for j in range(0, len(TRAIN_LETTERS)):
		charCount = 1
	    	prob = findEmissionProbPerChar(testChar, train_letters.get(TRAIN_LETTERS[j]))
		if prob > maxProb:
		    maxProb = prob
		    probChar = TRAIN_LETTERS[j]
		if TRAIN_LETTERS[j].lower() in initialProb:
		    charCount = initialProb.get(TRAIN_LETTERS[j].lower())
	    	tow1[TRAIN_LETTERS[j]] = prob * (float(charCount)/totalInitialChars)
	    finalSeq = finalSeq + probChar
    	else:
	    for j in range(0, len(TRAIN_LETTERS)): #s2
		prob = 0
		totCount = totalSum
		currentLetter = TRAIN_LETTERS[j].lower()
	    	for k in range(0, len(TRAIN_LETTERS)): #s1
		    charCount = totalChars
		    totCount = totalChars
		    previousLetter = TRAIN_LETTERS[k].lower()
		    seq = previousLetter + '->' + currentLetter
		    if seq in transitionProb:
			charCount = charCount + transitionProb.get(seq)
		    if previousLetter in totalTransitionPerChar:
			totCount = totCount + totalTransitionPerChar.get(previousLetter)
		    prob = prob + ((float(charCount)/totCount) * tow1.get(TRAIN_LETTERS[i]) * findEmissionProbPerChar(testChar, train_letters.get(TRAIN_LETTERS[j])))
		if prob > maxProb:
		    maxProb = prob
		    probChar = TRAIN_LETTERS[j]
		tow2[TRAIN_LETTERS[j]] = prob
	    finalSeq = finalSeq + probChar
	    tow1 = tow2.copy()
	    tow2.clear()
    return finalSeq
		
def findEmissionProbPerChar(testChar, trainChar):
    hitCount = 1
    spaceCount = 0
    missCount = 1
    for j in range(0, len(trainChar)):
        for k in range(0, len(trainChar[j])):
    	    if testChar[j][k] == ' ' and testChar[j][k] == trainChar[j][k]:
	        spaceCount = spaceCount + 1
            elif testChar[j][k] == '*' and testChar[j][k] == trainChar[j][k]:
                hitCount = hitCount + 1
            else:
                missCount = missCount + 1
    if spaceCount > ((CHARACTER_WIDTH * CHARACTER_HEIGHT) - 5):
	probability = float(spaceCount)/(CHARACTER_WIDTH*CHARACTER_HEIGHT)
    else:
    	probability = float(hitCount)/(CHARACTER_WIDTH*CHARACTER_HEIGHT)
    return probability

def hmmUsingViterbi(train_letters, test_letters):
    finalSeq = 'HMM MAP: '
    probChar = ''
    tow1 = {}
    tow2 = {}
    totalSum = 0
    for key in totalTransitionPerChar:
        totalSum = totalSum + totalTransitionPerChar.get(key)
    for i in range(0, len(test_letters)):
        maxProb = 0
        testChar = test_letters[i]
        if i == 0:
            for j in range(0, len(TRAIN_LETTERS)):
                charCount = 1
                prob = findEmissionProbPerChar(testChar, train_letters.get(TRAIN_LETTERS[j]))
                if prob > maxProb:
                    maxProb = prob
                    probChar = TRAIN_LETTERS[j]
                if TRAIN_LETTERS[j].lower() in initialProb:
                    charCount = initialProb.get(TRAIN_LETTERS[j].lower())
                tow1[TRAIN_LETTERS[j]] = prob * (float(charCount)/totalInitialChars)
	    finalSeq = finalSeq + probChar
        else:
            for j in range(0, len(TRAIN_LETTERS)): #s2
                prob = 0
                totCount = totalSum
                currentLetter = TRAIN_LETTERS[j].lower()
                for k in range(0, len(TRAIN_LETTERS)): #s1
                    previousLetter = TRAIN_LETTERS[k].lower()
		    charCount = totalChars
                    totCount = totalChars
                    seq = previousLetter + '->' + currentLetter
                    if seq in transitionProb:
                        charCount = charCount + transitionProb.get(seq)
                    if previousLetter in totalTransitionPerChar:
                        totCount = totCount + totalTransitionPerChar.get(previousLetter)
                    prob = max(prob, ((float(charCount)/totCount) * tow1.get(TRAIN_LETTERS[k])))
		prob = prob * findEmissionProbPerChar(testChar, train_letters.get(TRAIN_LETTERS[j]))
                if prob > maxProb:
                    maxProb = prob
                    probChar =  TRAIN_LETTERS[j]
                tow2[TRAIN_LETTERS[j]] = prob
            finalSeq = finalSeq + probChar
            tow1 = tow2.copy()
            tow2.clear()
    return finalSeq

def removePOS(line):
    for i in range(0, len(ignoreList)):
	line = line.replace(' '+ignoreList[i].lower(), '')
    return line

def removePunctuation(line):
    for i in range(0, len(punctuationList)):
        line = line.replace(punctuationList[i]+' '+'.'+' ', punctuationList[i])
    return line


#####
# main program
(train_img_fname, train_txt_fname, test_img_fname) = sys.argv[1:]
train_letters = load_training_letters(train_img_fname)
test_letters = load_letters(test_img_fname)
readData(str(train_txt_fname))
print simpleBayes(train_letters, test_letters)
print hmmUsingVE(train_letters, test_letters)
print hmmUsingViterbi(train_letters, test_letters)
##print "***********************************************"
#print totalTransitionPerChar
## Below is just some sample code to show you how the functions above work. 
# You can delete them and put your own code here!


# Each training letter is now stored as a list of characters, where black
#  dots are represented by *'s and white dots are spaces. For example,
#  here's what "a" looks like:
##print "\n".join([ r for r in train_letters['a'] ])

# Same with test letters. Here's what the third letter of the test data
#  looks like:
##print "\n".join([ r for r in test_letters[2] ])



