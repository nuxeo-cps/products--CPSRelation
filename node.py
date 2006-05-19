# Copyright (c) 2006 Nuxeo SAS <http://nuxeo.com>
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
"""Node classes

Some classes can be imported and used directly in third-party code, others have
to be created using adapters.
"""

import zope.interface
import zope.component

import sha

from Products.CMFCore.utils import getToolByName

from Products.CPSCore.interfaces import ICPSProxy

from Products.CPSRelation.interfaces import INode
from Products.CPSRelation.interfaces import IBlank
from Products.CPSRelation.interfaces import ILiteral
from Products.CPSRelation.interfaces import IResource
from Products.CPSRelation.interfaces import IStatement
from Products.CPSRelation.interfaces import IPrefixedResource
from Products.CPSRelation.interfaces import IVersionResource
from Products.CPSRelation.interfaces import IVersionHistoryResource
from Products.CPSRelation.interfaces import IRpathResource
from Products.CPSRelation.interfaces import IStatementResource

from Products.CPSRelation.resourceregistry import ResourceRegistry

class BaseNode:
    """Base node class, never instanciated
    """

    zope.interface.implements(INode)

    def __hash__(self):
        return hash(str(self))

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return str(self)

    def __cmp__(self, other):
        # useful for list of nodes sorting
        return cmp(str(self), str(other))


class Resource(BaseNode):
    """Resource node
    """

    zope.interface.implements(IResource)

    def __init__(self, uri):
        """Init for resource
        """
        self.uri = uri

    def __str__(self):
        return "<%s '%s'>"%(self.__class__, self.uri,)

    def __eq__(self, other):
        if (not isinstance(other, self.__class__)
            or self.uri != other.uri):
            return False
        else:
            return True


class PrefixedResource(Resource):
    """Base class for a prefixed resource
    """

    zope.interface.implements(IPrefixedResource)

    def __init__(self, prefix, localname):
        """Init for resource
        """
        self.prefix = prefix
        self.localname = localname
        self.uri = prefix + ':' + localname

    def __str__(self):
        return "<%s '%s'>"%(self.__class__, self.uri,)


class Blank(BaseNode):
    """Blank node
    """

    zope.interface.implements(IBlank)

    def __init__(self, id=''):
        """Init for blank node
        """
        self.id = id

    def __str__(self):
        return "<%s '%s'>"%(self.__class__, self.id,)

    def __eq__(self, other):
        if (not isinstance(other, self.__class__)
            or self.id != other.id):
            return False
        else:
            return True


class Literal(BaseNode):
    """Literal node (plain or typed)
    """

    zope.interface.implements(ILiteral)

    def __init__(self, value, language=None, type=None):
        """Init for literal node (plain or typed)

        value has to be encoded in iso-8859-15
        """
        # literal as to be plain or typed, cannot be both
        assert not language or not type
        if isinstance(value, unicode):
            # force value to iso-8859-15 here
            value = value.encode('iso-8859-15', 'ignore')
        self.value = value
        self.language = language
        self.type = type

    def __str__(self):
        name = str(self.__class__)
        if self.type:
            return "<%s '%s^^%s'>"%(name, self.value, self.type)
        elif self.language:
            return "<%s '%s@%s'>"%(name, self.value, self.language)
        else:
            return "<%s '%s'>"%(name, self.value,)

    def __eq__(self, other):
        if (not isinstance(other, self.__class__)
            or self.value != other.value
            or self.language != other.language
            or self.type != other.type):
            return False
        else:
            return True


# basic resource classes

class VersionResource(PrefixedResource):
    """Version resource
    """

    zope.interface.implements(IVersionResource)
    prefix = 'uuid'

    def __init__(self, localname='', docid='', revision=''):
        assert docid and revision or localname
        if docid and revision:
            self.docid = docid
            self.revision = revision
            # XXX rebuild the docid__revision pattern...
            self.localname = "%s__%#04d" % (docid, revision)
        else:
            # XXX decode the docid__revision pattern...
            self.localname = localname
            localname_split = localname.split('__')
            self.docid = localname_split[0]
            self.revision = int(localname_split[1])
        self.uri = self.prefix + ':' + self.localname

ResourceRegistry.register(VersionResource)


class VersionHistoryResource(PrefixedResource):
    """Version History Resource
    """

    zope.interface.implements(IVersionHistoryResource)
    prefix = 'docid'

    def __init__(self, localname):
        self.docid = localname
        self.localname = self.docid
        self.uri = self.prefix + ':' + self.localname

ResourceRegistry.register(VersionHistoryResource)


class RpathResource(PrefixedResource):
    """Rpath Resource
    """

    zope.interface.implements(IRpathResource)
    prefix = 'rpath'

    def __init__(self, localname):
        self.rpath = localname
        self.localname = self.rpath
        self.uri = self.prefix + ':' + self.localname

ResourceRegistry.register(RpathResource)


# reification attempt

class StatementResource(PrefixedResource):
    """Statement Resource
    """

    zope.interface.implements(IStatementResource)
    prefix = 'statement'

    def __init__(self, localname):
        self.rpath = localname
        self.localname = self.rpath
        self.uri = self.prefix + ':' + self.localname

ResourceRegistry.register(StatementResource)



# basic resource adapters

@zope.component.adapter(ICPSProxy)
@zope.interface.implementer(IVersionResource)
def getProxyVersionResource(proxy):
    """return a VersionResource from a proxy
    """
    docid = proxy.getDocid()
    revision = proxy.getRevision()
    return VersionResource(docid=docid, revision=revision)


@zope.component.adapter(ICPSProxy)
@zope.interface.implementer(IVersionHistoryResource)
def getProxyVersionHistoryResource(proxy):
    """return a VersionHistoryResource from a proxy
    """
    docid = proxy.getDocid()
    return VersionHistoryResource(docid)


# XXX any persistent object will do here
@zope.component.adapter(ICPSProxy)
@zope.interface.implementer(IRpathResource)
def getProxyRpathResource(proxy):
    """return a RpathResource from a proxy
    """
    utool = getToolByName(proxy, 'portal_url')
    # query the url tool to get the relative path
    rpath = utool.getRpath(proxy)
    return RpathResource(rpath)


@zope.component.adapter(IStatement)
@zope.interface.implementer(IStatementResource)
def getStatementResource(statement):
    """return an IStatementResource from an IStatement (reification)
    """
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
