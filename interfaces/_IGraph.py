# Copyright (c) 2005-2006 Nuxeo SAS <http://nuxeo.com>
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
"""Interface for graphs/models dealing with relations
"""

import zope.interface


class IGraph(zope.interface.Interface):
    """Interface for graphs/models dealing with relations
    """

    def add(statements):
        """Add given list of IStatement objects to the graph
        """

    def remove(statements):
        """Remove given list of IStatement objects from the graph
        """

    def getStatements(statement=None):
        """Return all IStatement objects matching the pattern

        If statement is None, return all statements.
        statement can use None nodes as wild cards.
        """

    def getSubjects(predicate, object):
        """Get items matching the IStatement(None, predicate, object)
        """

    def getPredicates(subject, object):
        """Get items matching the IStatement(subject, None, object)
        """

    def getObjects(subject, predicate):
        """Get items matching the IStatement(subject, predicate, None)
        """

    def hasStatement(statement):
        """Return True if given IStatement is in the graph

        statement can use None nodes as wild cards.
        """

    def hasResource(node):
        """Return True if given node appears in any statement of the graph.
        """

    def __len__():
        """Return the number of statements in the graph
        """

    def clear():
        """Clear the graph, removing all statements in it
        """

    def query(query_string, language, base_uri=None):
        """Query the graph, return an IQueryResult

        language is the query language (sparql, rdql...)
        """

    # I/O

    def read(source, base=None, format="application/rdf+xml"):
        """Parse source into the graph.

        Returns boolean: success or failure.

        source can either be a string, location, stream instance.
        base specifies the logical URI to use in case it differs from the
        physical source URI.
        format defaults to xml (AKA rdf/xml).
        """

    def write(destination=None, base=None, format="application/rdf+xml"):
        """Serialize graph to destination

        If destination is None then serialization is returned as a string.
        base specifies the logical URI to use in case it differs from the
        physical source URI.
        format defaults to xml (AKA rdf/xml).
        """
