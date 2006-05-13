====================
CPSRelation - README
====================

$Id$


Contents
========

* `Features`_
* `Installation notes`_

  - `Requirements`_
  - `CPSRelation Installation`_
  - `Redland Installation`_
  - `pydot Installation`_

Features
========

CPSRelation provides an API to manage relations between objects.

Interfaces have been defined to be able to use different types of graphs
for storing and managing relations. Currently, supported graphs are:

- simple IOBTrees managing relations between integer unique identifiers and
  tuples of integer unique identifiers. This is the historical relations
  management, useful to store relations between CPS documents, using ther
  docid in the repository as unique integer identifiers.
- Redland graphs managing RDF graphs provided by Redland using the python
  binding.

Redland is required to use the two last type of graphs, but is not required
for the product installation and use of simple graphs.

A tool (portal_relations) is able to manage several and different kinds of
graphs.

Another tool (portal_serializer) has been designed to provide object
serializations via pluggable TALES expressions. This tool currently requires
Redland to provide XML serializations following the RDF/XML syntax.
If the pydot Python library is available, this tool also provides drawings
representing the graph content.

Additional information can be found in the doc/ directory.


Installation notes
==================

Requirements
------------

CPSRelation requires:

- Zope (2.8.1 at least is recommended)
- CMF
- CPSInstaller
- CPSUtil


CPSRelation installation
------------------------

CMFQuickInstaller can be used to install this Zope product.

Otherwise, the usual way to install a CPS product applies:

- Log into the ZMI as manager
- Go to your CPS root directory
- Create an External Method with the following parameters::

    id            : cpsrelation_install (or whatever)
    title         : CPSRelation Install (or whatever)
    Module Name   : CPSRelation.install
    Function Name : install

- save it
- then click on the test tab of this external method


Redland installation
--------------------

Redland is a set of free software packages providing RDF related features,
written in C.

Packages are:

- Raptor RDF Parser Toolkit
- Rasqal RDF Query Library
- Redland RDF Application Framework
- Redland Language Bindings

Installation for CPSRelation requires the installation of Raptor, Rasqal,
Redland, and the Redland Python binding.

Tests have been made using following versions, with Python 2.3.5 and 2.4.2:

- raptor-1.4.7
- rasqal-0.9.10
- redland-1.0.2.
- redland-bindings-1.0.2.1

Following Ubuntu packages have also been tested:

- librdf0           1.0.2-2ubuntu1
- python2.3-librdf  1.0.2.1-1ubuntu1
- python2.4-librdf  1.0.2.1-1ubuntu1

Please refer to the Redland documentation and installation instructions at
http://librdf.org/.

- Take care of library path settings when installing packages because rasqal
  requires raptor, and redland requires raptor and rasqal.
- packages like libxml2-dev and libdb4.3-dev, and a C++ compiler like g++
  may have to be installed too.

For information, our build summaries were:

Raptor build summary::

  RDF parsers available     : rdfxml ntriples turtle rss-tag-soup grddl
  RDF parsers enabled       : rdfxml ntriples turtle rss-tag-soup grddl
  RDF serializers available : rdfxml rdfxml-abbrev ntriples
  RDF serializers enabled   : rdfxml rdfxml-abbrev ntriples
  XML parser                : libxml(system 2.6.20)
  WWW library               : libxml(system 2.6.20)

Rasqal build summary::

  RDF query languages available : rdql sparql
  RDF query languages enabled   : rdql sparql
  Triples source                : raptor 1.4.7

Redland build summary::

  Berkeley/Sleepycat DB   : Version 4.3 (library db-4.3 in /usr/lib)
  Triple stores available : file hashes(memory) hashes(bdb 4.3)
  Triple stores enabled   : memory file hashes
  RDF parsers             : raptor(system 1.4.7)
  RDF query               : rasqal(system 0.9.10)
  Content digests         : md5(openssl) sha1(openssl) ripemd160(openssl)

Redland build summary (using mysql backend too)::

  Berkeley/Sleepycat DB   : Version 4.3 (library db-4.3 in /usr/lib)
  Triple stores available : file hashes(memory) hashes(bdb 4.3) mysql(4.1.10a)
  Triple stores enabled   : memory file hashes mysql
  RDF parsers             : raptor(system 1.4.7)
  RDF query               : rasqal(system 0.9.10)
  Content digests         : md5(openssl) sha1(openssl) ripemd160(openssl)

Redland build summary (installing the Python binding)::

  Redland:              system 1.0.2
  Language APIs built:    python


Mysql notes:

Packages installed:

- mysql-common
- mysql-server
- mysql-client
- libmysqlclient14-dev

Rebuild Redland with configure option "--with-mysql=yes".
Re-installing redland-binding is not necessary.
Database with same name than the graph in portal_relations has to be
created, the rest is done automatically.

pydot Installation
------------------

pydot is a Python interface that allows to create graphs in GraphViz's dot
language. It is used in CPSRelation to provide graphic representations of
relation instances.

Please refer to the pydot documentation and installation instructions at
http://dkbza.org/pydot.html

GraphViz is required.
pyparsing is required too although it is not used for our purpose. The
dependency can be easily broken, though: commenting out one pyparsing import
before installing pydot is enough with version 0.9.10.
