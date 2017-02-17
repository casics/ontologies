#!/usr/bin/env python3.4
#
# @file         classify.py
# @brief	Use a CDE to classify GitHub projects
# @author 	Matthew Graham
#
# <!---------------------------------------------------------------------------
# Copyright (C) 2017 by the California Institute of Technology.
# This software is part of CASICS, the Comprehensive and Automated Software
# Inventory Creation System.  For more information, visit http://casics.org.
# ------------------------------------------------------------------------- -->

import dag
import CDE
from process-readme import preprocess, tfidf_vectorizer, svd_vectorizer

import sys
import os

sys.path.append('/Users/mjg/Projects/casics/casics/src')
import casics

if __name__ == '__main__' and __package__ is None:
    sys.path.append(os.path.join(os.path.dirname(__file__), "../database"))
    from casicsdb import *

# Main body.
# .............................................................................

def main():
    # Get label hierarchy
    concepts = DAG("lcsh.graphml")
    
    # Get training set
    ids, X, y = get_training_set()

    # Initialize CDE
    cde = CDE(concepts)

    # Train CDE
    cde.fit(X, y)

# Helpers
# .............................................................................

def get_training_set():
    '''Load the training set of annotated repos from the db'''
    # Connect to db
    casicsdb = CasicsDB(server = 'synonym.caltech.edu', port = '9988', username = 'mjg', password = 'casicsfun')
    github_db = casicsdb.open('github')
    # Get repos
    allrepos = github_db.repos
    # Get repos with LCSH annotations
    repos = allrepos.find({'topics.lcsh': {'$ne': []}})

    # Parse text per repo to create feature vectors
    ids, docs, labels = get_text(repos)
    docs_preprocess = map(lambda doc: preprocess(doc), docs) # stemming string
    tfidf_matrix = tfidf_vectorizer(docs_preprocess) # convert to td-idf matrix
    svd_vect = svd_vectorizer(tfidf_matrix, n_components = 200, n_iter = 150) # reduce dimeensions

    return ids, svd_vect, labels
    
    
def get_text(repos):
    ''' Construct vectors of text per repo '''
    text = []
    labels = []
    ids = []
    for repo in repos:
        descrip = ''
        readme = ''
        ids.append(repo['id_'])
        if repo['description']: descrip = repo['description']
        if repo['readme'] and repo['readme'] != -1:
            readme = repo['readme'] # bytes object
        if len(descrip) + len(readme) > 0:
            text.append(descrip + " " + str(readme))
            labels.append(repo['topics']['lcsh'])
    return ids, text, labels


# Quick test interface.
# .............................................................................

if __name__ == '__main__':
    import pprint
    msg(pprint.pprint(file_elements(sys.argv[1])))
