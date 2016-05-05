#!/usr/bin/env python3.4
#
# @file	   convert-owl.py
# @brief   Convert RepoData to OWL format
# @author  Matthew Graham
#
# <!---------------------------------------------------------------------------
# Copyright (C) 2016 by the California Institute of Technology.
# This software is part of CASICS, the Comprehensive and Automated Software
# Inventory Creation System.  For more information, visit http://casics.org.
# ------------------------------------------------------------------------- -->

from rdflib import *
from rdflib.namespace import NamespaceManager
from rdflib.extras.infixowl import *
import urllib
import plac
import sys
sys.path.append('/casics/src')
import casics

if __name__ == '__main__' and __package__ is None:
    sys.path.append(os.path.join(os.path.dirname(__file__), "../common"))
    from utils import *
    from reporecord import *
    from dbinterface import *


# Globals
# .............................................................................
casNs = Namespace('http://casics.org/ont/')
swoNs = Namespace('http://www.ebi.ac.uk/efo/swo/')
dcatNs = Namespace('http://www.w3.org/ns/dcat/')


# Main body.
# .............................................................................

def main(id = None):
    '''Convert RepoData entries in the database to OWL classes'''
    database = casics.Database()
    db = database.open()
    keys = id is None and db.keys() else id.split(",")
    for key in keys()
        entry = db[key]
        owl = convert(entry)
        store(owl)
    db.close()
    # close RDF store?


def convert(entry):
    ''' Create the OWL 2 representation of the RepoData entry '''
    # Class
    g = get_graph()
    a = get_class(casNs, entry.name, g)
    subClasses = [swoNs.software]
    # 'categories', 'copy_of', 'created', 'deleted', 'description', 'host', 'id', 'languages', 'name', 'owner', 'owner_type', 'readme', 'refreshed', 'topics']
    # URL
    prop = get_property(swoNs, 'has website homepage', 'https://github.com/%s/%s' % (entry.owner, entry.name), g)
    subClasses.append(prop)
    prop = get_property(dcat, 'has download location', '', g)
    subClasses.append(prop)
    # How recently updated
    prop = get_property(swoNs, 'modified', '', g)
    subClasses.append(prop)
    prop = get_property(swoNs, 'has version', '', g)
    subClasses.append(prop)
    prop = get_property(swoNs, 'preceded by', '', g)
    subClasses.append(prop)
    # Domain/subject/field of application
    for topic in entry.topics:
      topicClass = get_class(casNs, topic, g)
      prop = get_property(swoNs, 'has topic', topicClass, g)
      subClasses.append(prop)
    # Purpose of software
    # function
    for algorithm in get_algorithms(entry):
      algClass = get_class(casNs, alogrithm, g)
      prop = get_property(swoNs, 'implements', algClass, g)  
      subClasses.append(prop)
    # Operating systems supported
    prop = get_property(swoNs, 'uses platform', '', g)
    # Data formats supported
    dataClass = get_class(swoNs, 'data', g)
    inputuri = URIRef(swoNs + 'has specified data input')
    outputuri = URIRef(swoNs + 'has specified data input')
    specuri = URIRef(swoNs + 'has format specification')
    for format in get_formats(entry):
        formatClass = get_class(swoNs, format, g)
        x = Property(specuri, graph = g) | some | formatClass
        propin = Property(inputuri, graph = g) | some | (data & x)
        propout = Property(outputuri, graph = g) | some | (data & x)
        subClasses.append(propin, propout)
    # Software libraries needed
        
    # Source code availability
        
    # License terms of software
    for license in get_licenses(entry):
        licenseClass = get_class(swoNs, license, g)
        prop = get_property(swoNs, 'has license', licenseClass, g)
        subClasses.append(prop)

    g.subClassof = subClasses
    return g


def store(owl):
    print g.serialize()
    # rdfstore.add(owl)
 
# Helpers
# .............................................................................

def get_graph():
    namespace_manager = NamespaceManager(Graph())
    namespace_manager.bind('owl', OWL_NS, override = False)
    namespace_manager.bind('swo', swoNs, override = False)
    namespace_manager.bind('cas', casNs, override = False)
    namespace_manager.bind('dcat', dcatNs, override = False)
    g = Graph()
    g.namespace_manager = namespace_manager
    return g


def get_class(namespace, name, graph):
    uri = URIRef(namespace + name)
    c = Class(uri, graph = graph)
    return c


def get_property(namespace, property, predicate, graph):
    urllib.parse.quote_plus(namespace + property)
    uri = URIRef()
    if isinstance(predicate, Literal):
        p = Property(uri, graph = graph) | value | predicate
    elif isinstance(predicate, Class):
        p = Property(uri, graph = graph) | some | predicate
    return p


def get_algorithms(entry):
    pass


def get_formats(entry):
    pass

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
