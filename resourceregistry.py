# Copyright (c) 2004-2005 Nuxeo SARL <http://nuxeo.com>
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
"""
Registry of the available resource types.
"""

class ResourceRegistry:
    """Registry of the available resource types.
    """

    def __init__(self):
        """Initialization"""
        self._registry = {}

    def register(self, cls):
        """Register a resource class for a prefix."""
        self._registry[cls.prefix] = cls

    def listResourcePrefixes(self):
        """Return the list of resource types."""
        return self._registry.keys()

    def makeResource(self, prefix, **kw):
        """Factory to make a resource using given prefix.

        If the resource is prefixed, the keyword 'localname' is required.
        """
        try:
            cls = self._registry[prefix]
        except KeyError:
            raise KeyError("No registered prefix '%s'" % prefix)
        return cls(**kw)


# Singleton
ResourceRegistry = ResourceRegistry()
