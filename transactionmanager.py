# (C) Copyright 2005-2006 Nuxeo SARL <http://nuxeo.com>
# Authors: Julien Anguenot <ja@nuxeo.com>
#          Florent Guillaume <fg@nuxeo.com>
#          Anahide Tchertchian <at@nuxeo.com>
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
# $Id$
"""Manager for relations management that can be delayed until commit time.

Always synchronous, synchronism depends on the graph synchronism, this
transaction manager synchronism is ignored.
"""

import logging
import transaction
import zope.interface

from Acquisition import aq_base

from Products.CPSCore.interfaces import IBeforeCommitSubscriber
from Products.CPSCore.commithooks import BeforeCommitSubscriber
from Products.CPSCore.commithooks import get_before_commit_subscribers_manager

_TXN_MGR_ATTRIBUTE = '_cps_relation_manager'

# execute it just before CPSCore.IndexationManager (before any other managers)
_TXN_MGR_ORDER = -200

logger = logging.getLogger("CPSRelation.RelationManager")

class RelationManager(BeforeCommitSubscriber):
    """Holds data about relations additions/removals to be done.

    May be synchronous or not, but
    """

    zope.interface.implements(IBeforeCommitSubscriber)

    def __init__(self, mgr):
        """Initialize and register this manager with the transaction."""
        BeforeCommitSubscriber.__init__(self, mgr, order=_TXN_MGR_ORDER)
        # queue records operations by graph id
        self._queue = {}


    def add(self, graph, statements):
        """Process given statements to add to given graph
        """
        num = len(statements)
        graph_id = graph.getId()

        if not self.enabled:
            logger.debug("is DISABLED. Addition of %s statements "
                         "to graph %s won't be done" % (num, graph_id))
            return

        if graph._isSynchronous():
            logger.debug("Adding %s statements to %s" % (num, graph_id))
            graph._add(statements)
            return

        # add statements to add to the right queue for given graph, duplicate
        # statements are not handled
        if self._queue.has_key(graph_id):
            current = self.queue[graph_id]
            current['add'].extend(statements)
            self._queue[graph_id] = current
        else:
            new = {
                'graph': graph,
                'add': statements,
                'remove': [],
                }
            self._queue[graph_id] = new


    def remove(self, graph, statements):
        """Process given statements to remove from given graph
        """
        num = len(statements)
        graph_id = graph.getId()

        if not self.enabled:
            logger.debug("is DISABLED. Removal of %s statements "
                         "to graph %s won't be done" % (num, graph_id))
            return

        if graph._isSynchronous():
            logger.debug("Removing %s statements from %s" % (num, graph_id))
            graph._remove(statements)
            return

        # add statements to remove to the right queue for given graph,
        # duplicate statements are not handled
        if self._queue.has_key(graph_id):
            current = self._queue[graph_id]
            current['remove'].extend(statements)
            self._queue[graph_id] = current
        else:
            new = {
                'graph': graph,
                'add': [],
                'remove': statements,
                }
            self._queue[graph_id] = new


    def __call__(self):
        """Called when transaction commits.

        Does the actual addition/deletion work.
        """
        del_relation_manager()

        logger.debug("__call__")

        for graph_id, graph_info in self._queue.items():
            logger.debug("__call__ processing %s" % graph_id)
            graph = graph_info['graph']
            graph._add(graph_info['add'])
            graph._remove(graph_info['remove'])
            del self._queue[graph_id]

        logger.debug("__call__ done")


def del_relation_manager():
    """Delete relation manager
    """
    txn = transaction.get()
    setattr(txn, _TXN_MGR_ATTRIBUTE, None)


def get_relation_manager():
    """Get the relation manager.

    Creates it if needed.
    """
    txn = transaction.get()
    mgr = getattr(txn, _TXN_MGR_ATTRIBUTE, None)
    if mgr is None:
        mgr = RelationManager(get_before_commit_subscribers_manager())
        setattr(txn, _TXN_MGR_ATTRIBUTE, mgr)
    return mgr
