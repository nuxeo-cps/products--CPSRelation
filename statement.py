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
"""Statement class

This class can be imported and used in third-party code.
"""

import zope.interface

from Products.CPSRelation.interfaces import IStatement
from Products.CPSRelation.interfaces import IResource
from Products.CPSRelation.interfaces import IBlank
from Products.CPSRelation.interfaces import INode

class Statement:
    """Statement class

    A statement is basically a triple (IResource, IResource, INode).
    """

    zope.interface.implements(IStatement)

    def __init__(self, subject, predicate, object):
        """Init for statement
        """
        if (subject is not None and
            not IResource.providedBy(subject) and
            not IBlank.providedBy(subject)):
            msg = "Subject %s does not provide IResource nor IBlank" % (
                subject,)
            raise ValueError(msg)
        if (predicate is not None and
            not IResource.providedBy(predicate)):
            msg = "Predicate %s does not provide IResource" % (predicate,)
            raise ValueError(msg)
        if (object is not None and
            not INode.providedBy(object)):
            msg = "Object %s does not provide INode" % (object,)
            raise ValueError(msg)
        self.subject = subject
        self.predicate = predicate
        self.object = object

    def __str__(self):
        return "<%s {%s, %s, %s}>" % (self.__class__, self.subject,
                                      self.predicate, self.object)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if (not isinstance(other, Statement)
            or self.subject != other.subject
            or self.predicate != other.predicate
            or self.object != other.object):
            return False
        else:
            return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __cmp__(self, other):
        # useful for list of statements sorting
        return cmp(str(self), str(other))
