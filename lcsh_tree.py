# Code to generate lcsh DAG
from pymongo import MongoClient
import igraph

db = MongoClient(tz_aware = True, connect = True)
lcsh_db = db['lcsh-db']
lcsh = lcsh_db.terms

def knownTerm(term, graph):
  knownTerm = True
  try:
    graph.vs.find(term)
  except:
    knownTerm = False
  return knownTerm


def processEntry(term, graph):
  entry = lcsh.find_one({'_id': term})
  broader = entry['broader']
  for parent in broader:
    if not knownTerm(parent, graph):
      graph.add_vertex(parent)
      processEntry(parent, graph) # go up as far as it can
    graph.add_edge(parent, term)


terms = []
for line in open('lcsh_topics.dat'):
  terms.append(line.strip())

g = igraph.Graph(directed = True)

for term in terms:
  if not knownTerm(term, g):
    g.add_vertex(term)
    processEntry(term, g)

g.write_graphml("lcsh.graphml")
