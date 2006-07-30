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
"""Node adapters for Capsule document
"""

import zope.interface
import zope.component

from Products.CMFCore.utils import getToolByName

from nuxeo.capsule.interfaces import IDocument
from nuxeo.capsule.interfaces import IFrozenDocument
from nuxeo.capsule.interfaces import IProxy

from Products.CPSRelation.resourceregistry import ResourceRegistry

from Products.CPSRelation.interfaces import IVersionResource
from Products.CPSRelation.interfaces import IVersionHistoryResource
from Products.CPSRelation.interfaces import IRpathResource

from Products.CPSRelation.node import VersionResource
from Products.CPSRelation.node import VersionHistoryResource
from Products.CPSRelation.node import RpathResource


#
# version
#

class CapsuleVersionResource(VersionResource):
    """Capsule Version resource
    """

    zope.interface.implements(IVersionResource)
    prefix = 'cuuid'

    def __init__(self, localname=''):
        """Init for resource, only use localname
        """
        self.localname = localname
        self.uri = self.prefix + ':' + localname
        # XXX AT: useless, just here to follow the interface
        self.docid = self.localname
        self.revision = 0

ResourceRegistry.register(CapsuleVersionResource)


# getCapsuleDocumentVersionResource will do the trick for frozen documents as
# well as proxies (which are also IDocument instances)


@zope.component.adapter(IDocument)
@zope.interface.implementer(IVersionResource)
def getCapsuleDocumentVersionResource(document):
    """return a CapsuleVersionResource from a capsule document
    """
    uuid = document.getUUID()
    return CapsuleVersionResource(uuid)


#
# version history
#

# XXX AT: cannot get an integer revision number for VersionHistoryResource =>
# cannot be used with IOBTree graphs

@zope.component.adapter(IDocument)
@zope.interface.implementer(IVersionHistoryResource)
def getCapsuleDocumentVersionHistoryResource(document):
    """return a IVersionHistoryResource from a IDocument
    """
    uuid = document.getUUID()
    return VersionHistoryResource(uuid)

@zope.component.adapter(IFrozenDocument)
@zope.interface.implementer(IVersionHistoryResource)
def getCapsuleFrozenDocumentVersionHistoryResource(document):
    """return a IVersionHistoryResource from a IFrozenDocument
    """
    uuid = document.getOriginalUUID()
    return VersionHistoryResource(uuid)

@zope.component.adapter(IProxy)
@zope.interface.implementer(IVersionHistoryResource)
def getCapsuleProxyVersionHistoryResource(proxy):
    """return a IVersionHistoryResource from a IProxy
    """
    document = proxy.getContent()
    return IVersionHistoryResource(document)

#
# rpath
#

# getCapsuleDocumentRpathResource will do the trick for frozen documents as
# well as proxies (which are also IDocument instances)

@zope.component.adapter(IDocument)
@zope.interface.implementer(IRpathResource)
def getCapsuleDocumentRpathResource(document):
    """return a RpathResource from a capsule document
    """
    utool = getToolByName(document, 'portal_url')
    # query the url tool to get the relative path
    rpath = utool.getRpath(document)
    return RpathResource(rpath)
