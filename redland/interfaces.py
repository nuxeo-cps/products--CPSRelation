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
"""Redland specific interfaces
"""

from Products.CPSRelation.interfaces import IGraph

class IRedlandGraph(IGraph):
    """Interface for a Redland graph
    """

    def getNamespaceBindings():
        """get the prefix/namespace dictionnary
        """

    def _getRedlandStatement(statement):
        """Get the Redland statement representing given IStatement
        """

    def _getCPSStatement(rstatement):
        """Get the IStatement representing given Redland statement
        """
