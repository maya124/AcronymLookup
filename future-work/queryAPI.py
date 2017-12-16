# queryAPI.py [Rachel Gardner]
#
# This file is intended to allow the program to look up
# acronym definitions of acronyms it has never seen before
# (in any context). This is accomplished by quering the STANDS4 API.

from urllib import urlopen, urlencode, urlretrieve
import ConfigParser
import xml.etree.ElementTree as ET
import nltk
from gensim.models import Word2Vec

# parseResponse() - given a raw XML |response|, return the
# definition of the acronym
def parseResponse(response):
    tree = ET.fromstring(response.read())
    for result in tree:
        for attribute in result:
            if (attribute.tag == "definition"):
                return attribute.text

# parseConfigFile() - given a |configPath|,
# parse the config file to get the API key information
def parseConfigFile(configPath):
    config = ConfigParser.ConfigParser()
    config.read(configPath)
    section = 'Rachel Key'

    userID = config.get(section, 'user_ID')
    token = config.get(section, 'token')
    return {'uid':userID, 'tokenid':token}

# getDefinition() - given an |acronym|,
# return a list of possible definitions according to
# the STANDS4 API.
def getDefinition(acronym):
    query = parseConfigFile()
    
    url = "http://www.stands4.com/services/v2/abbr.php?"    
    query['term'] = acronym
    response = urlopen(url + urlencode(query))
    return parseResponse(response)

### EXPERIMENTAL - IN PROGRESS ###
# The following code is to experiment with predicting category from
# surrounding text. To do this effectively, we found that we would need
# to compile our own corpus (from the Wikipedia articles), since none of
# the existing corpora contained the highly specialized words we needed.

def saveModel():
    nltk.download('brown')
    sentences = nltk.corpus.brown.sents()
    model = Word2Vec(sentences, min_count=1)
    model.save('brown_model')
    print "Brown corpus model saved."
    return 'brown_model'

def loadModel(modelName):
    model = Word2Vec.load(modelName)
    #words most similar to mother
    print model.most_similar('autism')
    print model.most_similar('motor')
    print model.most_similar('software')
    print model.most_similar('cell')

def getCategory(text):
    categories = ['MEDICAL', 'SCIENCE', 'COMPUTING']
    subcategories = ['SCIENCE', 'BIOLOGY', 'BIOTECH', 'CHEMISTRY', 'ELECTRONICS', 'ENGINEERING', 'MATH', 'PHYSICS', 'ROBOTICS', 'MEDICAL', 'PHYSIOLOGY', 'BRITMEDICAL', 'COMPUTING', 'SECURITY', 'GENERALCOMP', 'HARDWARE', 'NETWORKING', 'SOFTWARE', 'TECHNOLOGY']
    
loadModel('brown_model')
