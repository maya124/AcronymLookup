# extractDefinition.py [Rachel Gardner]
#
# This file contains the formulation of the constraint satisfaction problem
# used to extract ground truth definitions from raw text that contains acronyms
# identified in a previous step. Simple test functionality is provided through the
# test(caseNum) function.

import collections, cspUtil
import re

# solveCSP() - given an |acronym| and |text| which
# gives the context of the acronym (but does not include
# the acronym itself, solve a constraint satisfaction
# problem.
# constraints (required):
#  - matched words in long form must be sequential
# factors (good to have):
#  - characters matching acronym are upper case
#  - characters matching acronyms are the first in the word
def solveCSP(acronym, text, threshold=1000):
    csp = cspUtil.CSP()

    for idx, char in enumerate(acronym):
        variableName = (idx, char)

        # create the domain
        # word is a string representing the word the variable corresponds to
        # wordIdx gives the index of the word in the text
        # charIdx gives the index of the character being matched in the word
        domain = []
        for wordIdx, word in enumerate(text):
            indices = [i for i, letter in enumerate(word) if letter.lower() == char.lower()]
            for charIdx in indices:
                domain.append((word, wordIdx, charIdx))
    
        csp.add_variable(variableName, domain)
        def is_first_char((candidateWord,_,index)):
            if (index == 0):
                return 10
            else:
                return 1
        csp.add_unary_factor(variableName, is_first_char)
        def is_upper((candidateWord,_,index)):
            if (candidateWord[index].isupper()):
                return 10
            else:
                return 1
        csp.add_unary_factor(variableName, is_upper)

    for idx in range(len(acronym)-1):
        var1 = (idx, acronym[idx])
        var2 = (idx+1, acronym[idx+1])
        def is_after(var1, var2):
            _,firstWordIdx,_ = var1
            _,secondWordIdx,_ = var2
        
            if secondWordIdx >= firstWordIdx:
                return 1
            else:
                return 0
        csp.add_binary_factor(var1, var2, is_after)

    search = cspUtil.BacktrackingSearch()
    search.solve(csp, True, True)

    # given the optimal assignment, re-create the definition
    # Note: this automatically includes all interim words
    # (ideally "and", "the" etc.)
    def extractDefinition(assignment):
        startIdx = assignment[min(assignment)][1]
        endIdx = assignment[max(assignment)][1]
        definition = text[startIdx:endIdx+1]
        return " ".join(definition)

    if (search.optimalWeight >= threshold):
        return extractDefinition(search.optimalAssignment)
    else:
        return None


# findDefinition() - given an |acronym|, the |text| containing
# the acronym, and the |index| at which the acronym was found
# in the text, find the appropriate definition for the acronym
def findDefinition(acronym, text, index):
    startIdx = index-5 if index-5 >=0 else 0
    endIdx = index+5 if index+5 <= len(text) else len(text)
    
    window = text[startIdx:index]
    leftSide = solveCSP(acronym, window)
    window = text[index+1:endIdx]
    rightSide = solveCSP(acronym, window)

    # prefer definition (acronym) format in case of a "tie"
    return leftSide if leftSide else rightSide

# test() - given a |caseNum| of a test case to test,
# run the CSP on that test case.
def test(caseNum):
    if (caseNum == 1):
        text = "Random Access Memory, or RAM (pronounced as ramm), is the physical hardware"
        acronym = "RAM"
    elif (caseNum == 2):
        text = "The National Aeronautics and Space Administration (NASA) is an independent agency of the executive branch"
        acronym = "NASA"
    elif (caseNum == 3):
        text = "ROS (Robot Operating System) provides libraries and tools to help software developers create robot applications."
        acronym = "ROS"
    elif (caseNum == 4):
        text = "The AMA, also known as the AmericanMedical Association is an organization."
        acronym = "AMA"
    elif (caseNum == 5):
        text = "complaint. History of present illness (HPI): the chronological order of "
        acronym = "HPI"
        
    text = re.split('\W+', text)
    index = text.index(acronym)

    return findDefinition(acronym, text, index)
