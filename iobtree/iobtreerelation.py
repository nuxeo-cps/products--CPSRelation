# Copyright (c) 2004-2005 Nuxeo SARL <http://nuxeo.com>
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
"""Relation that holds relations between objects

A relation holds a IOBTree with object uids as keys and tuples of related
object uids as values. It also stores the id of its inverse relation.
"""

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo

from zope.interface import implements

from BTrees.IOBTree import IOBTree

from Products.CMFCore.utils import SimpleItemWithProperties
from Products.CMFCore.permissions import ManagePortal, View

from Products.CPSRelation.interfaces import IResource
from Products.CPSRelation.interfaces import IPrefixedResource
from Products.CPSRelation.iobtree.interfaces import IIOBTreeRelation
from Products.CPSRelation.statement import Statement
from Products.CPSRelation.node import Resource
from Products.CPSRelation.node import PrefixedResource
from Products.CPSRelation.resourceregistry import ResourceRegistry


class IOBTreeRelation(SimpleItemWithProperties):
    """Relation

    A relation holds an IOBTree with object uids as keys and tuples of related
    object uids as values. It also stores the inverse IOBTree.
    """

    meta_type = 'IOBTree Relation'

    implements(IIOBTreeRelation)

    security = ClassSecurityInfo()

    _properties = (
        {'id': 'prefix', 'type': 'string', 'mode': 'w',
         'label': 'Resource prefix used for the relation'},
        {'id': 'subject_prefix', 'type': 'string', 'mode': 'w',
         'label': 'Resource prefix used for subjects'},
        {'id': 'object_prefix', 'type': 'string', 'mode': 'w',
         'label': 'Resource prefix used for objects'},
        )

    def __init__(self, id, prefix='', subject_prefix='', object_prefix=''):
        """Initialization
        """
        self.id = id
        self.prefix = prefix
        self.subject_prefix = subject_prefix
        self.object_prefix = object_prefix
        self.relations = IOBTree()
        self.inverse_relations = IOBTree()


    def __cmp__(self, other):
        """Compare method
        """
        try:
            other_id = other.getId()
        except AttributeError:
            other_id = None
        return cmp(self.getId(), other_id)


    #
    # Private API
    #

    security.declarePrivate('_getIntegerIdentifier')
    def _getIntegerIdentifier(self, resource, prefix=''):
        """Get an integer identifier from an INode

        Only IResource objects with an integer URI or IPrefixedResource objects
        with an integer localname are supported by IOBTree graphs.
        """
        if resource is None:
            integer = None
        elif not IResource.providedBy(resource):
            raise ValueError("%s is not a resource"%(resource,))
        else:
            if IPrefixedResource.providedBy(resource):
                identifier = resource.localname
            else:
                identifier = resource.uri
            try:
                integer = int(identifier)
            except ValueError:
                msg = "Non digital identifier for resource %s"%(resource,)
                raise ValueError(msg)
        return integer


    security.declarePrivate('_getCPSNode')
    def _getCPSNode(self, identifier, prefix=''):
        """Get an INode from an identifier and a prefix

        The identifier is an integer for subjects and objects.
        """
        if identifier is None:
            node = None
        else:
            temp_node = None
            identifier = str(identifier)
            if prefix:
                # use the prefix to make the resource
                try:
                    # XXX may not be the good keywords
                    temp_node = ResourceRegistry.makeResource(
                        prefix, localname=identifier)
                except KeyError:
                    # no factory registered for this prefix, default to
                    # PrefixedResource
                    temp_node = PrefixedResource(prefix, identifier)
            if temp_node is None:
                node = Resource(identifier)
            else:
                node = temp_node
        return node


    security.declarePrivate('_getCPSRelation')
    def _getCPSRelation(self):
        """Get an IResource representing this IIOBtreeRelation
        """
        return self._getCPSNode(self.getId(), self.prefix)


    security.declarePrivate('_add')
    def _add(self, int_subject, int_object, inverse=False):
        """Add given tuple to the relations tree

        int_subject and int_object have to be integers
        """
        # only check the object, the tree will check the subject
        if not isinstance(int_object, int):
            raise ValueError("Object %s is not an integer"%(int_object,))
        if inverse is False:
            tree = self.relations
        else:
            tree = self.inverse_relations
        related = tree.get(int_subject, [])
        related.append(int_object)
        if tree.has_key(int_subject):
            del tree[int_subject]
        tree.insert(int_subject, related)


    security.declarePrivate('_remove')
    def _remove(self, int_subject, int_object, inverse=False):
        """Remove given tuple from the relations tree

        int_subject and int_object have to be integers
        """
        if inverse is False:
            tree = self.relations
        else:
            tree = self.inverse_relations
        related = tree.get(int_subject, [])
        if int_object in related:
            related.remove(int_object)
        if tree.has_key(int_subject):
            del tree[int_subject]
        if related:
            tree.insert(int_subject, related)


    #
    # API
    #

    security.declarePrivate('add')
    def add(self, tuples):
        """Add given statements to the relation graphs

        A tuple has to be an (IPrefixedPesource, IPrefixedPesource) tuple, and
        resources have to have integer local names.
        """
        # not optimized...
        for subject, object in tuples:
            int_subject = self._getIntegerIdentifier(subject,
                                                     self.subject_prefix)
            int_object = self._getIntegerIdentifier(object,
                                                    self.object_prefix)
            self._add(int_subject, int_object)
            self._add(int_object, int_subject, inverse=True)


    security.declarePrivate('remove')
    def remove(self, tuples):
        """Remove given tuples from the relation graphs

        A tuple has to be an (IPrefixedPesource, IPrefixedPesource) tuple, and
        resources have to have integer local names.
        """
        # not optimized...
        for subject, object in tuples:
            int_subject = self._getIntegerIdentifier(subject,
                                                     self.subject_prefix)
            int_object = self._getIntegerIdentifier(object,
                                                    self.object_prefix)
            self._remove(int_subject, int_object)
            self._remove(int_object, int_subject, inverse=True)


    security.declarePrivate('getStatements')
    def getStatements(self, subject=None, object=None):
        """Get statements for this IOBTreeRelation

        None values can be used as wild cards
        """
        res = []
        predicate = self._getCPSRelation()
        if subject is None and object is None:
            # return all statements
            for int_subject, int_objects in self.relations.items():
                subject = self._getCPSNode(int_subject, self.subject_prefix)
                objects = [self._getCPSNode(int_object, self.object_prefix)
                           for int_object in int_objects]
                res.extend([Statement(subject, predicate, object)
                            for object in objects])
        elif subject is not None and object is not None:
            # return given tuple if it's in the graph
            if self.hasTuple(subject, object):
                res = [Statement(subject, predicate, object)]
        elif subject is None:
            # object is not None
            res = [Statement(x, predicate, object)
                   for x in self.getSubjects(object)]
        else:
            # object is None and subject is not None
            res = [Statement(subject, predicate, x)
                   for x in self.getObjects(subject)]
        return res


    security.declarePrivate('getSubjects')
    def getSubjects(self, object):
        """Get subjects for given object

        object has to be an IPrefixedPesource and have an integer localname.
        """
        int_object = self._getIntegerIdentifier(object, self.object_prefix)
        res = [self._getCPSNode(x, self.subject_prefix)
               for x in self.inverse_relations.get(int_object, [])]
        return res


    security.declarePrivate('getObjects')
    def getObjects(self, subject):
        """Get objects for given subject

        subject has to be an IPrefixedPesource and have an integer localname.
        """
        int_subject = self._getIntegerIdentifier(subject, self.subject_prefix)
        res = [self._getCPSNode(x, self.object_prefix)
               for x in self.relations.get(int_subject, [])]
        return res


    security.declarePrivate('hasTuple')
    def hasTuple(self, subject=None, object=None):
        """Return if given tuple is in the relations
        """
        res = False
        if subject is None and object is None:
            if len(self) > 0:
                res = True
        elif subject is not None and object is not None:
            related = self.getObjects(subject)
            res = object in related
        elif subject is None:
            # object is not None
            if self.getSubjects(object):
                res = True
        else:
            # object is None and subject is not None
            if self.getObjects(subject):
                res = True
        return res


    security.declareProtected(View, 'clear')
    def clear(self):
        """Clear the relation, removing all items in its trees
        """
        self.relations = IOBTree()
        self.inverse_relations = IOBTree()


    security.declareProtected(View, '__len__')
    def __len__(self):
        """Return the number of statements in the relation
        """
        # may be optimized (?)
        length = 0
        for related in self.relations.values():
            length += len(related)
        return length


    #
    # ZMI
    #

    manage_options = (SimpleItemWithProperties.manage_options[0],) + (
        {'label': "Contents",
         'action': 'contents'
         },
        {'label': "Overview",
         'action': 'overview'
         },
        ) + SimpleItemWithProperties.manage_options[1:]

    security.declareProtected(ManagePortal, 'contents')
    contents = DTMLFile('../zmi/iobtreerelation_content', globals())

    security.declareProtected(ManagePortal, 'overview')
    overview = DTMLFile('../zmi/iobtreerelation_overview', globals())


InitializeClass(IOBTreeRelation)
