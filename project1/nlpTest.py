# nlpTest.py
# Joseph Mercedes

import sys
import os
import errno
import operator
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.stem.lancaster import LancasterStemmer
from nltk import stem
from math import log, sqrt

def main():
    
    # Read the folder with the stats of the training stats
    inputTrain = raw_input("Name of the folder with stored training stats: ")
    subDict = []
    mainDict = dict()
    labels = []
    for files in os.listdir(inputTrain):
        labels.append(files.replace(".txt", ""))
    labels.remove('main')

    for l in labels:
        subDict.append(dict())

    # Indices for labels
    hashLabel = {}
    index = 0
    for l in labels:
        hashLabel[l] = index
        index = index + 1

    # Load the stats from the training documents
    for each in labels:
        files = open(inputTrain + "/" + each + ".txt").read().splitlines()
        for every in files:
            split = every.split()
            subDict[hashLabel[each]][split[0]] = float(split[1])
    files = open(inputTrain + "/main.txt").read().splitlines()
    for every in files:
        splitted = every.split()
        mainDict[splitted[0]] = float(splitted[1])

    # Read in the testing documents
    try:
        fileName = raw_input('Please enter the name of the file that contains the list of labeled testing documents: ')
        testFiles = open(fileName).read().splitlines()
    except EXPECTED_EXCEPTION_TYPES as e:
        print 'Not Valid File'

    # NLP features
    punct = [",", "''", "?", "", ";", ":", ".", "`", "``"]
    stop = stopwords.words('english') #+ punct
    
    texts = []
    stemmer = PorterStemmer()
    snowStemmer = stem.snowball.EnglishStemmer()
    wordNet = WordNetLemmatizer()
    lanStemmer = LancasterStemmer()
    for files in testFiles:
        fil = open(files)
        raw = fil.read().lower()
        fil.close()
        tokens = nltk.word_tokenize(raw)
        tokens = nltk.Text(tokens)
        noStop = [w for w in tokens if w not in stop]
        #stemmed = [snowStemmer.stem(t) for t in tokens] #maybe use?
        lemmatized = [wordNet.lemmatize(t) for t in noStop]
        #stemmed = [lanStemmer.stem(t) for t in noStop]
        #stemmed = [stemmer.stem(t) for t in tokens]
        texts.append(lemmatized)

    # Compute tf*idf and categorize documents
    index = 0
    docs = open("corpus1_predictions.labels", "w")
    for text in texts:
        docDict = dict()
        for w in text:
            if w in docDict:
                docDict[w] += 1.0
            else:
                docDict[w] = 1.0
        frequencyMaximum = docDict[max(docDict.iteritems(), key=operator.itemgetter(1))[0]]

        for w in text:
            if w in mainDict:
                docDict[w] = (0.25 + docDict[w]*0.25/frequencyMaximum)*mainDict[w] #Weighting the term frequency
                #docDict[w] = (docDict[w]/frequencyMaximum)*mainDict[w]
            else:
                docDict[w] = 0
                
        # Compute distance to each category and categorize based off minimum distance
        minDistance = []
        for l in range(len(labels)):
            dotProduct = 0
            docMagnitude = 0
            docMagnitudePrime = 0
            for w in docDict:
                if w in subDict[l]:
                    dotProduct += docDict[w]*subDict[l][w]
                    docMagnitude += docDict[w]*docDict[w]
                    docMagnitudePrime += subDict[l][w]*subDict[l][w]
            docMagnitude = sqrt(docMagnitude)
            docMagnitudePrime = sqrt(docMagnitudePrime)
            distance = dotProduct/(docMagnitude*docMagnitudePrime)
            if minDistance:
                if distance > minDistance[0]:
                    minDistance = [distance, l]
            else:
                minDistance = [distance, l]    

        docs.write(testFiles[index] + " " + labels[minDistance[1]] + "\n")
        index += 1
    docs.close()
    print "The predictions are in corpus1_predictions.txt"
    
if __name__ == "__main__":
    main()
