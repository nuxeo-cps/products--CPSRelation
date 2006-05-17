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
"""CPSRelation additional Interfaces
"""

# XXX AT these interfaces have only been defined to be used in the
# export/import mechanism

from zope.interface import Interface

from _IRelationTool import IRelationTool
from _IGraph import IGraph
from _IQuery import IQueryResult

from _IStatement import IStatement

from _INode import INode
from _INode import IResource
from _INode import IPrefixedResource
from _INode import IBlank
from _INode import ILiteral
# CPS additional concepts
from _INode import IVersionResource
from _INode import IVersionHistoryResource
from _INode import IRpathResource
# reification attemps
from _INode import IStatementResource


class IObjectSerializerTool(Interface):
    """ObjectSerializer Tool.
    """

class IObjectSerializer(Interface):
    """ObjectSerializer.
    """
