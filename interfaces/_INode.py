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
"""Interfaces for nodes
"""

from zope.interface import Interface
from zope.interface import Attribute


class INode(Interface):
    """Interface for base node
    """


class IResource(INode):
    """Base resource, representing an identified object
    """

    uri = Attribute("URI")


class IBlank(INode):
    """Blank node
    """

    id = Attribute("Blank node identifier")


class ILiteral(INode):
    """Literal node, plain or typed
    """

    value = Attribute("Literal string value")
    language = Attribute("Language")
    type = Attribute("Literal Data type")


# CPS additional resource types

class IPrefixedResource(IResource):
    """Base prefixed resource: identified by a prefix and a local name
    """

    prefix = Attribute("IPrefix for the namespace")
    localname = Attribute("Local name")

class IVersionResource(IPrefixedResource):
    """Resource representing a specific version of a document
    """

    # CPS3 style
    docid = Attribute("Document identifier")
    revision = Attribute("Document revision")


class IVersionHistoryResource(IPrefixedResource):
    """Resource representing the set of revisions of a document
    """

    # CPS3 style
    docid = Attribute("Document identifier")


class IRpathResource(IPrefixedResource):
    """Resource representing a document at a given place
    """

    rpath = Attribute("Relative path")
