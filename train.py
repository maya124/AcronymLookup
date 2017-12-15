# Machine-Learning Approach for Cross-Domain Acronym Definition Identification
# Maya Varma and Rachel Gardner
# Autumn 2017
# Train Machine Learning Classifier
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
from sklearn.grid_search import GridSearchCV
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




# Extracting Features


db = AcronymDatabase()

#Convert training data to sparse vectors
tokenize = CountVectorizer().build_tokenizer()
true_defs = []
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

cadList = db.getContextAcronymList()
vect = DictVectorizer()
X_train = vect.fit_transform(features(d) for d in cadList)
joblib.dump(vect, 'trained-models/vectorizer.pkl')
print X_train.toarray()


# Train Machine Learning Classifier
clf1 = MultinomialNB(alpha=0.09).fit(X_train, true_defs)
print 'Trained Model 1'
clf2 = svm.LinearSVC(C=1).fit(X_train, true_defs)
print 'Trained Model 2'
clf3 = tree.DecisionTreeClassifier(min_samples_leaf=1).fit(X_train, true_defs)
print 'Trained Model 3'
clf4 = RandomForestClassifier().fit(X_train, true_defs)
print 'Trained Model 4'

joblib.dump(clf1, 'trained-models/naivebayes.pkl') 
joblib.dump(clf2, 'trained-models/svc.pkl') 
joblib.dump(clf3, 'trained-models/decisiontree.pkl') 
joblib.dump(clf4, 'trained-models/randomforest.pkl') 


db.close()
