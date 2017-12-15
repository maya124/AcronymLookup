# Machine-Learning Approach for Cross-Domain Acronym Definition Identification
# Maya Varma and Rachel Gardner
# Autumn 2017
# Moxel Model
import re
from collections import defaultdict, Counter
from sklearn.feature_extraction import text, DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from sklearn.externals import joblib


#Takes url as input. Returns list of all acronyms in webpage
def identifyAcronyms(rawText):
    acronyms = []
    #words commonly misidentified as acronyms are manually blacklisted
    blacklist = ['ABSTRACT', 'INTRODUCTION', 'CONCLUSION', 'CONCLUSIONS', 'ACKNOWLEDGEMENTS', 'RESULTS']
    for i in range(0,len(rawText)-1):
        word = rawText[i]
        word = re.sub(r'[^\w\s]','',word)
        '''
        characteristics of an acronym: all capital letters, length > 2,
        contains only alphabet characters, not in blacklist, and not part
        of a header (identified by determining if surrounding words are in all-caps)
        '''
        nextIndex = i+1
        prevIndex = i-1
        if(len(word)>2 and word[:-1].isupper() and word.isalpha() and word not in blacklist):
            acronyms.append((word, i))    
    return acronyms

model = joblib.load('trained-models/naivebayes.pkl')
vect = joblib.load('trained-models/vectorizer.pkl')
tokenize = CountVectorizer().build_tokenizer()

def findContext(acronym, i, rawText):
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

def predict(sentence):
    rawText = sentence.split(' ')
    acronyms = identifyAcronyms(rawText)
    data = []
    for acronym, i in acronyms:
        context = findContext(acronym, i, rawText)
        data.append((acronym,context))
    featureVect = vect.transform(features(d) for d in data)
    predicted = model.predict(featureVect)
    results = ''
    for train, definition in zip(data, predicted):
        results += '%s => %s\n' % (train[0], definition)
    return {'results': results}
#print predict('NASA is an aeronatical space company.')
