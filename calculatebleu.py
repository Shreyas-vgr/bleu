import codecs
import math
import os
import sys
from operator import itemgetter


def Ngrams(line, n):
  return zip(*[line[i:] for i in range(n)])


def brevityPenalty(r, c):
    if c > r:
        bp = 1.0
    else:
        bp = math.exp(1-(float(r)/c))
    return bp

def countClip(candDict, refDict):
    count = 0
    for key in candDict.keys():
        candidateWordCount = candDict[key]
        maxMatch = 0
        for reference in refDict:
            if key in reference:
                maxMatch = max(maxMatch, reference[key])
        candidateWordCount = min(candidateWordCount, maxMatch)
        count += candidateWordCount
    return count


def getBestLength(referenceLengths , candidateLen):
    result = [abs(x - candidateLen) for x in referenceLengths]
    bestlenIndex = min(enumerate(result), key=itemgetter(1))[0]
    return referenceLengths[bestlenIndex]

def getPrecisionNgram(candidate, references):
    precesion = []
    for i in xrange(1, 5):
        countClippedVal = 0
        wordCount = 0
        c = 0
        r = 0
        p = 0.0
        for line in xrange(len(candidate)):
            candDict = {}
            data = candidate[line].lower().strip().split()
            ngrams = []
            candidateLen = len(data)
            for ngram in Ngrams(data,i):
                ngrams.append(" ".join(ngram))
            for ngram in ngrams:
                if ngram in candDict:
                    candDict[ngram] += 1
                else:
                    candDict[ngram] = 1
            #print candDict
            referenceslist=[]
            referenceLengths=[]
            for reference in references:
                referencedata = reference[line].lower().strip().split()
                referenceNgrams=[]
                referenceDict ={}
                referenceLen = len(referencedata)
                referenceLengths.append(referenceLen)
                for ngram in Ngrams(referencedata,i):
                    referenceNgrams.append(" ".join(ngram))
                for ngram in referenceNgrams:
                    if ngram in referenceDict:
                        referenceDict[ngram] += 1
                    else:
                        referenceDict[ngram] = 1
                #print referenceDict
                referenceslist.append(referenceDict)
            countClippedVal += countClip(candDict, referenceslist)
            c += candidateLen
            r += getBestLength(referenceLengths , candidateLen)
            wordCount += len(ngrams)   ### change to ngram len of candidate
        if countClippedVal!=0:
            p = float(countClippedVal)/wordCount
        precesion.append(p)
    bp = brevityPenalty(r,c)
    #print bp
    #print precesion
    geometricMean = reduce(lambda x, y: x*y, precesion)**(1.0/len(precesion))
    bleu = geometricMean * bp
    #print bleu
    return bleu


candidatePath = sys.argv[1]
#candidatePath = "candidate-3.txt"
with codecs.open(candidatePath,encoding="utf-8") as f:
    candidateData = f.readlines()
referencePath = sys.argv[1]
#referencePath="reference-3.txt"
referenceData = []
if os.path.isdir(referencePath):
    for files in os.listdir(referencePath):
        with codecs.open(referencePath+files,encoding="utf-8") as f:
            referenceData.append(f.readlines())
else:
    with codecs.open(referencePath,encoding="utf-8") as f:  ### change to dir of references
        referenceData.append(f.readlines())

bleu = getPrecisionNgram(candidateData,referenceData)

with open("bleu_out.txt","w") as f:
    f.write(str(bleu))
