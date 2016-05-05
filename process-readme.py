#!/usr/bin/env python3.4
#
# @file	   process-readme.py
# @brief   Process README and description texts (based on science concierge)
# @author  Matthew Graham
#
# <!---------------------------------------------------------------------------
# Copyright (C) 2016 by the California Institute of Technology.
# This software is part of CASICS, the Comprehensive and Automated Software
# Inventory Creation System.  For more information, visit http://casics.org.
# ------------------------------------------------------------------------- -->

import plac
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('/Users/mjg/Projects/casics/casics/src')
# sys.path.append('/home/mjg/code/casics/src/')
import casics
import re
import string
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import WhitespaceTokenizer
from unidecode import unidecode
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import TSNE
import pandas as pd
import matplotlib.pyplot as plt
from bhtsne import bh_tsne
from time import time

if __name__ == '__main__' and __package__ is None:
    sys.path.append(os.path.join(os.path.dirname(__file__), "../database"))
    from casicsdb import *

# Globals
# .............................................................................

stemmer = PorterStemmer()
w_tokenizer = WhitespaceTokenizer()
punct_re = re.compile('[{}]'.format(re.escape(string.punctuation)))

# Main body.
# .............................................................................

def main():
    docs = get_text() # list of READMEs and descriptions
    docs_preprocess = map(lambda doc: preprocess(doc), docs) # stemming string
    tfidf_matrix = tfidf_vectorizer(docs_preprocess) # convert to tf-idf matrix
    svd_vect = svd_vectorizer(tfidf_matrix, n_components=200, n_iter=150) # reduce dimensions
    # Run t-distributed Stochastic Neighbor Embedding (t-SNE; Barnes-Hut implementation)
    # Timings: sklearn - 1k: 15.9195120335, 2k - 41.7645118237, 4k - 185.737361908
    #          t-sne - 1k: 15.7083182335, 2k - 38.8270409107, 4k - 78.0439789295
    embedded = []
    for res in bh_tsne(svd_vect, no_dims = 2, perplexity = 40, verbose = True):
        embedded.append(res)
    embedded = np.array(embedded)
    # We can use this as input to identify clusters of projects

    # Plot t-SNE
    fig, ax = plt.subplots(figsize=(10, 10))
    plt.setp(ax, xticks=(), yticks=())
    fig.subplots_adjust(left=0.0, bottom=0.0, right=1.0, top=0.9,
                wspace=0.0, hspace=0.0)
    ax.scatter(embedded[:, 0], embedded[:, 1], marker = 'x')
            #        c=newsgroups.target, marker="x")
            #    fig.savefig('tsne.pdf', format = 'pdf')
    plt.show()
    
# Helpers
# .............................................................................

def preprocess(text, stem=True):
    """
    Apply Snowball stemmer to string

    Parameters
    ----------
    text : input abstract of papers/posters string
    stem : apply stemmer if True, default True
    """
    text = unidecode(text).lower()
    text = punct_re.sub(' ', text) # remove punctuation
    if stem:
        text_new = [stemmer.stem(token) for token in w_tokenizer.tokenize(text)]
    else:
        text_new = w_tokenizer.tokenize(text)
    return ' '.join(text_new)


def tfidf_vectorizer(abstract_list, min_df=3, max_df=0.8,
                     ngram_range=(1, 2), return_model=False):
    """
    Transform list of abstracts to tf-idf matrix
    """
    tfidf_model = TfidfVectorizer(min_df=min_df, max_df=max_df, strip_accents='unicode',
                                  analyzer='word', token_pattern=r'\w{1,}', ngram_range=ngram_range,
                                  use_idf=True, smooth_idf=True, sublinear_tf=True, stop_words='english')
    tfidf_matrix = tfidf_model.fit_transform(abstract_list)
    if return_model:
        return tfidf_matrix, tfidf_model
    else:
        return tfidf_matrix


def svd_vectorizer(tfidf_matrix, n_components=400,
                   n_iter=150, return_model=False):
    """
    Apply dimensionality reduction using truncated SVD or Latent Semantic Analysis (LSA) to tfidf matrix
    """
    svd_model = TruncatedSVD(n_components=n_components, n_iter=n_iter, algorithm='arpack')
    text_vect = svd_model.fit_transform(tfidf_matrix)
    if return_model:
        return text_vect, svd_model
    else:
        return text_vect


def get_text():
    text = []
    for line in open("docs_4k.dat"):
        text.append(line)
    return text


def get_text_mongo(limit = 1000):
    """
    Retrieve the descriptions and READMEs from the db
    """
    text = []
    connection = CasicsDB(server = 'hyponym.caltech.edu', port = '9988',
                          login = 'mjg', password = 'casicsfun')
    github_db = connection.open('github')
    repos = github_db.repos

    count = 0
    for repo in repos.find():
        if count > limit: break
        descrip = ''
        readme = ''
        if repo['description']:
            if len(repo['description'].split()) < 200:  descrip = repo['description']
        if repo['readme'] and repo['readme'] != -1:
            readme = repo['readme']
        if len(descrip) + len(readme) > 0:
            text.append(descrip + " " + readme)
            count += 1
    casicsdb.close()
    return text


# Plac annotations for main function arguments
# .............................................................................
# Argument annotations are: (help, kind, abbrev, type, choices, metavar)
# Plac automatically adds a -h argument for help, so no need to do it here.

main.__annotations__ = dict(
    file           = ('file containing repository identifiers', 'option', 'f'),
    id             = ('comma-separated list of repository ids', 'option', 'i'),
)


# Entry point
# .............................................................................

def cli_main():
    plac.call(main)

cli_main()
