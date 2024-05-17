..  ****************************************************************************
    Copyright(c) 2024 RoXimn. All rights reserved.

    This work is licensed under the Creative Commons Attribution 4.0 International License.
    To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.

    Author:      RoXimn <roximn@rixir.org>
    ****************************************************************************

***************************************
Guidelines for Organizing Documentation
***************************************
..  contents:: Contents
    :local:
    :class: well


Introduction [#XpertPyBook]_
============================
An easier way to guide your readers and your writers is to provide each one of
them with helpers and guidelines.

From a writer's point of view, this is done by having a set of reusable templates
together with a guide that describes how and when to use them in a project. It is
called a **documentation portfolio**.

From a reader point of view, being able to browse the documentation with
no pain, and getting used to finding the info efficiently, is done by building a
**documentation landscape**.


Building the Portfolio
======================
There are many kinds of documents a software project can have, from low-level
documents that refer directly to the code, to design papers that provide a high-level
overview of the application.

For instance, Scott Ambler defines an extensive list of document types in
his book `Agile Modeling <http://www.agilemodeling.com/essays/
agileArchitecture.htm>`_. He builds a portfolio from early specifications to
operations documents. Even the project management documents are covered, so the
whole documenting needs are built with a standardized set of templates.
Since a complete portfolio is tightly related to the methodologies used to build the
software, this chapter will only focus on a common subset that you can complete
with your specific needs. Building an efficient portfolio takes a long time, as it
captures your working habits.

A common set of documents in software projects can be classified in three categories:

*   Design
        All documents that provide architectural information, and low-level
        design information, such as class diagrams, or database diagrams
*   Usage
        Documents on how to use the software; this can be in the shape of a
        cookbook and tutorials, or a module-level help
*   Operations
        Provide guidelines on how to deploy, upgrade, or operate
        the software


Design
------
The purpose of design documentation is to describe how the software works and
how the code is organized. It is used by developers to understand the system but
is also a good entry point for people who are trying to understand how the
application works.

The different kinds of design documents a software can have are:

*   Architecture overview
*   Database models
*   Class diagrams with dependencies and hierarchy relations
*   User interface wireframes
*   Infrastructure description

Mostly, these documents are composed of some diagrams and a minimum amount
of text. The conventions used for the diagrams are very specific to the team and the
project, and this is perfectly fine as long as it is consistent.

..  note::
    UML provides thirteen diagrams that cover most aspects in a
    software design. The class diagram is probably the most used one,
    but it is possible to describe every aspect of software with it. See
    `UML Diagrams <http://en.wikipedia.org/wiki/Unified_Modeling_Language#Diagrams>`_.

Following a specific modeling language such as UML is not often fully done,
and teams just make up their own way throughout their common experience.
They pick up good practice from UML or other modeling languages, and create
their own recipes.

For instance, for **architecture overview diagrams**, some designers just draw boxes
and arrows on a whiteboard without following any particular design rules and take
a picture of it. Others work with simple drawing programs such as
`Dia <https://wiki.gnome.org/Apps/Dia>`_ or Microsoft Visio (not open source,
so not free), since it is enough to understand the design.

**Database model diagrams** depend on the kind of database you are using. There
are complete data modeling software applications that provide drawing tools to
automatically generate tables and their relations. But this is overkill in Python most
of the time. If you are using an ORM such as SQLAlchemy (for instance), simple
boxes with lists of fields, together with table relations as shown in Chapter 6 are
enough to describe your mappings before you start to write them.

**Class diagrams** are often simplified UML class diagrams: There is no need in Python
to specify the protected members of a class, for instance. So the tools used for an
architectural overview diagram fit this need too.

**User interface diagrams** depend on whether you are writing a web or a desktop
application. Web applications often describe the center of the screen, since the
header, footer, left, and right panels are common. Many web developers just
handwrite those screens and capture them with a camera or a scanner. Others
create prototypes in HTML and make screen snapshots. For desktop applications,
snapshots on prototype screens, or annotated mock-ups made with tools such as
Gimp or Photoshop are the most common way.

**Infrastructure overview diagrams** are like architecture diagrams, but they focus
on how the software interacts with third-party elements, such as mail servers,
databases, or any kind of data streams.

Common Template
^^^^^^^^^^^^^^^
The important point when creating such documents is to make sure the target
readership is perfectly known, and the content scope is limited. So a generic template
for design documents can provide a light structure with a little advice for the writer.
Such a structure can include:

*   Title
*   Author
*   Tags (keywords)
*   Description (abstract)
*   Target (Who should read this?)
*   Content (with diagrams)
*   References to other documents

The content should be three or four screens (a 1024x768 average screen) at the most,
to be sure to limit the scope. If it gets bigger, it should be split into several documents
or summarized.

The template also provides the author's name and a list of tags to manage its
evolutions and ease its classification.


Usage
-----
Usage documentation describes how a particular part of the software works. This
documentation can describe low-level parts such as how a function works, but also
high-level parts such command-line arguments for calling the program. This is the
most important part of documentation in framework applications, since the target
readership is mainly the developers that are going to reuse the code.

The three main kinds of documents are:

*   `Recipe`_
        A short document that explains how to do something. This kind of
        document targets one readership and focuses on one specific topic.
*   `Tutorial`_
        A step-by-step document that explains how to use a feature of the
        software. This document can refer to recipes, and each instance is intended to
        one readership.
*   `Module Helper`_
        A low-level document that explains what a module contains.

This document could be shown (for instance) when you call the help built-in
over a module.

Recipe
^^^^^^
A recipe answers a very specific problem and provides a solution to resolve it.
For example, ActiveState provides a Python Cookbook online (a cookbook is a
collection of recipes), where developers can describe how to do something in Python
(see `ActiveState Recipes <http://code.activestate.com/recipes/langs/python>`_).

These recipes must be short and are structured like this:

*   Title
*   Submitter
*   Last updated
*   Version
*   Category
*   Description
*   Source (the source code)
*   Discussion (the text explaining the code)
*   Comments (from the web)

Often, they are one-screen long and do not go into great details. This structure
perfectly fits a software's needs and can be adapted in a generic structure, where
the target readership is added and the category replaced by tags:

*   Title (short sentence)
*   Author
*   Tags (keywords)
*   Who should read this?
*   Prerequisites (other documents to read, for example)
*   Problem (a short description)
*   Solution (the main text, one or two screens)
*   References (links to other documents)

The date and version are not useful here, since we will see later that the
documentation is managed like source code in the project.

Tutorial
^^^^^^^^
A tutorial differs from a recipe in its purpose. It is not intended to resolve an isolated
problem, but rather describes how to use a feature of the application step by step.
This can be longer than a recipe and can concern many parts of the application.

For example, Django provides a list of tutorials on its website. `Writing your
first Django App, part 1 <https://docs.djangoproject.com/en/1.9/intro/tutorial01/>`_
explains in ten screens how to build an application with Django.

A structure for such a document can be:

*   Title (short sentence)
*   Author
*   Tags (words)
*   Description (abstract)
*   Who should read this?
*   Prerequisites (other documents to read, for example)
*   Tutorial (the main text)
*   References (links to other documents)

Module Helper
^^^^^^^^^^^^^
The last template that can be added in our collection is the module helper template.
A module helper refers to a single module and provides a description of its contents,
together with usage examples.

Some tools can automatically build such documents by extracting the docstrings
and computing module help using pydoc, like `Epydoc <http://epydoc.sourceforge.net>`_.
So it is possible to generate an extensive documentation based
on API introspection. This kind of documentation is often provided in Python
frameworks. For instance Plone provides a `server <http://api.plone.org>`_ that
keeps an up-to-date collection of module helpers.

The main problems with this approach are:

*   There is no smart selection performed over the modules that are really
    interesting to document.
*   The code can be obfuscated by the documentation.

Furthermore, a module documentation provides examples that sometimes refer to
several parts of the module, and are hard to split between the functions' and classes'
docstrings. The module ``docstring`` could be used for that purpose by writing a text
at the top of the module. But this ends in having a hybrid file composed of a block
of text, then a block of code. This is rather obfuscating when the code represents less
than 50% of the total length. If you are the author, this is perfectly fine. But when
people try to read the code (not the documentation), they will have to jump the
docstrings part.

Another approach is to separate the text in its own file. A manual selection can then
be operated to decide which Python module will have its module helper file. The
documents can then be separated from the code base and allowed to live their own
life, as we will see in the next part. This is how Python is documented.

Many developers will disagree on the fact that doc and code separation is better than
docstrings. This approach means that the documentation process is fully integrated
in the development cycle; otherwise it will quickly become obsolete. The docstrings
approach solves this problem by providing proximity between the code and its usage
example, but doesn't bring it to a higher level: a document that can be used as part of
a plain documentation.

The template for Module Helper is really simple, as it contains just a little metadata
before the content is written. The target is not defined since it is the developers who
wish to use the module:

*   Title (module name)
*   Author
*   Tags (words)
*   Content


Operations
----------
Operation documents are used to describe how the software can be operated.

For instance:

*   Installation and deployment documents
*   Administration documents
*   "Frequently Asked Questions" documents that help the users when a
    failure occurs
*   Documents that explain how people can ask for help or provide feedback

These documents are very specific, but they can probably use the tutorial template
defined previously.


Make Your Own Portfolio
=======================
The templates that we discussed earlier are just a basis that you can use to document
your software.

Keep in mind the light but sufficient approach for project documentation: Each
document added should have a clearly defined target readership and should fill a
real need. Documents that don't add a real value should not be written.


Building the Landscape
======================
The document portfolio built in the previous section provides a structure at
document level, but does not provide a way to group and organize it to build
the documentation the readers will have. This is what Andreas Rüping calls a
document landscape, referring to the mental map the readers use when they browse
documentation. He came up with the conclusion that the best way to organize
documents is to build a logical tree.

In other words, the different kinds of documents composing the portfolio need to
find a place to live within a tree of directories. This place must be obvious to the
writers when they create the document and to the readers when they are looking
for it.

A great helper in browsing documentation is index pages at each level that can drive
writers and readers.

Building a document landscape is done in two steps:

*   Building a tree for the producers (*the writers*)
*   Building a tree for the consumers (*the readers*), on the top of the
    producers' one

This distinction between producers and consumers is important since they access the
documents in different places and different formats.


Producer's Layout
-----------------
From a producer's point of view, each document is processed exactly like a Python
module. It should be stored in the version control system and worked like code.
Writers do not care about the final appearance of their prose and where it is
available. They just want to make sure that they are writing a document, so it is the
single source of truth on the topic covered.

reStructuredText files stored in a folder tree are available in the version control
system together with the software code, and are a convenient solution to build the
documentation landscape for producers.

The simplest way to organize the tree is to group documents by nature:

..  code-block:: console

    $ cd atomisator
    $ find docs
    docs
    docs/source
    docs/source/design
    docs/source/operations
    docs/source/usage
    docs/source/usage/cookbook
    docs/source/usage/modules
    docs/source/usage/tutorial

Notice that the tree is located in a source folder because the docs folder will be used
as a root folder to set up a special tool in the next section.

From there, an ``index.txt`` file can be added at each level (besides the root),
explaining what kind of documents the folder contains, or summarizing what
each sub-folder contains. These index files can define a listing of the documents
they contain. For instance, the operation folder can contain a list of operations
documents available:

..  code-block:: restructuredtext

    ==========
    Operations
    ==========
    This section contains operations documents:

    −   How to install and run Atomisator
    −   How to install and manage a PostgreSQL database

    for Atomisator

So that people do not forget to update them, we can have lists generated
automatically.


Consumer's Layout
-----------------
From a consumer's point of view, it is important to work out the index files and to
present the whole documentation in a format that is easy to read and looks good.
Web pages are the best pick and are easy to generate from reStructuredText files.

`Sphinx <http://sphinx-doc.org>`_ is a set of scripts and ``docutils`` extensions that
can be used to generate an HTML structure from our text tree. This tool is used (for
instance) to build the Python documentation, and many projects are now using it for
their documentation. Among its built-in features, it produces a really nice browsing
system, together with a light but sufficient client-side JavaScript search engine. It
also uses ``pygments`` for rendering code examples, which produces really nice
syntax highlights.

Sphinx can be easily configured to stick with the document landscape defined in the
earlier section. To install it, just call ``pip install``:

..  code-block:: console

    $ pip install sphinx

This installs a few scripts such as ``sphinx-quickstart``. This script will generate
a script together with a ``Makefile``, which can be used to generate the web
documentation every time it is needed. Let's run this script in the ``docs`` folder and
answer its questions:

..  code-block:: none

    $ sphinx-quickstart
    Welcome to the Sphinx quickstart utility.
    Enter the root path for documentation.
    > Root path for the documentation [.]:
    > Separate source and build directories (y/n) [n]: y
    > Name prefix for templates and static dir [.]:
    > Project name: Atomisator
    > Author name(s): Tarek Ziadé
    > Project version: 0.1.0
    > Project release [0.1.0]:
    > Source file suffix [.rst]: .txt
    > Name of your master document (without suffix) [index]:
    > Create Makefile? (y/n) [y]: y
    Finished: An initial directory structure has been created.
    You should now populate your master file ./source/index.txt and create
    other documentation
    source files. Use the sphinx-build.py script to build the docs, like so:
    make <builder>

This adds a ``conf.py`` file in the source folder that contains the configuration
defined through the answers, and an ``index.txt`` file at the root, together with a
``Makefile`` in ``docs``.

Running ``make html`` will then generate a tree in build:

..  code-block:: none

    Running Sphinx v1.3.3
    loading pickled environment... done
    building [mo]: targets for 0 po files that are out of date
    building [html]: targets for 1 source files that are out of date
    updating environment: 0 added, 1 changed, 0 removed

    looking for now-outdated files... none found
    pickling environment... done
    checking consistency... done
    preparing documents... done

    generating indices... genindex
    writing additional pages... search
    copying static files... done
    copying extra files... done
    dumping search index in English (code: en) ... done
    dumping object inventory... done
    build succeeded.

The documentation will then be available in ``build/html``, starting at ``index.html``.

Besides the HTML versions of the documents, the tool also builds automatic pages
such as a module list and an index. Sphinx provides a few ``docutils`` extensions to
drive these features. The main ones are:

*   A directive that builds a table of contents
*   A marker that can be used to register a document as a module helper
*   A marker to add an element in the index

Working on the Index Pages
^^^^^^^^^^^^^^^^^^^^^^^^^^
Sphinx provides a ``toctree`` directive that can be used to inject a table of contents in
a document, with links to other documents. Each line must be a file with its relative
path, starting from the current document. Glob-style names can also be provided to
add several files that match the expression.

For example, the index file in the cookbook folder, which we have previously
defined in the producer's landscape, can look like this:

..  code-block:: rst

    ========
    Cookbook
    ========
    Welcome to the CookBook.
    Available recipes:
    ..  toctree::
        :glob:
        *

    With this syntax, the HTML page will display a list of all reStructuredText
    documents available in the ``cookbook`` folder. This directive can be used in all index
    files to build a browseable documentation.

Registering Module Helpers
^^^^^^^^^^^^^^^^^^^^^^^^^^
For module helpers, a marker can be added so that it is automatically listed and
available in the module's index page:

..  code-block:: rst

    =======
    session
    =======
    ..  module:: db.session
        The module session...

Notice that the ``db`` prefix here can be used to avoid module collision. Sphinx will
use it as a module category and will group all modules that start with db. in
this category.

In your documentation, you can use this feature when you have a lot of modules.

Adding Index Markers
^^^^^^^^^^^^^^^^^^^^
Another option can be used to fill the index page by linking the document to
an entry:

..  code-block:: rst

    =======
    session
    =======
    ..  module:: db.session
    ..  index::
        Database Access
            Session
            The module session...

Two new entries, ``Database Access`` and ``Session`` will be added in the index page.

Cross-references
^^^^^^^^^^^^^^^^
Finally, Sphinx provides an inline markup to set cross-references. For instance, a link
to a module can be done like this:

::

    :mod:`db.session`

Where ``:mod:`` is the module marker's prefix and ```db.session``` is the name of the
module to be linked to (as registered previously), keep in mind that ``:mod:`` as well
as the previous elements are the specific directives introduced in reSTructuredText
by Sphinx.


Summary
=======
This chapter explained in detail how to:

*   Use a few rules for efficient writing
*   Use reStructuredText, the Pythonistas LaTeX
*   Build a document portfolio and landscape
*   Use Sphinx to generate nice web documentation

The hardest thing to do when documenting a project is to keep it accurate and up
to date. Making the documentation part of the code repository makes it a lot easier.

From there, every time a developer changes a module, he or she should change the
corresponding documentation as well.

This can be quite difficult in big projects, and adding a list of related documents in
the header of the modules can help in that case.

A complementary approach to make sure the documentation is always accurate is to
combine the documentation with tests through doctests.


References
==========
..  [#XpertPyBook] Tarek Ziadé. Documenting Your Project.
    Expert Python Programming: Best practices for designing, coding, and
    distributing your Python software, First ed. Birmingham, UK:
    Packt Publishing; 2008. pp. 223.

    This document is a copy of the aptly written chapter on the
    topic by `Tarek Ziadé <http://ziade.org/>`_ in his book
    `Expert Python Programming <https://www.packtpub.com/application-development/expert-python-programming>`_.


.. raw:: latex

   \pagebreak

