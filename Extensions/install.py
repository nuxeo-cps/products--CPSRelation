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
CPSRelation Installer

Howto use the CPSRelation installer :
 - Log into the ZMI as manager
 - Go to your CPS root directory
 - Create an External Method with the following parameters:

     id            : cpsrelation_install (or whatever)
     title         : CPSRelation Install (or whatever)
     Module Name   : CPSRelation.install
     Function Name : install

 - save it
 - then click on the test tab of this external method
"""

from Products.CMFCore.utils import getToolByName

profile_ids = (
    'CPSRelation:default',
    )

def install(self, REQUEST):
    # run extension profiles in given order
    setup_tool = getToolByName(self, 'portal_setup')
    for profile_id in profile_ids:
        setup_tool.importProfile('profile-' + profile_id)
    msg = 'Install done'
    if REQUEST is not None:
        url = REQUEST.URL0 + '/manage_main?manage_tabs_message=' + msg
        REQUEST.RESPONSE.redirect(url)
    return msg
