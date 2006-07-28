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

from nuxeo.capsule.interfaces import IDocument as ICapsuleDocument
from nuxeo.capsule.interfaces import IProxy as ICapsuleProxy

from Products.CPSRelation.interfaces import IVersionHistoryResource
from Products.CPSRelation.interfaces import IRpathResource

from Products.CPSRelation.node import VersionHistoryResource
from Products.CPSRelation.node import RpathResource


# XXX AT: cannot get an integer revision number for VersionResource for now =>
# not implemented as it is

@zope.component.adapter(ICapsuleDocument)
@zope.interface.implementer(IVersionHistoryResource)
def getCapsuleDocumentVersionHistoryResource(document):
    """return a VersionHistoryResource from a ICapsuleDocument
    """
    docid = document.getDocid()
    return VersionHistoryResource(docid)


@zope.component.adapter(ICapsuleProxy)
@zope.interface.implementer(IVersionHistoryResource)
def getCapsuleProxyVersionHistoryResource(proxy):
    """return a VersionHistoryResource from a ICapsuleProxy
    """
    document = proxy.getContent()
    return IVersionHistoryResource(document)


@zope.component.adapter(ICapsuleDocument)
@zope.interface.implementer(IRpathResource)
def getCapsuleDocumentRpathResource(document):
    """return a RpathResource from a capsule document
    """
    utool = getToolByName(document, 'portal_url')
    # query the url tool to get the relative path
    rpath = utool.getRpath(document)
    return RpathResource(rpath)

# getCapsuleDocumentRpathResource will do the trick for frozen documents as
# well as proxies (which are also ICapsuleDocument instances)
