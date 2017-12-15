# Machine-Learning Approach for Cross-Domain Acronym Definition Identification
# Maya Varma and Rachel Gardner
# Autumn 2017
# Test Machine Learning Classifier
import sys
sys.path.append('postgres-database/')

from urllib import urlopen
import re
import csv
import os
from collections import defaultdict, Counter
import operator
import random 
from dbFunctions import AcronymDatabase
from sklearn.feature_extraction import text, DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.linear_model import SGDClassifier
from sklearn import tree, metrics, svm
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import matplotlib.pyplot as plt
from sklearn.externals import joblib


#Load in csv data (contains list of HTML urls)
def loadHTMLData():
    urls = []
    with open('data/data.csv', 'rU') as data:
        reader = csv.reader(data, dialect=csv.excel_tab)
        for row in reader:
            if(len((row[0].split(','))[1]) > 0): urls.append((row[0].split(','))[1])
    return urls

def loadDuplicateData():
    train = []
    test = []
    with open('data/duplicatedata.csv', 'rU') as data:
        reader = csv.reader(data, dialect=csv.excel_tab)
        count=0
        for row in reader:
            if(len((row[0].split(','))[1]) > 0): train.append((row[0].split(','))[2])
            if(count%2 == 0 and len((row[0].split(','))[1]) > 0): train.append((row[0].split(','))[3])
            elif(count%2 == 1 and len((row[0].split(','))[1]) > 0): test.append((row[0].split(','))[3])
            count+=1
    return (train, test)

urls = loadHTMLData()
trainingUrlsDuplicates = loadDuplicateData()[0] 
testingUrlsDuplicates = loadDuplicateData()[1]
trainingUrls = trainingUrlsDuplicates + urls[:int(0.7*len(urls))]
testingUrls = testingUrlsDuplicates + urls[int(0.7*len(urls)):]
print 'Size of Training Dataset: ', len(trainingUrls)
print 'Size of Testing Dataset: ', len(testingUrls)



#Adapted from NLTK package. Removes HTML markup from given string. 
def clean_html(html):
    # First we remove inline JavaScript/CSS:
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html.strip())
    # Then we remove html comments. This has to be done before removing regular
    # tags since comments can contain '>' characters.
    cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)
    # Next we can remove the remaining tags:
    cleaned = re.sub(r"(?s)<.*?>", " ", cleaned)
    # Finally, we deal with whitespace
    cleaned = re.sub(r"&nbsp;", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    return (cleaned.strip()).split()


#Takes url as input. Returns list of all acronyms in webpage
def identifyAcronyms(rawText):
    acronyms = []
    #words commonly misidentified as acronyms are manually blacklisted
    blacklist = ['ABSTRACT', 'INTRODUCTION', 'CONCLUSION', 'CONCLUSIONS', 'ACKNOWLEDGEMENTS', 'RESULTS']
    for i in range(1,len(rawText)-1):
        word = rawText[i]
        word = re.sub(r'[^\w\s]','',word)
        '''
        characteristics of an acronym: all capital letters, length > 2,
        contains only alphabet characters, not in blacklist, and not part
        of a header (identified by determining if surrounding words are in all-caps)
        '''
        nextIndex = i+1
        prevIndex = i-1
        if(len(word)>2 and word[:-1].isupper() and word.isalpha()            and word not in blacklist and not(rawText[i-1].isupper())            and not(rawText[i+1].isupper())):
            acronyms.append((word, i))    
    return acronyms

db = AcronymDatabase()

clf1 = joblib.load('trained-models/naivebayes.pkl') 
clf2 = joblib.load('trained-models/svc.pkl') 
clf3 = joblib.load('trained-models/decisiontree.pkl') 
clf4 = joblib.load('trained-models/randomforest.pkl') 
vect = joblib.load('trained-models/vectorizer.pkl')
tokenize = CountVectorizer().build_tokenizer()

'''MEASURE ACCURACY OF TRAIN DATASET'''
trainData = []
y_true = []
#count=0
for fl in (trainingUrls):
    #print "URL Index: %d" % urls.index(fl)
    #print count
    #count+=1
    try:
        html = urlopen(fl).read()
    except:
        continue
    rawText = clean_html(html)
    footerIndices = [i for i, x in enumerate(rawText) if x.lower()=='references']
    headerIndices = [i for i, x in enumerate(rawText) if x.lower()=='abstract']
    if(len(footerIndices)>0): rawText = rawText[:max(footerIndices)] #remove extraneous information
    if(len(headerIndices)>0): rawText = rawText[max(headerIndices):] #remove extraneous information

    def findContext(acronym, i):
        startIndex=i-15
        if (i-10 < 0): startIndex=0
        endIndex = i+15 
        if (i+10 > len(rawText)): endIndex = len(rawText)-1
        context = []
        for word in rawText[startIndex:endIndex+1]:
            word = word.lower()
            word = "".join(re.findall("[a-zA-Z]+", word))
            if(len(word)==0 or word==acronym.lower()): continue
            context.append(word)
        return " ".join(context)

    #Populate PostGres Database
    acronyms = identifyAcronyms(rawText) #list of all acronyms and corresponding index in rawtext
    for acronym, i in acronyms:
        if(db.getTrueDefinition(acronym, fl)==None): continue #Definition has been labeled in database
        context = findContext(acronym, i)
        trainData.append((acronym, context))
        y_true.append(db.getTrueDefinition(acronym, fl))        

X_new_counts = vect.transform(features(d) for d in trainData)
predicted1 = clf1.predict(X_new_counts)
predicted2 = clf2.predict(X_new_counts)
predicted3 = clf3.predict(X_new_counts)
predicted4 = clf4.predict(X_new_counts)

print "Prediction Accuracy - Multinomial NB: ", accuracy_score(y_true, predicted1)
print metrics.precision_recall_fscore_support(y_true, predicted1, average='weighted')
print "Prediction Accuracy - SVC: ", accuracy_score(y_true, predicted2)
print metrics.precision_recall_fscore_support(y_true, predicted2, average='weighted')
print "Prediction Accuracy - Decision Tree: ", accuracy_score(y_true, predicted3)
print metrics.precision_recall_fscore_support(y_true, predicted3, average='weighted')
print "Prediction Accuracy - Random Forest: ", accuracy_score(y_true, predicted4)
print metrics.precision_recall_fscore_support(y_true, predicted4, average='weighted')

'''MEASURE ACCURACY OF TEST DATASET: BREADTH'''
testData = []
y_true_test = []
for fl in (testingUrls):
    #print "URL Index: %d" % urls.index(fl)
    try:
        html = urlopen(fl).read()
    except:
        continue
    rawText = clean_html(html)
    footerIndices = [i for i, x in enumerate(rawText) if x.lower()=='references']
    headerIndices = [i for i, x in enumerate(rawText) if x.lower()=='abstract']
    if(len(footerIndices)>0): rawText = rawText[:max(footerIndices)] #remove extraneous information
    if(len(headerIndices)>0): rawText = rawText[max(headerIndices):] #remove extraneous information

    def findContext(acronym, i):
        startIndex=i-15
        if (i-10 < 0): startIndex=0
        endIndex = i+15 
        if (i+10 > len(rawText)): endIndex = len(rawText)-1
        context = []
        for word in rawText[startIndex:endIndex+1]:
            word = word.lower()
            word = "".join(re.findall("[a-zA-Z]+", word))
            if(len(word)==0 or word==acronym.lower()): continue
            context.append(word)
        return " ".join(context)

    acronyms = identifyAcronyms(rawText) #list of all acronyms and corresponding index in rawtext
    for acronym, i in acronyms:
        if(db.getTrueDefinition(acronym, fl)==None): continue #Definition has been labeled in database
        if(db.getTrueDefinition(acronym, fl) not in y_true): continue
        context = findContext(acronym, i)
        testData.append((acronym, context))
        y_true_test.append(db.getTrueDefinition(acronym, fl))        

X_new_counts = vect.transform(features(d) for d in testData)
predicted1 = clf1.predict(X_new_counts)
predicted2 = clf2.predict(X_new_counts)
predicted3 = clf3.predict(X_new_counts)
predicted4 = clf4.predict(X_new_counts)

print "Prediction Accuracy - Multinomial NB: ", accuracy_score(y_true_test, predicted1)
print metrics.precision_recall_fscore_support(y_true_test, predicted1, average='weighted')
print "Prediction Accuracy - SVC: ", accuracy_score(y_true_test, predicted2)
print metrics.precision_recall_fscore_support(y_true_test, predicted2, average='weighted')
print "Prediction Accuracy - Decision Tree: ", accuracy_score(y_true_test, predicted3)
print metrics.precision_recall_fscore_support(y_true_test, predicted3, average='weighted')
print "Prediction Accuracy - Random Forest: ", accuracy_score(y_true_test, predicted4)
print metrics.precision_recall_fscore_support(y_true_test, predicted4, average='weighted')

def features(cad):
    acronym = cad[0]
    context = cad[1]
    if(len(cad)==3): true_defs.append(cad[2])
    terms = tokenize(context)
    d = {acronym: 10}
    for t in terms:
        if(t not in text.ENGLISH_STOP_WORDS):
            d[t] = d.get(t, 0) + 1
    return d


'''MEASURE ACCURACY OF TEST DATASET: DEPTH'''
testDataDuplicates = []
y_true_test_duplicates = []
for fl in (testingUrlsDuplicates):
    try:
        html = urlopen(fl).read()
    except:
        continue
    rawText = clean_html(html)
    footerIndices = [i for i, x in enumerate(rawText) if x.lower()=='references']
    headerIndices = [i for i, x in enumerate(rawText) if x.lower()=='abstract']
    if(len(footerIndices)>0): rawText = rawText[:max(footerIndices)] #remove extraneous information
    if(len(headerIndices)>0): rawText = rawText[max(headerIndices):] #remove extraneous information

    def findContext(acronym, i):
        startIndex=i-15
        if (i-10 < 0): startIndex=0
        endIndex = i+15 
        if (i+10 > len(rawText)): endIndex = len(rawText)-1
        context = []
        for word in rawText[startIndex:endIndex+1]:
            word = word.lower()
            word = "".join(re.findall("[a-zA-Z]+", word))
            if(len(word)==0 or word==acronym.lower()): continue
            context.append(word)
        return " ".join(context)

    acronyms = identifyAcronyms(rawText) #list of all acronyms and corresponding index in rawtext
    for acronym, i in acronyms:
        if(db.getTrueDefinition(acronym, fl)==None): continue #Definition has been labeled in database
        if(db.getTrueDefinition(acronym, fl) not in y_true): continue
        context = findContext(acronym, i)
        testDataDuplicates.append((acronym, context))
        y_true_test_duplicates.append(db.getTrueDefinition(acronym, fl))        

X_new_counts_duplicates = vect.transform(features(d) for d in testDataDuplicates)
predicted1 = clf1.predict(X_new_counts_duplicates)
predicted2 = clf2.predict(X_new_counts_duplicates)
predicted3 = clf3.predict(X_new_counts_duplicates)
predicted4 = clf4.predict(X_new_counts_duplicates)

print "Prediction Accuracy - Multinomial NB: ", accuracy_score(y_true_test_duplicates, predicted1)
print metrics.precision_recall_fscore_support(y_true_test_duplicates, predicted1, average='weighted')
print "Prediction Accuracy - SVC: ", accuracy_score(y_true_test_duplicates, predicted2)
print metrics.precision_recall_fscore_support(y_true_test_duplicates, predicted2, average='weighted')
print "Prediction Accuracy - Decision Tree: ", accuracy_score(y_true_test_duplicates, predicted3)
print metrics.precision_recall_fscore_support(y_true_test_duplicates, predicted3, average='weighted')
print "Prediction Accuracy - Random Forest: ", accuracy_score(y_true_test_duplicates, predicted4)
print metrics.precision_recall_fscore_support(y_true_test_duplicates, predicted4, average='weighted')

db.close()

