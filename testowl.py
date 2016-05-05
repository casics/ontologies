from rdflib import *
from rdflib.namespace import NamespaceManager
from rdflib.extras.infixowl import *

casNs = Namespace('http://casics.org/ont/')
swoNs = Namespace('http://www.ebi.ac.uk/efo/swo/')
dcatNs = Namespace('http://www.w3.org/ns/dcat/')

namespace_manager = NamespaceManager(Graph())
namespace_manager.bind('owl', OWL_NS, override = False)
namespace_manager.bind('swo', swoNs, override = False)
namespace_manager.bind('cas', casNs, override = False)
namespace_manager.bind('dcat', dcatNs, override = False)
g = Graph()
g.namespace_manager = namespace_manager

uri = URIRef(casNs + "name")
c = Class(uri, graph = g)
c.subClassOf = [swoNs.software]

uri = URIRef(swoNs + 'has website homepage')
Property(uri, graph = g) | value | Literal("http://github.com/test")
uri = URIRef(swoNs + 'has download location')
Property(uri, graph = g) | value | Literal("http://github.com/test")
uri = URIRef(swoNs + 'modified')
Property(uri, graph = g) | value | Literal("2016-02-22T09:30:15")
uri = URIRef(swoNs + 'has version')
Property(uri, graph = g) | value | Literal("1.0.1")
uri = URIRef(swoNs + 'preceded by')
Property(uri, graph = g) | value | Literal("1.0.0")
uri = URIRef(swoNs + 'has Topic')
topic = URIRef(casNs + 'topic')
Property(uri, graph = g) | some | Class(topic, graph = g)
uri = URIRef(swoNs + 'has function')
function = URIRef(casNs + 'function')
Property(uri, graph = g) | some | Class(function, graph = g)
uri = URIRef(swoNs + 'implements')
algorithm = URIRef(casNs + 'algorithm')
Property(uri, graph = g) | some | Class(algorithm, graph = g)
uri = URIRef(swoNs + 'uses platform')
Property(uri, graph = g) | some | Class(swoNs.Linux, graph = g)

#		'has specified data input' some 
#        	(data 
#            and ('has format specification' some 'some format')),
#        'has specified data output' some
#        	(data
#            and ('has format specification' some 'some format'))

inputuri = URIRef(swoNs + 'has specified data input')
outputuri = URIRef(swoNs + 'has specified data input')
specuri = URIRef(swoNs + 'has format specification')
x = Property(specuri, graph = g) | some | Class(swoNs.formatA, graph = g)
y = Property(specuri, graph = g) | some | Class(swoNs.formatB, graph = g)
data = Class(swoNs.data, graph = g)
propin = Property(inputuri, graph = g) | some | (data & x)
propout = Property(outputuri, graph = g) | some | (data & y)
#subClassOf[propin, propout]

uri = URIRef(swoNs + 'implements')
algorithm = URIRef(casNs + 'algorithm')
Property(uri, graph = g) | some | Class(algorithm, graph = g)

uri = URIRef(swoNs + 'has dependency')
Property(uri, graph = g) | some | Class(swoNs.software, graph = g)
uri = URIRef(swoNs + 'has source')
Property(uri, graph = g) | value | Literal("true")
uri = URIRef(swoNs + 'has license')
license = URIRef(swoNs + 'CC By 2.0')
Property(uri, graph = g) | some | Class(license, graph = g)



#print(g.serialize(format='pretty-xml'))
print(g.serialize(format='nt'))

