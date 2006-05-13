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
"""
Object Serializer Tool that provides services to get RDF serializations of
objects
"""

# XXX Currently requires Serializer from RDF to serialize to RDF/XML files

import os
import tempfile
import logging

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo

from zope.interface import implements

from Products.CMFCore.permissions import ManagePortal, View
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.CMFBTreeFolder import CMFBTreeFolder

from Products.CPSRelation.interfaces import IObjectSerializerTool
from Products.CPSRelation.objectserializer import ObjectSerializer

logger = logging.getLogger("CPSRelation.ObjectSerializerTool")

class ObjectSerializerTool(UniqueObject, CMFBTreeFolder):
    """Object Serializer Tool that provides services to get RDF serializations
    of objects

    Stores definitions of mappings between objects and their rdf view
    (statements)
    """

    id = 'portal_serializer'
    meta_type = "Object Serializer Tool"

    implements(IObjectSerializerTool)

    security = ClassSecurityInfo()

    #
    # API
    #

    def __init__(self):
        """Initialization
        """
        CMFBTreeFolder.__init__(self, self.id)


    security.declareProtected(View, 'listSerializers')
    def listSerializers(self):
        """List object serializers managed by the tool
        """
        return CMFBTreeFolder.objectIds_d(self).keys()


    security.declareProtected(View, 'hasSerializer')
    def hasSerializer(self, id):
        """Does the tool have the given object serializer?
        """
        key = CMFBTreeFolder.has_key(self, id)
        if key:
            return 1
        else:
            return 0


    security.declareProtected(ManagePortal, 'addSerializer')
    def addSerializer(self, id, expr='', bindings={}):
        """Add an object serializer with given id and expression
        """
        if self.hasSerializer(id):
            raise ValueError("The id '%s' is invalid - it is already in use"%id)
        else:
            ser = ObjectSerializer(id, expr, bindings)
            self._setObject(id, ser)
            return self._getOb(id)


    security.declareProtected(ManagePortal, 'deleteSerializer')
    def deleteSerializer(self, id):
        """Delete given object serializer
        """
        if self.hasSerializer(id):
            self._delObject(id)


    security.declarePrivate('getSerializer')
    def getSerializer(self, id):
        """Get object serializer with given id
        """
        try:
            ser = self._getOb(id)
        except KeyError:
            raise AttributeError("Serializer '%s' does not exist" %id)
        else:
            return ser

    # serialization operations

    security.declareProtected(View, 'getSerializationStatements')
    def getSerializationStatements(self, object, serializer_id):
        """Get Serialization for given object using given serializer

        return serialization as a list of statements
        """
        ser = self.getSerializer(serializer_id)
        statements = ser.getStatements(object)
        return statements


    # XXX AT: Currently (indirectly) requires Redland
    security.declarePrivate('serializeGraph')
    def serializeGraph(self, rdf_graph, base=None):
        """Serialize given IGraph to an rdf/xml string using the optional
        base URI string
        """
        res = rdf_graph.write(base=base, format="application/rdf+xml")
        return res


    # XXX AT: Currently requires Redland
    security.declareProtected(View, 'getSerializationGraph')
    def getSerializationGraph(self, statements=[], serialization='',
                              namespace_bindings={}):
        """Get the IGraph that will be used for serialization

        bindings are optional bindings that will be set on the IGraph and used
        for serialization operations.
        """
        # may throw an error if Redland is not available
        from Products.CPSRelation.redland.redlandgraph import RedlandGraph
        graph = RedlandGraph('dummy', backend='memory',
                             namespace_bindings=namespace_bindings)
        # add given statements
        graph.add(statements)
        # add given serialization statements
        if serialization:
            base_uri = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            graph.read(serialization, base=base_uri)
        return graph


    # XXX AT: Currently (indirectly) requires Redland
    security.declareProtected(View, 'getSerializationFromSerializer')
    def getSerializationFromSerializer(self, object, serializer_id, base=None):
        """Get serialization for given object using given serializer

        Serialize statements given by serializer to an rdf/xml string using the
        optional base URI.
        """
        ser = self.getSerializer(serializer_id)
        statements = ser.getStatements(object)
        bindings = ser.getNamespaceBindings()
        rdf_graph = self.getSerializationGraph(
            statements=statements, namespace_bindings=bindings)
        return self.serializeGraph(rdf_graph, base=base)


    # XXX AT: Currently (indirectly) requires Redland
    security.declareProtected(View, 'getSerializationFromStatements')
    def getSerializationFromStatements(self, statements, base=None,
                                       namespace_bindings={}):
        """Get serialization for given statements

        Serialize given statements to an rdf/xml string using the optional base
        URI.
        """
        graph = self.getSerializationGraph(
            statements=statements, namespace_bindings=namespace_bindings)
        return self.serializeGraph(graph, base=base)


    # XXX AT: Currently (indirectly) requires Redland
    security.declareProtected(View, 'getSerializationFromGraph')
    def getSerializationFromGraph(self, graph, base=None):
        """Get serialization for given IGraph

        Serialize graph to an rdf/xml string using the optional base URI.
        """
        return self.serializeGraph(graph, base=base)


    # XXX AT: Currently (indirectly) requires Redland
    security.declareProtected(View, 'getMultipleSerialization')
    def getMultipleSerialization(self, objects_info, base=None):
        """Get Serialization for given objects

        objects_info is a sequence of items with object as first element and
        serializer id as second element.

        Serialize found statements to an rdf/xml string using the optional base
        URI
        """
        all_statements = []
        all_bindings = {}
        for object_info in objects_info:
            ser = self.getSerializer(object_info[1])
            statements = ser.getStatements(object_info[0])
            all_statements.extend(statements)
            all_bindings.update(ser.getNamespaceBindings())
        rdf_graph = self.getSerializationGraph(statements=all_statements)
        return self.serializeGraph(rdf_graph, base=base,
                                   bindings=all_bindings)


    # drawing operations, require pydot installation

    def checkPydotInstall(self):
        """Check pydot/GraphViz installation

        Return (ok, err). If ok is False (some install has not been detected),
        err is the error message.
        """
        ok = True
        err = ''
        try:
            import pydot
        except ImportError, err:
            if str(err) != 'No module named pydot':
                raise
            logger.info("pydot could not be found")
            ok, err = False, 'pydot not found'
        else:
            if pydot.find_graphviz() is None:
                logger.info("GraphViz could not be found")
                ok, err = False, 'GraphViz not found'
        return ok, err

    def getGraphDrawing(self, graph_id):
        """Get the graph drawing

        graph is a CPSRelation graph: it has to have a type registered in the
        graph registry.
        """
        ok, err = self.checkPydotInstall()
        if ok is True:
            rtool = getToolByName(self, 'portal_relations')
            graph = rtool.getGraph(graph_id)
            ok, res = graph.getDrawing()
        else:
            res = ''
        # only return drawing as image will be displayed in a img HTML tag
        return res

    #
    # ZMI
    #

    # Here define options using DTML files
    manage_options = (
        {'label': "Object Serializers",
         'action': 'manage_main'
         },
        {'label': "Overview",
         'action': 'overview'
         },
        ) + CMFBTreeFolder.manage_options[2:4]

    security.declareProtected(ManagePortal, 'manage_main')
    manage_main = DTMLFile('zmi/objectserializertool_content', globals())

    security.declareProtected(ManagePortal, 'overview')
    overview = DTMLFile('zmi/objectserializertool_overview', globals())

    security.declareProtected(ManagePortal, 'manage_addSerializer')
    def manage_addSerializer(self, id, serialization_expr, bindings,
                             REQUEST=None):
        """Add a graph TTW"""
        self.addSerializer(id, serialization_expr, bindings)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main'
                                      '?manage_tabs_message=Serializer Added.')

    security.declareProtected(ManagePortal, 'manage_editSerializers')
    def manage_editSerializers(self,
                               all_ids,
                               serialization_expressions,
                               all_bindings,
                               REQUEST=None):
        """Edit Object Serializers TTW.
        """
        for index, id in enumerate(all_ids):
            if self.hasSerializer(id):
                expr = serialization_expressions[index]
                bindings = all_bindings[index]
                kw = {
                    'serialization_expr': expr,
                    'bindings': bindings,
                    }
                serializer = self.getSerializer(id)
                serializer.manage_changeProperties(**kw)
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main'
                                      '?manage_tabs_message=Edited.')

    security.declareProtected(ManagePortal, 'manage_deleteSerializers')
    def manage_deleteSerializers(self, checked_ids, REQUEST=None):
        """Delete object serializers TTW."""
        for id in checked_ids:
            self.deleteSerializer(id)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main'
                                      '?manage_tabs_message=Deleted.')

    security.declareProtected(ManagePortal, 'manage_deleteAllSerializers')
    def manage_deleteAllSerializers(self, REQUEST=None):
        """Delete all object serializers TTW."""
        for id in self.listSerializers():
            self.deleteSerializer(id)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main'
                                      '?manage_tabs_message=Deleted.')



InitializeClass(ObjectSerializerTool)

