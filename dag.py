#!/usr/bin/env python3.4
#
# @file     dag.py
# @brief    A directed acyclic graph representation of a concept scheme
# @author   Matthew Graham
#
# <!---------------------------------------------------------------------------
# Copyright (C) 2017 by the California Institute of Technology.
# This software is part of CASICS, the Comprehensive and Automated Software
# Inventory Creation System.  For more information, visit http://casics.org.
# ------------------------------------------------------------------------- -->

import numpy as np
import json
from igraph import Graph

import sys
import os

# Main body.
# .............................................................................

class DAG(object):
    '''Implements a concept scheme as a directed acyclic graph'''

    def __init__(self, file):
        if file.endswith(".json"):
            self.dag = load_from_json(file)
        elif file.endswith(".graphml"):
            self.dag = load_from_graphml(file)
      

    def non_leaf_nodes(self):
        ''' Returns a list of the non-leaf nodes in the DAG '''
        nodes = self.dag.vs.select(_degree_gt = 1)['name']
        return nodes


    def get_parents(self, node):
        ''' Return the parents of the specified node in the DAG '''
        parents = []
        for p in self.dag.vs.find(node).predecessors():
            parents.append(p['name'])
        return parents


    def get_children(self, node):
        ''' Return the children of the specified node in the DAG '''
        children = []
        for s in self.dag.vs.find(node).successors():
            children.append(s['name'])
        return children


    def remove(self, node):
        ''' Remove the specified nodes and its descendants from the DAG '''
        self.dag.vs.remove(node)
          
          
# Helpers
# .............................................................................
def load_from_json(filename):
    '''Load a JSON representation of a concept scheme'''
    # Load JSON representation to dict
    dic = json.load(open(filename))
    root = dic.keys()[0]
    # Parse dict
    g = Graph(directed = True)
    g.add_vertex(root) # Root node
    parse_dict(dic[root], root, g)
    return g


def parse_dict(children, parent, g):
    '''Parse a dictionary and recursive call if not leaf node'''
    for child in children.keys():
        print "%s: %s -> %s" % (child, parent, child)
        g.add_vertex(child)
        g.add_edge(parent, child)
        if isinstance(children[child], dict):
            parse_dict(children[child], child, g)
        elif isinstance(children[child], list):
            for item in children[child]:
                g.add_vertex(item)
                g.add_edge(child, item) 


def load_from_graphml(filename):
    '''Load a GraphML representation of a concept scheme'''
    g = Graph.Read_GraphML(filename)
    return g
