# Copyright (c) 2005-2006 Nuxeo SAS <http://nuxeo.com>
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
"""Interface for a tool that deals with different graphs
"""

from zope.interface import Interface

class IRelationTool(Interface):
    """Interface for a tool that deals with graphs
    """

    # graphs

    def listGraphIds():
        """List all the existing graphs
        """

    def deleteAllGraphs():
        """Delete all graphs
        """

    def hasGraph(graph_id):
        """Is there a graph with the given id?
        """

    def addGraph(graph_id, graph_type, **kw):
        """Add a graph with the given information
        """

    def deleteGraph(graph_id):
        """Delete graph with given id
        """

    def getGraph(graph_id, default=None):
        """Get the given graph

        Then will be able to query this graph API
        """

    # XXX Additional methods defined on graph are needed here too
