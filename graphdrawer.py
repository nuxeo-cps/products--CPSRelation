# Copyright (c) 2004-2005 Nuxeo SARL <http://nuxeo.com>
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
Drawer for graphs
"""

import string
import logging

from Globals import InitializeClass

logger = logging.getLogger("CPSRelation.GraphDrawer")

try:
    import pydot
except ImportError, err:
    if str(err) != 'No module named pydot':
        raise
    logger.info("pydot could not be found")

class GraphDrawer:

    def __init__(self, graph):
        """Init with graph as attribute
        """
        self.graph = graph

    def _getDotGraph(self):
        """Get the graph in dot language

        May be overloaded in specific graph classes
        """
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

        May be overloaded in specific graph classes
        """
        new_triple = []
        for item in triple:
            if isinstance(item, unicode):
                item.encode('utf-8', 'ignore')
            item = str(item)
            # dont break label
            item = string.replace(item, ':', '_')
            new_triple.append(item)
        edge = pydot.Edge(new_triple[0], new_triple[2], label=new_triple[1])
        return edge

    def getDrawing(self, format="jpeg"):
        """Get graph drawing in given format

        Return (ok, result), result is the image if ok is True, the error
        message if ok is False.
        Given format has to be supported by pydot.
        """
        dot_graph = self._getDotGraph()
        if format not in dot_graph.formats:
            ok = False
            result = 'format %s not supported' % (format,)
        else:
            ok = True
            result = dot_graph.create(prog='dot', format=format)
        return ok, result

InitializeClass(GraphDrawer)
