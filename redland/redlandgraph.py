# Copyright (c) 2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# - Anahide Tchertchian <at@nuxeo.com>
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
"""Graph using the Redland RDF Application Framework
"""

import RDF

# RDF patches

# see http://bugs.librdf.org/mantis/view.php?id=59
from RDF import QueryResults, Redland, Node

def make_results_hash(self):
    results = {}
    c = Redland.librdf_query_results_get_bindings_count(self._results)
    for i in range(c):
        n = Redland.librdf_query_results_get_binding_name(self._results, i)
        v = Redland.librdf_query_results_get_binding_value(self._results, i)
        if v is None:
            results[n] = None
        else:
            results[n] = Node(from_object=v)
    return results

QueryResults.make_results_hash = make_results_hash


# better representation for nodes, ok this is dummy but it helps
def __repr__(self):
    old_repr = object.__repr__(self)
    address = old_repr[len('<RDF.Node object at '):-1]
    return "<RDF.Node for %s at %s>" % (repr(self), address)

Node.__repr__ = __repr__

# End of RDF patches


import os
import os.path
import tempfile
import string
import logging
import sha

import zope.interface
import zope.component

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo

from Products.CMFCore.permissions import ManagePortal, View
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.PortalFolder import PortalFolder

# nodes
from Products.CPSRelation.interfaces import IResource
from Products.CPSRelation.interfaces import IPrefixedResource
from Products.CPSRelation.interfaces import IBlank
from Products.CPSRelation.interfaces import ILiteral
from Products.CPSRelation.interfaces import IStatementResource
from Products.CPSRelation.interfaces import IStatement
from Products.CPSRelation.resourceregistry import ResourceRegistry
from Products.CPSRelation.node import Resource
from Products.CPSRelation.node import PrefixedResource
from Products.CPSRelation.node import Literal
from Products.CPSRelation.node import Blank
from Products.CPSRelation.node import StatementResource
from Products.CPSRelation.statement import Statement

# graph
from Products.CPSRelation.redland.interfaces import IRedlandGraph
from Products.CPSRelation.graphregistry import GraphRegistry
from Products.CPSRelation.graphdrawer import GraphDrawer

# query
from Products.CPSRelation.query import QueryResult

from Products.CPSRelation.transactionmanager import get_relation_manager

#
# Graph
#

class RedlandGraph(UniqueObject, PortalFolder):
    """Graph using the Redland RDF Application Framework
    """
    meta_type = 'Redland Graph'

    zope.interface.implements(IRedlandGraph)

    security = ClassSecurityInfo()

    logger = logging.getLogger("CPSRelation.RedlandGraph")

    #
    # Properties
    #

    _properties = (
        {'id': 'synchronous', 'type': 'boolean', 'mode': 'w',
         'label': "Synchronous",
         },
        {'id': 'backend', 'type': 'selection', 'mode': 'w',
         'select_variable': 'supported_backends',
         'label': "Backend",
         },
        # one binding per line, following the format "key value", for instance:
        # rdf http://www.w3.org/1999/02/22-rdf-syntax-ns#
        # exp http://www.example.org/
        {'id': 'namespace_bindings', 'type': 'lines', 'mode': 'w',
         'label': "Namespace bindings",
         },
        # XXX
        # one binding per line, following the format "key adapter", for
        # instance:
        # rdf IResource
        # exp IVersionHistoryResource
        #{'id': 'adapter_bindings', 'type': 'lines', 'mode': 'w',
        # 'label': "Adapter bindings, defaults to IResource",
        # },
        # path is relative to the var directory of the Zope instance
        {'id': 'bdb_path', 'type': 'string', 'mode': 'w',
         'label': "Path towards bdb files (for bdb backend)",
         },
        # mysql options are like
        # host='localhost',port=3306,user='root',password='mypass'
        {'id': 'mysql_options', 'type': 'string', 'mode': 'w',
         'label': "mysql connection parameters (for mysql backend)"
         },
        # add optional mysql database name; defaults to the graph id
        {'id': 'mysql_database', 'type': 'string', 'mode': 'w',
         'label': "mysql database name (for mysql backend)"
         },
        )
    supported_backends = [
        'memory',
        'bdb',
        'mysql',
        ]
    # default values
    synchronous = True
    backend = 'memory'
    namespace_bindings = ()
    adapter_bindings = ()
    bdb_path = ''
    mysql_options = ''
    mysql_database = ''

    #
    # API
    #

    def __init__(self, id, backend='memory', namespace_bindings=(),
                 adapter_bindings=(), **kw):
        """Initialization

        kw are passed to be able to set the backend specific parameters
        """
        # check backend before init
        if backend not in self.supported_backends:
            raise ValueError("Backend %s not supported "
                             "for graph %s" %(backend, id))

        self.id = id
        self.backend = backend
        if backend == 'bdb':
            # path is the path towards the directory where BDB files will be
            # kept in the var directory of the Zope instance
            bdb_path = kw.get('bdb_path')
            if not bdb_path:
                raise ValueError("Graph %s cannot be created with bdb "
                                 "backend if no bdb_path is specified" %(id,))
            else:
                self.bdb_path = bdb_path
        elif backend == 'mysql':
            # options information
            mysql_options = kw.get('mysql_options')
            if not mysql_options:
                raise ValueError("Graph %s cannot be created with mysql "
                                 "backend if no mysql_options are specified"
                                 % (id,))
            else:
                self.mysql_options = mysql_options
        self.namespace_bindings = namespace_bindings
        self.synchronous = kw.get('synchronous', True)


    security.declarePrivate('_isSynchronous')
    def _isSynchronous(self):
        """Return True if graph is synchronous
        """
        return self.synchronous


    security.declarePrivate('_getGraph')
    def _getGraph(self):
        """Get the RDF graph
        """
        if self.backend == 'memory':
            storage = getattr(self, '_v_storage', None)
            if storage is None:
                # WARNING level because content can be lost with memory storage
                self.logger.warn("_getGraph: rebuilding memory storage")
                options = "new='yes',hash-type='memory',dir='.'"
                storage = RDF.Storage(storage_name="hashes",
                                      name=self.id,
                                      options_string=options)
                self._v_storage = storage
        elif self.backend == 'bdb':
            storage = getattr(self, '_v_storage', None)
            if storage is None:
                self.logger.debug("_getGraph: rebuilding bdb storage")
                # XXX AT: check behaviour with multiple access to BDB
                dir_path = os.path.join(CLIENT_HOME, self.bdb_path)
                storage = RDF.HashStorage(dir_path, options="hash-type='bdb'")
                self._v_storage = storage
        elif self.backend == 'mysql':
            storage = getattr(self, '_v_storage', None)
            database_id = self.mysql_database or self.id
            if storage is None:
                self.logger.debug("_getGraph: rebuilding mysql storage")
                options = self.mysql_options + ",database='%s'"%database_id
                try:
                    storage = RDF.Storage(storage_name="mysql",
                                          name=database_id,
                                          options_string=options)
                except Exception, err:
                    # XXX catching RDF.RedlandError is unefficient, because
                    # RedlandError raised in that case does not come from the
                    # Python binding but from C code, even if it has the same
                    # name.
                    if err.__class__.__name__ != 'RedlandError':
                        raise
                    else:
                        # Try to create table: adding the new option creates
                        # tables, but erases data if tables already exist,
                        # that's why it's done after a first try without it.
                        self.logger.debug("_getGraph: creating mysql tables")
                        options = "new='yes'," + options
                        storage = RDF.Storage(storage_name="mysql",
                                              name=database_id,
                                              options_string=options)
                self._v_storage = storage
        else:
            raise ValueError("Backend %s not supported "
                             "for graph %s" %(self.backend, self.id))

        graph = RDF.Model(storage)
        return graph


    security.declarePrivate('getNamespaceBindings')
    def getNamespaceBindings(self):
        """Get defined namespace bindings dictionnary
        """
        bindings_dict = {}
        for binding in self.namespace_bindings:
            sep_index = binding.find(' ')
            if sep_index != -1:
                key = binding[:sep_index]
                value = binding[sep_index+1:]
                bindings_dict[key] = value
        return bindings_dict


    security.declarePrivate('_getRedlandNode')
    def _getRedlandNode(self, node):
        """Get an RDF.Node object from an INode

        Change unicode values into utf-8 encoded values because Redland does
        not accept unicode.
        """
        if node is None:
            rnode = None
        elif IResource.providedBy(node):
            temp_node = None
            if IPrefixedResource.providedBy(node):
                ns_bindings = self.getNamespaceBindings()
                namespace = ns_bindings.get(node.prefix)
                if namespace is not None:
                    localname = node.localname
                    if isinstance(localname, unicode):
                        localname = localname.encode('utf-8', 'ignore')
                    temp_node = RDF.NS(namespace)[localname]
            if temp_node is None:
                # no namespace used
                uri = node.uri
                if isinstance(uri, unicode):
                    uri = uri.encode('utf-8', 'ignore')
                temp_node = RDF.Node(uri_string=uri)
            rnode = temp_node
        elif IBlank.providedBy(node):
            id = node.id
            if isinstance(id, unicode):
                id = id.encode('utf-8', 'ignore')
            rnode = RDF.Node(blank=id)
        elif ILiteral.providedBy(node):
            value = node.value
            if isinstance(value, unicode):
                value = value.encode('utf-8', 'ignore')
            if node.type:
                # typed literal
                rnode = RDF.Node(literal=value,
                                 datatype=RDF.Uri(node.type))
            else:
                # plain literal
                rnode = RDF.Node(literal=value,
                                 language=node.language)
        return rnode


    security.declarePrivate('_getCPSNode')
    def _getCPSNode(self, rnode):
        """Get an INode from a RDF.Node
        """
        if rnode is None:
            node = None
        elif rnode.is_resource():
            # Parse the uri using namespace bindings to get the best resource
            # implementation
            uri_string = str(rnode.uri)
            namespace_bindings = self.getNamespaceBindings()
            prefix = None
            localname = None
            for key, value in namespace_bindings.items():
                if uri_string.startswith(value):
                    prefix = key
                    localname = uri_string[len(value):]
                    break
            node = None
            if prefix and localname:
                try:
                    # XXX may not be the good keywords
                    node = ResourceRegistry.makeResource(
                        prefix, localname=localname)
                except KeyError:
                    # no factory registered for this prefix, default to
                    # PrefixedResource
                    node = PrefixedResource(prefix, localname)
            if node is None:
                node = Resource(uri_string)
        elif rnode.is_blank():
            node = Blank(rnode.blank_identifier)
        elif rnode.is_literal():
            literal_value = rnode.literal_value
            value = literal_value['string']
            # decode from Uri type
            dt_uri = literal_value['datatype']
            if dt_uri is not None:
                dt_uri = str(dt_uri)
            node = Literal(value=value,
                           language=literal_value['language'],
                           type=dt_uri)
        else:
            raise ValueError("Invalid RDF.Node object %s" % (rnode,))
        return node


    security.declarePrivate('_getRedlandStatement')
    def _getRedlandStatement(self, statement):
        """Get an RDF.Statement instance from an IStatement
        """
        rstatement = RDF.Statement(
            self._getRedlandNode(statement.subject),
            self._getRedlandNode(statement.predicate),
            self._getRedlandNode(statement.object))
        return rstatement


    security.declarePrivate('_getCPSStatement')
    def _getCPSStatement(self, rstatement):
        """Get an IStatement from a RDF.Statement
        """
        statement = Statement(
            self._getCPSNode(rstatement.subject),
            self._getCPSNode(rstatement.predicate),
            self._getCPSNode(rstatement.object))
        return statement


    security.declarePrivate('_add')
    def _add(self, statements):
        """Add given list of IStatement objects to the graph
        """
        rdf_graph = self._getGraph()
        for statement in statements:
            rstatement = self._getRedlandStatement(statement)
            rdf_graph.append(rstatement)


    security.declareProtected(View, 'add')
    def add(self, statements):
        """Add given list of IStatement objects to the graph

        Addition may be delayed to the end of the transaction if graph is
        asynchronous.
        """
        get_relation_manager().add(self, statements)


    security.declarePrivate('_remove')
    def _remove(self, statements):
        """Remove given list of IStatement objects from the graph
        """
        rdf_graph = self._getGraph()
        for statement in statements:
            rstatement = self._getRedlandStatement(statement)
            rdf_graph.remove_statement(rstatement)


    security.declareProtected(View, 'remove')
    def remove(self, statements):
        """Remove given list of IStatement objects from the graph

        Removal may be delayed to the end of the transaction if graph is
        asynchronous.
        """
        get_relation_manager().remove(self, statements)


    security.declareProtected(View, 'getStatements')
    def getStatements(self, statement=None):
        """Return all IStatement objects matching the pattern

        If statement is None, return all statements.
        statement can use None nodes as wild cards.
        """
        rdf_graph = self._getGraph()
        if statement is None:
            statement = Statement(None, None, None)
        rstatement = self._getRedlandStatement(statement)
        riterator = rdf_graph.find_statements(rstatement)
        res = []
        while not riterator.end():
            res.append(self._getCPSStatement(riterator.current()))
            riterator.next()
        return res


    security.declareProtected(View, 'getSubjects')
    def getSubjects(self, predicate, object):
        """Get items matching the IStatement(None, predicate, object)
        """
        rdf_graph = self._getGraph()
        rpredicate = self._getRedlandNode(predicate)
        robject = self._getRedlandNode(object)
        rsubjects = rdf_graph.get_sources(rpredicate, robject)
        subjects = [self._getCPSNode(x) for x in rsubjects]
        return subjects


    security.declareProtected(View, 'getPredicates')
    def getPredicates(self, subject, object):
        """Get items matching the IStatement(subject, None, object)
        """
        rdf_graph = self._getGraph()
        rsubject = self._getRedlandNode(subject)
        robject = self._getRedlandNode(object)
        rpredicates = rdf_graph.get_predicates(rsubject, robject)
        predicates = [self._getCPSNode(x) for x in rpredicates]
        return predicates


    security.declareProtected(View, 'getObjects')
    def getObjects(self, subject, predicate):
        """Get items matching the IStatement(subject, predicate, None)
        """
        rdf_graph = self._getGraph()
        rsubject = self._getRedlandNode(subject)
        rpredicate = self._getRedlandNode(predicate)
        robjects = rdf_graph.get_targets(rsubject, rpredicate)
        objects = [self._getCPSNode(x) for x in robjects]
        return objects


    security.declareProtected(View, 'hasStatement')
    def hasStatement(self, statement):
        """Return True if given IStatement is in the graph

        statement can use None nodes as wild cards.
        """
        rdf_graph = self._getGraph()
        res = False
        if not statement:
            # optim: is graph empty?
            if len(self) > 0:
                res = True
        elif (statement.subject is not None
              and statement.predicate is not None
              and statement.object is not None):
            rstatement = self._getRedlandStatement(statement)
            res = rstatement in rdf_graph
        else:
            if self.getStatements(statement):
                res = True
        return res


    security.declareProtected(View, 'hasResource')
    def hasResource(self, node):
        """Return True if given node appears in any statement of the graph.
        """
        # XXX no direct API to do that in Redland...
        if self.hasStatement(Statement(node, None, None)):
            return True
        if self.hasStatement(Statement(None, node, None)):
            return True
        if self.hasStatement(Statement(None, None, node)):
            return True
        return False


    security.declareProtected(View, 'clear')
    def clear(self):
        """Clear the graph, removing all statements in it
        """
        if self.backend == 'memory':
            self.logger.warn("_getGraph: recreating memory storage")
            options = "new='yes',hash-type='memory',dir='.'"
            storage = RDF.Storage(storage_name="hashes",
                                  name=self.id,
                                  options_string=options)
        elif self.backend == 'bdb':
            self.logger.debug("_getGraph: recreating bdb storage")
            dir_path = os.path.join(CLIENT_HOME, self.bdb_path)
            storage = RDF.HashStorage(dir_path,
                                      options="new='yes',hash-type='bdb'")
        elif self.backend == 'mysql':
            self.logger.debug("_getGraph: recreating mysql storage")
            options = self.mysql_options + "new='yes',database='%s'"%self.id
            storage = RDF.Storage(storage_name="mysql",
                                  name=self.id,
                                  options_string=options)
        else:
            raise ValueError("Backend %s not supported "
                             "for graph %s" %(self.backend, self.id))
        self._v_storage = storage


    security.declareProtected(View, '__len__')
    def __len__(self):
        """Return the number of statements in the graph
        """
        rdf_graph = self._getGraph()
        return rdf_graph.size()


    def __nonzero__(self):
        return True


    security.declareProtected(View, 'query')
    def query(self, query_string, language, base_uri=None):
        """Query the graph, return an IQueryResult

        language is the query language (sparql, rdql...)
        """
        rdf_graph = self._getGraph()
        if base_uri is not None:
            base_uri = RDF.Uri(base_uri)
        if isinstance(query_string, unicode):
            query_string = query_string.encode('utf-8', 'ignore')
        query = RDF.Query(query_string, base_uri=base_uri,
                          query_language=language)
        rresults = rdf_graph.execute(query)
        # make the conversion
        if rresults is None:
            results = QueryResult([], [], 0)
        else:
            rbindings = list(rresults)
            # XXX hack: no API in RDF to get the variable names...
            variable_names = rbindings and rbindings[0].keys() or []
            bindings = []
            for rbinding in rbindings:
                mapping = [(variable, self._getCPSNode(rnode))
                           for variable, rnode in rbinding.items()]
                bindings.append(dict(mapping))
            count = len(bindings)
            results = QueryResult(variable_names, bindings, count)
        return results


    security.declareProtected(ManagePortal, 'read')
    def read(self, source, base=None, format="application/rdf+xml"):
        """Parse source into Graph.

        Returns boolean: success or failure.

        source can either be a string, location, stream instance.
        base specifies the logical URI to use in case it differs from the
        physical source URI.
        format defaults to xml (AKA rdf/xml).
        """
        rdf_graph = self._getGraph()
        parser = RDF.Parser(mime_type=format)
        if isinstance(source, str) and source.startswith('file:'):
            res = parser.parse_into_model(rdf_graph, source,
                                          base_uri=RDF.Uri(base))
        else:
            # XXX AT: A base URI is required when parsing a string
            if base is None:
                base = RDF.Uri('xxx')
            res = parser.parse_string_into_model(rdf_graph, source,
                                                 base_uri=base)
        return res


    security.declareProtected(View, 'write')
    def write(self, destination=None, base=None, format="application/rdf+xml"):
        """Serialize graph to destination

        If destination is None then serialization is returned as a string.
        base specifies the logical URI to use in case it differs from the
        physical source URI.
        format defaults to xml (AKA rdf/xml).
        """
        rdf_graph = self._getGraph()
        serializer = RDF.Serializer(mime_type=format)
        namespace_bindings = self.getNamespaceBindings()
        for prefix, uri in namespace_bindings.items():
            # redland bug: rdf is a builtin namespace for serializers
            if prefix == 'rdf':
                continue
            serializer.set_namespace(prefix, uri)
        if destination is None:
            # XXX AT: serializing to string is costly for big graphs ; writing
            # to a file is more efficient
            #res = serializer.serialize_model_to_string(rdf_graph,
            #                                           base_uri=base)
            fd, file_path = tempfile.mkstemp('rdf')
            serializer.serialize_model_to_file(file_path, rdf_graph,
                                               base_uri=base)
            os.close(fd)
            f = open(file_path, 'r')
            res = f.read()
            f.flush()
            f.close()
            os.unlink(file_path)
        else:
            res = serializer.serialize_model_to_file(destination, rdf_graph,
                                                     base_uri=base)
        return res


    security.declareProtected(View, 'getDrawing')
    def getDrawing(self):
        """Get drawing for this graph
        """
        drawer = RedlandGraphDrawer(self)
        ok, res = drawer.getDrawing()
        return ok, res

    #
    # ZMI
    #

    manage_options = (PortalFolder.manage_options[2],) + (
        {'label': "Relations",
         'action': 'manage_editRelations'
         },
        {'label': "Drawing",
         'action': 'manage_drawing'
         },
        {'label': "Overview",
         'action': 'overview'
         },
        ) + PortalFolder.manage_options[3:]

    manage_workspace = PortalFolder.manage_propertiesForm
    manage_workspace._setName('manage_propertiesForm')

    security.declareProtected(ManagePortal, 'manage_editRelations')
    manage_editRelations = DTMLFile('../zmi/rdfgraph_content', globals())

    security.declareProtected(ManagePortal, 'manage_drawing')
    manage_drawing = DTMLFile('../zmi/graph_drawing', globals())

    security.declareProtected(ManagePortal, 'overview')
    overview = DTMLFile('../zmi/redlandgraph_overview', globals())

    security.declareProtected(ManagePortal, 'manage_deleteAllRelations')
    def manage_deleteAllRelations(self, REQUEST=None):
        """Delete relations TTW."""
        self.clear()
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url()
                                      + '/manage_editRelations'
                                      '?manage_tabs_message=Deleted.')



InitializeClass(RedlandGraph)

# Register to the graph registry
GraphRegistry.register(RedlandGraph)


# reification attempt
@zope.component.adapter(IStatement, IRedlandGraph)
@zope.interface.implementer(IStatementResource)
def getStatementResource(statement, graph):
    """Return an IStatementResource from an IStatement (reification) and an
    IRedlandGraph

    The statement resource created may depend on the graph internal
    representation, that's why this is a multi adapter.
    """
    # convert statement so that it does not depend on the graph internal
    # representation
    redland_statement = graph._getRedlandStatement(statement)
    statement = graph._getCPSStatement(redland_statement)
    # use sha to identify the statement...
    if not statement:
        # null statement or None value
        res = None
    else:
        statement_id = "{%s, %s, %s}"%(statement.subject,
                                       statement.predicate,
                                       statement.object)
        uid = sha.new(statement_id).hexdigest()
        res = StatementResource(uid)
    return res


#
# Drawer
#


class RedlandGraphDrawer(GraphDrawer):

    def _getDotGraph(self):
        """Get the graph in dot language

        Get rela triples, not their string representation
        """
        import pydot
        dot_graph = pydot.Dot(graph_name=self.graph.getId(),
                              type='digraph',
                              simplify=True)
        for triple in self.graph.listAllRelations():
            edge = self._getEdge(triple)
            if edge is not None:
                dot_graph.add_edge(edge)
        return dot_graph

    def _getEdge(self, triple):
        """Get the pydot edge representing the given triple

        Use graph binding to get a clearer drawing
        """
        new_triple = []
        for item in triple:
            if isinstance(item, Node):
                if isinstance(item, unicode):
                    item.encode('utf-8', 'ignore')
                item = str(item)
                if item.startswith('['):
                    item = item[1:]
                if item.endswith(']'):
                    item = item[:-1]
                for key, binding in self.graph.namespace_bindings.items():
                    if item.startswith(binding):
                        item = item[len(binding):]
                        item = key + '_' + item
            else:
                if isinstance(item, unicode):
                    item.encode('utf-8', 'ignore')
                item = str(item)
            # dont break label
            item = string.replace(item, ':', '_')
            new_triple.append(item)
        import pydot
        edge = pydot.Edge(new_triple[0], new_triple[2], label=new_triple[1])
        return edge
