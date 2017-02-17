#!/usr/bin/env python3.4
#
# @file     cde.py
# @brief    Chained path evaluation
# @author   Matthew Graham
#
# <!---------------------------------------------------------------------------
# Copyright (C) 2017 by the California Institute of Technology.
# This software is part of CASICS, the Comprehensive and Automated Software
# Inventory Creation System.  For more information, visit http://casics.org.
# ------------------------------------------------------------------------- -->

import numpy as np
from sklearn.ensemble import RandomForestClassifier
import dag

import sys
import os

sys.path.append('/Users/mjg/Projects/casics/casics/src')
import casics

if __name__ == '__main__' and __package__ is None:
    sys.path.append(os.path.join(os.path.dirname(__file__), "../database"))
    from casicsdb import *

# Main body.
# .............................................................................

class CDE(object):
    '''Implements chained path evaluation'''
    
    def __init__(self, concept):
    '''
    Initialize a CDE based on the specified concept scheme.

    Parameters
    ----------
    concept : the concept scheme to use with this CDE (represented as a DAG)
    '''
        self.concept = concept
        self.clf = {}

        
    def fit(self, X, y):
    '''
    Build a CDE from the training set (X, y).

    Parameters
    ----------
    X : array-like of shape = [n_samples, n_features]
        The training input samples.

    y : array-like, shape = [n_samples]
        The target values (class labels).

    Returns
    -------
    self : object
        Returns self.
    '''
    unknown = -1 # unknown class label

    # Extend feature space to include parent class feature
    newX = np.zeros([X.shape[0], X.shape[1] + 1])
    newX[:, :-1] = X
        
    # Train a classifier for each non-leaf node in the concept hierarchy
    # assume nodes returned in topological order (?)
    # Do we need to infer all classes for instances?
    for node in self.concept.non_leaf_nodes():
        # Define base classifier
        self.clf[node] = RandomForestClassifier(n_estimators = 10)

        # Define classes
        labels = []
        for child in self.concept.get_children(node):
            labels.append(child.label)

        # Define training set
        X_pos = []
        y_pos = []
        for i in labels:
            X_pos.append(X[y == i]) # this probably needs to be multi-d
            y_pos.append(np.ones(len(X[y == i])) * i) 
            # Set parent class feature = 1
            ...

        X_neg = []
        y_neg = []
        siblings = []
        # Get siblings of node
        for parent in self.concept.get_parents(node):
            siblings.append(self.concept.get_children(parent))
        # If no siblings, get uncles
        if len(sibling) == 0:
            for parent in self.concept.get_parents(node):
                for gparent in self.concept.get_parents(parent):
                    siblings.append(self.concept.get_children(gparent))
        # Does this get all instances under the siblings or just direct children?
        # Let's assume direct children only for the moment
        for sibling in siblings:            
            X_neg.append(X[y == sibling.label]) # this probably needs to be multi-d
            y_neg.append(unknown)

        # Undersample negative set to create a balanced training set
        num = np.array([len(np.where(y_pos == i)[0]) for i in np.unique(y_pos)]).mean()
        num = np.rint(num)
        X_neg = np.random.choice(X_neg, num)
        y_neg = y_neg[:num]

        # Final training set for this node
        X = np.concatenate([X_pos, X_neg])
        y = np.concatenate([y_pos, y_neg])
        
        self.clf[node].fit(X, y)    

        
    def predict(self, X):
    '''
    Predict class for X.
    '''
        # Prune
        tree = self.concept.copy()
        root = tree.get_root()
        prune(X, root, tree)
        
        # Merge
        pass


    def prune(self, X, node, tree):
    '''
    Prune the tree
    '''
        total_confidence = 0.
        max_confidence = 0.
        for child in tree.get_children(node):
            y = self.clf[node].predict_proba(X)
            total_confidence += y
            if y < max_confidence: max_confidence = y

        unknown = 1. - total_confidence
        if max_confidence > unknown:
            for child in tree.get_children(node):
                self.prune(X, child, tree)
        else:
            tree.remove(node)
