#nlpTrain.py
#Joseph Mercedes

import sys
import os
import errno
import operator
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem import WordNetLemmatizer
from nltk import stem
from math import log

def main():
    
    # Read in the input file with the list of training files and category labels
    try:
        fileName = raw_input('Please enter the name of the file that contains the list of labeled training documents: ')
        trainFilesLabels = open(fileName).read().splitlines()
    except EXPECTED_EXCEPTION_TYPES as e:
        print 'Not Valid File'
    
    splitTrain = []
    for item in trainFilesLabels:
        splitTrain.append(item.split())
    splitTrain = zip(*splitTrain)

    splitTrain[0] = list(splitTrain[0])
    splitTrain[1] = list(splitTrain[1])
    trainFiles = splitTrain[0]
    trainLabels = list(set(splitTrain[1]))

    # Indices for Labels
    hashLabels = {}
    index = 0
    for label in trainLabels:
        hashLabels[label] = index
        index = index + 1

    # List of Filenames and Indices
    index = 0
    for stuff in splitTrain[0]:
        splitTrain[1][index] = hashLabels[splitTrain[1][index]]
        index = index + 1

    punct = [",", "''", "?", "", ";", ":", ".", "`", "``"]
    stop = stopwords.words('english') #+ punct

    # Enter file name for output training stats
    try:
        outTrain = raw_input("Enter the name of the file to which the training stats will be stored: ")
        os.mkdir(outTrain)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(outTrain):
            pass

    #NLP Features
    punct = [",", "''", "?", "", ";", ":", ".", "`", "``"]
    stop = stopwords.words('english') #+ punct
    
    texts = []
    stemmer = PorterStemmer()
    snowStemmer = stem.snowball.EnglishStemmer()
    lanStemmer = LancasterStemmer()
    wordNet = WordNetLemmatizer()
    for files, indices in zip(*splitTrain):
        fil = open(files)
        raw = fil.read().lower()
        fil.close()
        tokens = nltk.word_tokenize(raw)
        tokens = nltk.Text(tokens)
        noStop = [w for w in tokens if w not in stop]
        #stemmed = [snowStemmer.stem(t) for t in tokens] #maybe use?
        #lemmatized = [wordNet.lemmatize(t) for t in tokens]
        #stemmed = [lanStemmer.stem(t) for t in noStop]
        #stemmed = [stemmer.stem(t) for t in tokens]
        texts.append([noStop, indices])

    # Compute tf*idf
    numberLabels = len(trainLabels)
    corpusDict = []
    for i in range(numberLabels):
        corpusDict.append(dict())
    mainDict = dict()
    for text, indices in texts:
        documentDict = dict()
        for t in text:
            if t in documentDict:
                documentDict[t] += 1.0
            else:
                documentDict[t] = 1.0
        frequencyMax = documentDict[max(documentDict.iteritems(), key=operator.itemgetter(1))[0]]
        for d in documentDict:
            documentDict[d] = 0.25 + documentDict[d]*0.25/frequencyMax #Weighting the term frequency
            #documentDict[d] = documentDict[d]/frequencyMax
            if d in mainDict:
                mainDict[d] += 1.0
            else:
                mainDict[d] = 1.0
            if d in corpusDict[indices]:
                corpusDict[indices][d][0] += documentDict[d]
                corpusDict[indices][d][1] += 1.0
            else:
                corpusDict[indices][d] = [documentDict[d], 1.0]
                
    index = 0
    for docs in corpusDict:
        docName = str(trainLabels[index])
        docName = open(outTrain + "/" + docName + ".txt", "w")
        for d in docs:
            corpusDict[index][d][1] = log(len(texts)/(corpusDict[index][d][1]))
            corpusDict[index][d][0] = corpusDict[index][d][0]*corpusDict[index][d][1]
            docName.write(d + " " + str(corpusDict[index][d][0]) +  "\n")
        docName.close()
        index += 1
    docName = open(outTrain + "/main.txt", "w")
    for w in mainDict:
        mainDict[w] = log(len(texts)/(mainDict[w]))
        docName.write(w + " " + str(mainDict[w]) + "\n")
    docName.close()

if __name__ == "__main__":
    main()
