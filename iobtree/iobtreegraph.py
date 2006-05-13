# Copyright (c) 2004-2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# - Anahide Tchertchian <at@nuxeo.com>
# - M.-A. Darche
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
#-------------------------------------------------------------------------------
# $Id$
#-------------------------------------------------------------------------------
"""Graph using IOBtree objects to store relations between integers
"""

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo

from zope.interface import implements

from Products.CMFCore.permissions import ManagePortal, View
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.PortalFolder import PortalFolder

from Products.CPSRelation.interfaces import IGraph
from Products.CPSRelation.interfaces import IPrefixedResource
from Products.CPSRelation.statement import Statement
from Products.CPSRelation.iobtree.iobtreerelation import IOBTreeRelation
from Products.CPSRelation.graphregistry import GraphRegistry
from Products.CPSRelation.graphdrawer import GraphDrawer

class IOBTreeGraph(UniqueObject, PortalFolder):
    """Graph using IOBtree objects to store relations between integers
    """

    meta_type = 'IOBTree Graph'

    implements(IGraph)

    security = ClassSecurityInfo()

    _properties = ()

    def __init__(self, id):
        """Initialization
        """
        self.id = id

    #
    # Relation types management
    #

    security.declarePrivate('_getRelations')
    def _getRelations(self):
        """Get the relations declared in the relations tool
        """
        return self.objectValues()

    security.declarePrivate('_getRelation')
    def _getRelation(self, id):
        """Get a relation held in the relations tool.
        """
        try:
            relation = self._getOb(id)
        except AttributeError:
            raise AttributeError("Relation '%s' does not exist" %id)
        else:
            return relation

    security.declareProtected(ManagePortal, 'listRelationIds')
    def listRelationIds(self):
        """Get the relation ids
        """
        return self.objectIds()

    security.declareProtected(ManagePortal, 'deleteAllRelations')
    def deleteAllRelations(self):
        """Delete all relations.
        """
        for id in self.listRelationIds():
            self.deleteRelation(id)

    security.declareProtected(ManagePortal, 'hasRelation')
    def hasRelation(self, id):
        """Does the tool have a relation for the given id?
        """
        relations = self.listRelationIds()
        if id in relations:
            return 1
        else:
            return 0

    security.declareProtected(ManagePortal, 'addRelation')
    def addRelation(self, id, prefix='', subject_prefix='', object_prefix=''):
        """Add a relation to the relations tool
        """
        if self.hasRelation(id):
            raise ValueError("The id '%s' is invalid - it is already in use"%id)
        else:
            relation = IOBTreeRelation(id=id,
                                       prefix=prefix,
                                       subject_prefix=subject_prefix,
                                       object_prefix=object_prefix)
            # FIXME: there's a 'title' attribute in the acquisition path
            # preventing to add a relation with a 'title' id...
            id = self._setObject(id, relation)
            return self._getOb(id)


    security.declareProtected(ManagePortal, 'deleteRelation')
    def deleteRelation(self, id):
        """Delete a relation from the relations tool
        """
        if self.hasRelation(id):
            self._delObject(id)

    #
    # relation instances
    #

    security.declarePrivate('_getIOBTreeRelation')
    def _getIOBTreeRelation(self, resource, default=None):
        """Get an IIOBtreeRelation from an IResource
        """
        if not IPrefixedResource.providedBy(resource):
            relation_id = resource.uri
        else:
            # ignore the prefix
            relation_id = resource.localname
        # XXX see if IOBTree relation prefix needs to be checked if resource is
        # prefixed
        return self._getOb(relation_id, default)


    security.declarePrivate('_getIOBTreeStatementsStructure')
    def _getIOBTreeStatementsStructure(self, statements):
        """Get an IOBtree statement structure from an IStatement

        Result is a dictionnary with IOBTreeRelation instances as keys and
        lists of (IResource, INode) tuples as values.
        """
        res = {}
        for statement in statements:
            predicate = self._getIOBTreeRelation(statement.predicate)
            if predicate is not None:
                # ignore not found predicate
                if res.has_key(predicate):
                    related = res[predicate]
                    related.append((statement.subject, statement.object))
                    res[predicate] = related
                else:
                    res[predicate] = [(statement.subject, statement.object)]
        return res


    security.declareProtected(View, 'add')
    def add(self, statements):
        """Add given list of IStatement objects to the graph
        """
        # sort statements by predicate
        structure = self._getIOBTreeStatementsStructure(statements)
        for iobtreerelation, tuples in structure.items():
            iobtreerelation.add(tuples)


    security.declareProtected(View, 'remove')
    def remove(self, statements):
        """Remove given list of IStatement objects from the graph
        """
        # sort statements by predicate
        structure = self._getIOBTreeStatementsStructure(statements)
        for iobtreerelation, tuples in structure.items():
            iobtreerelation.remove(tuples)


    security.declareProtected(View, 'getStatements')
    def getStatements(self, statement=None):
        """Return all IStatement objects matching the pattern

        If statement is None, return all statements.
        statement can use None nodes as wild cards.
        """
        res = []
        if statement is None:
            statement = Statement(None, None, None)
        if statement.predicate is None:
            for relation in self._getRelations():
                statements = relation.getStatements(statement.subject,
                                                    statement.object)
                res.extend(statements)
        else:
            relation = self._getIOBTreeRelation(statement.predicate)
            if relation is not None:
                res = relation.getStatements(statement.subject,
                                             statement.object)
        return res


    security.declareProtected(View, 'getSubjects')
    def getSubjects(self, predicate, object):
        """Get items matching the IStatement(None, predicate, object)
        """
        res = []
        relation = self._getIOBTreeRelation(predicate)
        if relation is not None:
            res = relation.getSubjects(object)
        return res


    security.declareProtected(View, 'getPredicates')
    def getPredicates(self, subject, object):
        """Get items matching the IStatement(subject, None, object)
        """
        res = []
        for relation in self._getRelations():
            if relation.hasTuple(subject, object):
                res.append(relation._getCPSRelation())
        return res


    security.declareProtected(View, 'getObjects')
    def getObjects(self, subject, predicate):
        """Get items matching the IStatement(subject, predicate, None)
        """
        res = []
        relation = self._getIOBTreeRelation(predicate)
        if relation is not None:
            res = relation.getObjects(subject)
        return res


    security.declareProtected(View, '__contains__')
    def __contains__(self, statement):
        """Return True if given IStatement is in the graph

        statement can use None nodes as wild cards.
        """
        res = False
        if statement.predicate is None:
            for relation in self._getRelations():
                if relation.hasTuple(statement.subject, statement.object):
                    res = True
                    break
        else:
            relation = self._getIOBTreeRelation(statement.predicate)
            if relation is not None:
                res = relation.hasTuple(statement.subject, statement.object)
        return res


    security.declareProtected(View, 'containsResource')
    def containsResource(self, node):
        """Return True if given node appears in any statement of the graph.
        """
        # XXX no direct API to do that...
        # XXX AT: strange acquisition problem: the graph __contains__ method is
        # not found
        from Acquisition import aq_base
        base_graph = aq_base(self)
        try:
            if Statement(node, None, None) in base_graph:
                return True
            if Statement(None, node, None) in base_graph:
                return True
            if Statement(None, None, node) in base_graph:
                return True
        except (ValueError, KeyError):
            # avoid invalid node problem
            pass
        return False


    security.declareProtected(View, 'clear')
    def clear(self):
        """Clear the graph, removing all statements in it
        """
        for relation in self._getRelations():
            relation.clear()


    security.declareProtected(View, '__len__')
    def __len__(self):
        """Return the number of statements in the graph
        """
        length = 0
        for relation in self._getRelations():
            length += len(relation)
        return length


    def __nonzero__(self):
        return True


    security.declareProtected(ManagePortal, 'read')
    def query(self, query_string, language, base_uri=None):
        """Query the graph, return an IQueryResult

        language is the query language (sparql, rdql...)
        """
        raise NotImplementedError


    security.declareProtected(ManagePortal, 'read')
    def read(self, source, base=None, format="application/rdf+xml"):
        """Parse source into Graph.

        Returns boolean: success or failure.

        source can either be a string, location, stream instance.
        base specifies the logical URI to use in case it differs from the
        physical source URI.
        format defaults to xml (AKA rdf/xml).
        """
        raise NotImplementedError


    security.declareProtected(View, 'write')
    def write(self, destination=None, base=None, format="application/rdf+xml"):
        """Serialize graph to destination

        If destination is None then serialization is returned as a string.
        base specifies the logical URI to use in case it differs from the
        physical source URI.
        format defaults to xml (AKA rdf/xml).
        """
        raise NotImplementedError


    security.declareProtected(View, 'getDrawing')
    def getDrawing(self):
        """Get drawing for this graph
        """
        drawer = GraphDrawer(self)
        ok, res = drawer.getDrawing()
        return ok, res

    #
    # ZMI
    #

    manage_options = (
        {'label': "Relations",
         'action': 'manage_editRelations'
         },
        {'label': "Drawing",
         'action': 'manage_drawing'
         },
        {'label': "Overview",
         'action': 'overview'
         },
        ) + PortalFolder.manage_options[3:-2]


    security.declareProtected(ManagePortal, 'manage_editRelations')
    manage_editRelations = DTMLFile('../zmi/iobtreegraph_content', globals())
    manage_main = manage_editRelations

    security.declareProtected(ManagePortal, 'manage_drawing')
    manage_drawing = DTMLFile('../zmi/graph_drawing', globals())

    security.declareProtected(ManagePortal, 'overview')
    overview = DTMLFile('../zmi/iobtreegraph_overview', globals())

    security.declareProtected(ManagePortal, 'manage_addRelation')
    def manage_addRelation(self, id, prefix='', subject_prefix='',
                           object_prefix='', REQUEST=None):
        """Add a relation TTW."""
        relation = self.addRelation(id, prefix, subject_prefix, object_prefix)
        if REQUEST:
            REQUEST.RESPONSE.redirect(
                self.absolute_url()+'/manage_editRelations'
                '?manage_tabs_message=Added.')
        else:
            return relation

    security.declareProtected(ManagePortal, 'manage_delRelations')
    def manage_delRelations(self, ids, REQUEST=None):
        """Delete relations TTW."""
        for id in ids:
            self.deleteRelation(id)
        if REQUEST:
            REQUEST.RESPONSE.redirect(
                self.absolute_url()+'/manage_editRelations'
                '?manage_tabs_message=Deleted.')

    security.declareProtected(ManagePortal, 'manage_delAllRelations')
    def manage_delAllRelations(self, REQUEST=None):
        """Delete all relations TTW."""
        self.deleteAllRelations()
        if REQUEST:
            REQUEST.RESPONSE.redirect(
                self.absolute_url()+'/manage_editRelations'
                '?manage_tabs_message=Deleted.')


InitializeClass(IOBTreeGraph)

# Register to the graph registry
GraphRegistry.register(IOBTreeGraph)
