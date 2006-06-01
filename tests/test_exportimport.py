# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
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
# $Id$
"""Tests for the CPSRelation export/import mechanism
"""

import unittest
from Testing import ZopeTestCase
from Products.CPSUtil.testing.genericsetup import ExportImportTestCase
from Products.CPSRelation.tests.test_redland import USE_REDLAND

ZopeTestCase.installProduct('CPSRelation')

class ExportImportTest(ExportImportTestCase):

    def beforeTearDown(self):
        ExportImportTestCase.beforeTearDown(self)
        self.clearProfileRegistry()


    def test_default_import(self):
        self.registerProfile('default', "CPS Relation", "Default profile",
                             'profiles/default', 'CPSRelation')
        self.assertEquals('portal_relations' in self.folder.objectIds(),
                          False)
        self.assertEquals('portal_serializer' in self.folder.objectIds(),
                          False)
        self.importProfile('CPSRelation:default')

        # check portal_relations
        self.assertEquals('portal_relations' in self.folder.objectIds(),
                          True)
        self.assertEquals('portal_serializer' in self.folder.objectIds(),
                          True)


    def test_default_export(self):
        self.registerProfile('default', "CPS Relation", "Default profile",
                             'profiles/default', 'CPSRelation')
        self.importProfile('CPSRelation:default')
        toc_list = [
            'export_steps.xml',
            'import_steps.xml',
            'relations.xml',
            'serializers.xml',
            ]
        self._checkExportProfile('CPSRelation/tests/profiles/default_export/',
                                 toc_list)

    def test_basic_import_graphs(self):
        self.registerProfile('basic', "CPS Relation", "Basic profile",
                             'tests/profiles/basic', 'CPSRelation')
        self.assertEquals('portal_relations' in self.folder.objectIds(), False)
        self.importProfile('CPSRelation:basic')
        self.assertEquals('portal_relations' in self.folder.objectIds(), True)
        rtool = self.folder.portal_relations
        self.assertEquals(rtool.meta_type, 'Relation Tool')
        self.assertEquals(list(rtool.objectIds()), ['iobtree_graph'])
        graph = rtool.iobtree_graph
        self.assertEquals(graph.meta_type, 'IOBTree Graph')
        self.assertEquals(graph.listRelationIds(), ['hasPart'])
        hasPart = graph._getRelation('hasPart')
        self.assertEquals(hasPart.meta_type, 'IOBTree Relation')
        property_items = [
            ('prefix', 'cps'),
            ('subject_prefix', 'docid'),
            ('object_prefix', 'docid'),
            ]
        self.assertEquals(hasPart.propertyItems(), property_items)

    def test_basic_import_serializers(self):
        self.registerProfile('basic', "CPS Relation", "Basic profile",
                             'tests/profiles/basic', 'CPSRelation')
        self.assertEquals('portal_serializer' in self.folder.objectIds(), False)
        self.importProfile('CPSRelation:basic')
        self.assertEquals('portal_serializer' in self.folder.objectIds(), True)
        stool = self.folder.portal_serializer
        self.assertEquals(stool.meta_type, 'Object Serializer Tool')
        self.assertEquals(list(stool.objectIds()), ['test_serializer'])
        serializer = stool.test_serializer
        expr = "python:[(getattr(object, 'id'), 'hasTitle', getattr(object, 'title'))]"
        bindings = (
            'rdf http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'exp http://www.example.org/',
            )
        property_items = [
            ('serialization_expr', expr),
            ('namespace_bindings', bindings)
            ]
        self.assertEquals(serializer.meta_type, 'Object Serializer')
        self.assertEquals(serializer.propertyItems(), property_items)
        # check that properties have been processed
        self.assertNotEquals(serializer.serialization_expr_c, None)

    def test_basic_export(self):
        self.registerProfile('basic', "CPS Relation", "Basic profile",
                             'tests/profiles/basic', 'CPSRelation')
        self.importProfile('CPSRelation:basic')
        toc_list = [
            'export_steps.xml',
            'import_steps.xml',
            'relations.xml',
            'relations/iobtree_graph.xml',
            'serializers.xml',
            'serializers/test_serializer.xml',
           ]
        self._checkExportProfile('CPSRelation/tests/profiles/basic',
                                 toc_list)


    if USE_REDLAND:
        # additionnal test for redland graphs

        def test_redland_import(self):
            self.registerProfile('redland', "CPS Relation", "Redland profile",
                                 'tests/profiles/redland', 'CPSRelation')
            self.assertEquals('portal_relations' in self.folder.objectIds(), False)
            self.importProfile('CPSRelation:redland')
            self.assertEquals('portal_relations' in self.folder.objectIds(), True)
            rtool = self.folder.portal_relations
            self.assertEquals(rtool.meta_type, 'Relation Tool')
            self.assertEquals(list(rtool.objectIds()), ['redland_graph'])
            graph = rtool.redland_graph
            bindings = (
                'rdf http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                'exp http://www.example.org/',
                )
            property_items = [
                ('backend', 'mysql'),
                ('namespace_bindings', bindings),
                ('bdb_path', ''),
                # FIXME change that string into a readable one
                ('mysql_options', '"host=\'localhost\',port=3306,user=\'test\',password=\'pass\'"'),
                ('mysql_database', 'db_name'),
                ]
            self.assertEquals(graph.meta_type, 'Redland Graph')
            self.assertEquals(graph.propertyItems(), property_items)

        def test_redland_export(self):
            self.registerProfile('redland', "CPS Relation", "Redland profile",
                                 'tests/profiles/redland', 'CPSRelation')
            self.importProfile('CPSRelation:redland')
            toc_list = [
                'export_steps.xml',
                'import_steps.xml',
                'relations.xml',
                'relations/redland_graph.xml',
               ]
            self._checkExportProfile('CPSRelation/tests/profiles/redland',
                                     toc_list)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ExportImportTest),
        ))

