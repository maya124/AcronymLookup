# generateURLSpreadsheet.py
#
# Create spreadsheets of URLs for Wikipedia articles in the categories listed in categories.txt

import urllib
import csv
import sys
import json as simplejson
import argparse

# listCategoryMembers() - given a |category|,
# query the Wikipedia API and return a JSON object
# of all Wikipedia pages/categories under that category.
def listCategoryMembers(category):
    api_url = 'http://en.wikipedia.org/w/api.php?'
    params = {'action': 'query', 'list': 'categorymembers', 'cmlimit':500, 'format':'json', 'prop':'info', 'inprop':'fullurl', 'cmtitle': u'Category:{}'.format(category), 'cmsort':'timestamp'}
    try:
        url = urllib.urlencode(params)
    except UnicodeEncodeError:
        return [] # sorry Schr\xf6dinger equation

    search_results = urllib.urlopen(api_url + url)
    json = simplejson.loads(search_results.read())
    try:
        result = json['query']['categorymembers']
    except:
        print("Skipping category due to error: ", json)
        result = None
    return result

# recurse() - given a |writer| referring to the
# current file to write to, a |category| indicating
# the current page/category and a |level| indicating
# the current recursive depth, this function either
# writes out the current page, or recurses on its
# subcategories (so long as the maximum recursive depth
# has not been reached).
def recurse(writer, category, level):
    global URLCount, visited

    if (level <= 0 or URLCount <= 0):
        return

    categoryMembers = listCategoryMembers(category)
    if (categoryMembers == None):
        return
    for pageData in categoryMembers:
        if (pageData['pageid'] not in visited):
            # if found a subcategory
            if(pageData['title'][:len("Category:")] == "Category:"):
                recurse(writer, pageData['title'][len("Category:"):], level-1)
            else:
                pageUrl = u'https://en.wikipedia.org/?curid={}'.format(pageData['pageid'])
                writer.writerow([pageData['title'].encode('ascii', 'ignore'), pageUrl])
                URLCount -= 1
                visited.add(pageData['pageid'])

visited = set()
URLCount = 0

# generateSpreadsheets() - reads from categories.txt to generate
# spreadsheets of |numUrls| Wikipedia URLs in those categories.
# Note that this function only traverses |recursionDepth| subcategories.
def generateSpreadsheets(recursionDepth, numURLs):
    global URLCount
    with open('categories.txt', 'r') as categoriesList:
        category = categoriesList.readline()
        while (category != None and category != ""):
            print("Now adding: %s " % category)
            URLCount = numURLs
            with open('categories/%s.csv' % category, 'wb') as csvfile:
                writer = csv.writer(csvfile, dialect=csv.excel_tab)
                recurse(writer, category, recursionDepth)
                category = categoriesList.readline()

parser = argparse.ArgumentParser()
parser.add_argument('--recursionDepth', type=int, help='number of sublevels of categories to traverse', default=3)
parser.add_argument('--numURLs', type=int, help='approximately how many URLs per category to explore', default=3000)

args = parser.parse_args()
generateSpreadsheets(args.recursionDepth, args.numURLs)
