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
"""CPS Relation Init
"""

import logging

from Products.GenericSetup import profile_registry
from Products.GenericSetup import EXTENSION

from Products.CMFCore.utils import ToolInit
from Products.CMFCore.permissions import AddPortalContent, ManagePortal

from Products.CPSCore.interfaces import ICPSSite

from Products.CPSRelation import relationtool
from Products.CPSRelation import graphregistry
from Products.CPSRelation import resourceregistry

from Products.CPSRelation import objectserializertool
from Products.CPSRelation import objectserializer

# register default resources
from Products.CPSRelation import node

from Products.CPSRelation.iobtree import iobtreegraph
from Products.CPSRelation.iobtree import iobtreerelation

logger = logging.getLogger("CPSRelation")

USE_REDLAND = 0

# XXX check that Redland is installed before importing
try:
    import RDF
except ImportError, err:
    msg = "Redland is not installed, no RDF feature will be available"
    logger.info(msg)
    if str(err) != 'No module named RDF':
        raise
else:
    USE_REDLAND = 1
    from Products.CPSRelation.redland import redlandgraph

tools = (
    relationtool.RelationTool,
    objectserializertool.ObjectSerializerTool,
    )

def initialize(registrar):
    """Initalization of Relations tool and Relation content
    """
    ToolInit('CPSRelation Tools',
             tools=tools,
             icon='tool.png').initialize(registrar)

    # additional classes, needed for export/import
    registrar.registerClass(
        iobtreegraph.IOBTreeGraph,
        permission=ManagePortal,
        constructors=(relationtool.RelationTool.addGraph,)
        )
    if USE_REDLAND:
        registrar.registerClass(
            redlandgraph.RedlandGraph,
            permission=ManagePortal,
            constructors=(relationtool.RelationTool.addGraph,)
            )
    registrar.registerClass(
        objectserializer.ObjectSerializer,
        permission=ManagePortal,
        constructors=(
        objectserializertool.ObjectSerializerTool.manage_addSerializer,)
        )

    profile_registry.registerProfile(
        'default',
        'CPS Relation',
        "Relation product for CPS.",
        'profiles/default',
        'CPSRelation',
        EXTENSION,
        for_=ICPSSite)
