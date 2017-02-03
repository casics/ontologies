#!/usr/bin/env python3.4
#
# @file     similiarity.py
# @brief	Calculate semantic similarities
# @author 	Matthew Graham
#
# <!---------------------------------------------------------------------------
# Copyright (C) 2017 by the California Institute of Technology.
# This software is part of CASICS, the Comprehensive and Automated Software
# Inventory Creation System.  For more information, visit http://casics.org.
# ------------------------------------------------------------------------- -->

from anytree import Node, RenderTree
import json

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
    # Connect to db
    casicsdb = CasicsDB(server=server, port=port, username=user, password=password)
    github_db = casicsdb.open('github')
    # Get repos
    repos = github_db.repos
    # Get repos with LCSH annotations
    repos.find({'topics.lcsh': {'$ne': []}})
    


# Helpers
# .............................................................................
def load_tree_from_json(filename):
    '''Load a JSON representation of a concept scheme'''
    # Load JSON representation to dict
    dic = json.load(open(filename))
    # Parse dict
    idx = {}
    parse_dict(dic, None, idx)
    return idx


def parse_dict(parent, parent_node, node_index):
    '''Parse a dictionary and recursive call if not leaf node'''
    for child in parent.keys():
        child_node = Node(child, parent = parent_node)
        node_index[child] = child_node
        if isinstance(parent[child], dict):
            parse_dict(parent[child], child_node, node_index)
        elif isinstance(parent[child], list):
            for item in parent[child]:
                node = Node(item, parent = child_node)
                node_index[item] = node

                
def least_common_subsumer(term_a, term_b, index):
    '''Returns the most specific concept which is ancestor of both A and B'''
    node_a = index[term_a]
    node_b = index[term_b]
    if node_a.depth > node_b.depth:
        ref, test = node_a.anchestors, node_b.anchestors
    else:
        ref, test = node_b.anchestors, node_a.anchestors
    lcs = None
    for n in test:
        if n in ref: lcs = n
    return lcs


def shortest_path(term_a, term_b, index):
    '''Returns the shortest path between A and B via the least common subsumer'''
    n1 = index[term_a].depth
    n2 = index[term_b].depth
    lcs = least_common_subsumer(term_a, term_b, index).depth
    sp = (n1 - lcs) + (n2 - lcs)
    return sp
    

def wup_sim(term_a, term_b, idx):
    '''Wu and Palmer similarity'''
    n = least_common_subsumer(term_a, term_b, idx).depth
    n1 = idx[term_a].depth
    n2 = idx[term_b].depth
    sim = 2. * n  / (n1 + n2)
    return sim


                
# Quick test interface.
# .............................................................................

if __name__ == '__main__':
    import pprint
    msg(pprint.pprint(file_elements(sys.argv[1])))
