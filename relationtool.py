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
"""Relation tool to manage graphs holding relations between objects.
"""

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo

from zope.interface import implements

from Products.CMFCore.permissions import ManagePortal, View
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.CMFBTreeFolder import CMFBTreeFolder

from Products.CPSRelation.interfaces import IRelationTool
from Products.CPSRelation.graphregistry import GraphRegistry

class RelationTool(UniqueObject, CMFBTreeFolder):
    """Relation tool to manage graphs holding relations between objects.
    """

    id = 'portal_relations'
    meta_type = 'Relation Tool'

    implements(IRelationTool)

    security = ClassSecurityInfo()

    #
    # API
    #

    def __init__(self):
        """Initialization
        """
        CMFBTreeFolder.__init__(self, self.id)

    security.declareProtected(View, 'getSupportedGraphTypes')
    def getSupportedGraphTypes(self):
        """Get supported graph meta types
        """
        return GraphRegistry.listGraphTypes()

    # graphs

    security.declareProtected(ManagePortal, 'listGraphIds')
    def listGraphIds(self):
        """List all the existing graphs
        """
        return CMFBTreeFolder.objectIds_d(self).keys()

    security.declareProtected(ManagePortal, 'deleteAllGraphs')
    def deleteAllGraphs(self):
        """Delete all the graphs.
        """
        for graph_id in self.listGraphIds():
            self.deleteGraph(graph_id)

    security.declareProtected(ManagePortal, 'hasGraph')
    def hasGraph(self, graph_id):
        """Is there a graph with the given id?
        """
        key = CMFBTreeFolder.has_key(self, graph_id)
        if key:
            return 1
        else:
            return 0

    security.declareProtected(ManagePortal, 'addGraph')
    def addGraph(self, graph_id, type, **kw):
        """Add a graph with the given information

        Use a graph registry to instanciate the graph with given type
        """
        if self.hasGraph(graph_id):
            raise KeyError, 'the graph %s already exists.' % graph_id
        graph = GraphRegistry.makeGraph(type, graph_id, **kw)
        return CMFBTreeFolder._setOb(self, graph_id, graph)

    security.declareProtected(ManagePortal, 'deleteGraph')
    def deleteGraph(self, graph_id):
        """Delete graph with given id
        """
        # remove relations in the graph in case it's in a bdb backend
        try:
            graph = self.getGraph(graph_id)
        except KeyError:
            pass
        else:
            try:
                graph.clear()
            except AttributeError:
                pass
        return CMFBTreeFolder._delOb(self, graph_id)

    security.declareProtected(ManagePortal, 'getGraph')
    def getGraph(self, graph_id, default=None):
        """Get the given graph

        Then will be able to query this graph API
        """
        return CMFBTreeFolder._getOb(self, graph_id, default)

    #
    # Relations
    #

    # TODO: get the graph to be used using predicate mappings and implement
    # base methods (add, remove)


    #
    # ZMI
    #

    manage_options = (
        {'label': "Graphs",
         'action': 'manage_editGraphs'
         },
        {'label': "Overview",
         'action': 'overview'
         },
        ) + CMFBTreeFolder.manage_options[2:4]

    security.declareProtected(ManagePortal, 'manage_editGraphs')
    manage_editGraphs = DTMLFile('zmi/relationtool_graphs', globals())

    security.declareProtected(ManagePortal, 'overview')
    overview = DTMLFile('zmi/relationtool_overview', globals())

    security.declareProtected(ManagePortal, 'manage_listGraphTypes')
    def manage_listGraphTypes(self):
        """List graph types that can be added TTW"""
        return GraphRegistry.listGraphTypes()

    security.declareProtected(ManagePortal, 'manage_addGraph')
    def manage_addGraph(self, id, type, REQUEST=None):
        """Add a graph TTW"""
        self.addGraph(id, type)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url()
                                      + '/manage_editGraphs'
                                      '?manage_tabs_message=Graph Added.')

    security.declareProtected(ManagePortal, 'manage_deleteGraphs')
    def manage_deleteGraphs(self, ids, REQUEST=None):
        """Delete graphs TTW."""
        for id in ids:
            self.deleteGraph(id)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url()
                                      + '/manage_editGraphs'
                                      '?manage_tabs_message=Deleted.')

    security.declareProtected(ManagePortal, 'manage_deleteAllGraphs')
    def manage_deleteAllGraphs(self, REQUEST=None):
        """Delete graphs TTW."""
        self.deleteAllGraphs()
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url()
                                      + '/manage_editGraphs'
                                      '?manage_tabs_message=Deleted.')

InitializeClass(RelationTool)
