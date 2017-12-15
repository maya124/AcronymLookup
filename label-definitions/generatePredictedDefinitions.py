import nltk   
from urllib import urlopen
import urllib
import urllib2
import re
import csv
import os
import textract
from collections import defaultdict, Counter
import operator
import random 
from sklearn import svm
from sklearn.feature_extraction import DictVectorizer
from extractDefinition import findDefinition

'''
generatePredictedDefinitions: Creates csv file with all predicted definitions
for all files in the training/testing set. CSV file is then manually edited.
'''

def loadHTMLData():
    urls = []
    with open('data/data.csv', 'rU') as data:
        reader = csv.reader(data, dialect=csv.excel_tab)
        for row in reader:
            if(len((row[0].split(','))[1]) > 0): urls.append((row[0].split(','))[1])
    return urls

urls = loadHTMLData()

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
        if(len(word)>2 and word[:-1].isupper() and word.isalpha() \
           and word not in blacklist and not(rawText[i-1].isupper()) \
           and not(rawText[i+1].isupper())):
            acronyms.append((word, i))    
    return acronyms

'''
#Store list of identified definitions
for fl in (urls):
    print urls.index(fl)
    try:
        html = urllib2.urlopen(fl, timeout=30).read()
    except:
        print 'error'
        continue
    rawText = clean_html(html)
    footerIndices = [i for i, x in enumerate(rawText) if x.lower()=='references']
    headerIndices = [i for i, x in enumerate(rawText) if x.lower()=='abstract']
    if(len(footerIndices)>0): rawText = rawText[:max(footerIndices)] #remove extraneous information
    if(len(headerIndices)>0): rawText = rawText[max(headerIndices):] #remove extraneous information

    #find an appropriate definition for an acronym based on surrounding text
  
    def findDefinition(acronym, i):
        startIndex=i-len(acronym)-3
        if (i-len(acronym)-3 < 0): startIndex=0
        endIndex = i+len(acronym)+3 
        if (i+len(acronym)+3 > len(rawText)): endIndex = len(rawText)-1
        scores = {} #store scores for each possible definition
        for j in range(startIndex, endIndex+1-len(acronym)):
            potentialDef = ' '.join(rawText[j:j+len(acronym)])
            potentialDef = ' '.join(re.findall("[a-zA-z]+", potentialDef))
            potentialDef = potentialDef.lower()
            score = 0
            if(len(potentialDef.split()) < len(acronym)): continue
            for k in range(len(acronym)):
                if(potentialDef.split()[k][0].lower()==acronym[k].lower()):
                    score+=1
            scores[potentialDef] = score
        if(len(scores.values())==0 or max(scores.values()) <= 1): return 'unknown'
        else: return max(scores.iteritems(), key=operator.itemgetter(1))[0] #definition wiht maximum score
    
    currentAcronymDefs = {} #local database links acronym text to definitions (file-specific)
    acronyms = identifyAcronyms(rawText) #list of all acronyms and corresponding index in rawtext
    for acronym, i in acronyms:
        if acronym not in currentAcronymDefs:
            definition = findDefinition(acronym, rawText, i)
            if (definition):
                currentAcronymDefs[acronym] = (definition, " ".join(rawText[i-5:i+5]))

    with open('definitions_new.csv', 'a') as csvfile:
        writer = csv.writer(csvfile)
        for ac in currentAcronymDefs:
            writer.writerow([ac, currentAcronymDefs[ac][0], fl, currentAcronymDefs[ac][1]])
'''
with open('definitions_editing.csv', 'rU') as csvfile1:
    with open('definitions_new.csv', 'rU') as csvfile2:
            reader1 = csv.reader(csvfile1)
            reader2 = csv.reader(csvfile2)
            data = list(reader2)
            for row in reader1:
                found=0
                for otherrow in data:
                    if(row[0]==otherrow[0] and row[2]==otherrow[2]):
                        with open('definitions_combined.csv', 'a') as out:
                            writer = csv.writer(out)
                            writer.writerow([otherrow[0], otherrow[1], otherrow[2], otherrow[3]])
                        found=1
                if(found==0):
                    with open('definitions_combined.csv', 'a') as out:
                        writer = csv.writer(out)
                        writer.writerow([row[0], row[1], row[2], ''])
                    
                

