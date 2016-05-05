# Code to parse LOC subject structure
from rdflib import Graph, ConjunctiveGraph, URIRef, RDFS, Literal
from rdflib.namespace import RDF, SKOS

#g = ConjunctiveGraph()
#g.load('subjects-skos-20140306.rdf')
#g.load('test.rdf')

g = Graph("Sleepycat")
graph.open("store", create = True)
graph.parse("subjects-skos-20140306.rdf")

for s, p, o in g:
  print '%s "%s"' % (s, g.preferredLabel(s)[0][1])

  #for s, o in g.predicates():
