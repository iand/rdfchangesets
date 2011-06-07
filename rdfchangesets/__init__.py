__all__ = ["BatchChangeSet", "ChangeSet"]

from rdflib.graph import Graph
from rdflib.namespace import Namespace
from rdflib.term import URIRef, Literal, BNode
from rdflib.parser import StringInputSource
import time
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
CS = Namespace("http://purl.org/vocab/changeset/schema#")

class ChangeSet(Graph):
  def __init__(self, subjectOfChange):
    s = super(ChangeSet, self)
    s.__init__()
    self._add = s.add
    self.subjectOfChange = subjectOfChange
    self.subj = BNode()
    self.bind("rdf", RDF)
    self.bind("cs", CS)
    self._add((self.subj, RDF.type, CS.ChangeSet))
    self._add((self.subj, CS.createdDate, Literal(time.strftime('%Y-%m-%dT%H:%M:%SZ'))))
    self._add((self.subj, CS.subjectOfChange, subjectOfChange))
  
  def setCreatorName(self, creatorName):
    self._add((self.subj, CS.creatorName, Literal(creatorName)))
  
  def setChangeReason(self, changeReason):
    self._add((self.subj, CS.changeReason, Literal(changeReason)))
  
  def add(self, pred, obj):
    stmt = BNode()
    self._add((self.subj, CS.addition, stmt))
    self._add((stmt, RDF.type, RDF.Statement))
    self._add((stmt, RDF.subject, self.subjectOfChange))
    self._add((stmt, RDF.predicate, pred))
    self._add((stmt, RDF.object, obj))
    return stmt
  
  def remove(self, pred, obj):
    stmt = BNode()
    self._add((self.subj, CS.removal, stmt))
    self._add((stmt, RDF.type, RDF.Statement))
    self._add((stmt, RDF.subject, self.subjectOfChange))
    self._add((stmt, RDF.predicate, pred))
    self._add((stmt, RDF.object, obj))
    return stmt

  def getGraph(self):
    return self

class BatchChangeSet(object):
  def __init__(self):
    self.changesets = {}
    self.creatorName = ""
    self.changeReason = ""
  
  def setCreatorName(self, creatorName):
    self.creatorName = creatorName
  
  def setChangeReason(self, changeReason):
    self.changeReason = changeReason
  
  def add(self, s, p, o):
    if s not in self.changesets:
      cs = ChangeSet(s)
      cs.setCreatorName(self.creatorName)
      cs.setChangeReason(self.changeReason)
      self.changesets[s] = cs
    return self.changesets[s].add(p, o)
  
  def remove(self, s, p, o):
    if s not in self.changesets:
      cs = ChangeSet(s)
      cs.setCreatorName(self.creatorName)
      cs.setChangeReason(self.changeReason)
      self.changesets[s] = cs
    return self.changesets[s].remove(p, o)
  
  def getGraph(self):
    g = Graph()
    g.bind("rdf", RDF)
    g.bind("cs", CS)
    for cs in self.changesets.values():
      g += cs
    return g
  
  def graphs(self):
    for cs in self.changesets.values():
      yield cs

  def diff(self, old, new, prop_whitelist = [], prop_blacklist = []):
    has_changes = False
    for (s,p,o) in old.triples((None, None, None)):
      if str(p) not in prop_blacklist and (len(prop_whitelist) == 0 or str(p) in prop_whitelist):
        if ((s,p,o) not in new):
          self.remove(s, p, o)
          has_changes = True
    
    for (s,p,o) in new.triples((None, None, None)):
      if str(p) not in prop_blacklist and (len(prop_whitelist) == 0 or str(p) in prop_whitelist):
        if ((s,p,o) not in old):
          self.add(s, p, o)
          has_changes = True

    return has_changes
