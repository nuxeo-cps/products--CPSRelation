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
Registry of the available graph types.
"""

class GraphRegistry:
    """Registry of the available graph types.
    """

    def __init__(self):
        """Initialization"""
        self._graph_classes = {}

    def register(self, cls):
        """Register a class for a graph."""
        graph_type = cls.meta_type
        self._graph_classes[graph_type] = cls

    def listGraphTypes(self):
        """Return the list of graph types."""
        return self._graph_classes.keys()

    def makeGraph(self, graph_type, id, **kw):
        """Factory to make a graph of the given type."""
        try:
            cls = self._graph_classes[graph_type]
        except KeyError:
            raise KeyError("No graph type '%s'" % graph_type)
        return cls(id, **kw)

# Singleton
GraphRegistry = GraphRegistry()
