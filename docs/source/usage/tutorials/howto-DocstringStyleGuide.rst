..  ****************************************************************************
    Copyright(c) 2024 RoXimn. All rights reserved.

    This work is licensed under the Creative Commons Attribution 4.0 International License.
    To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.

    Author:      RoXimn <roximn@rixir.org>
    ****************************************************************************

==========================
Style Guide for Docstrings
==========================

..  contents:: Contents
    :local:
    :class: well

Abstract
========

This document details the reST semantics and conventions used in the docstrings.

The aim is to standardize the high-level structure of docstrings:

*   what they should contain? and
*   how to say it?

Specification [#PEP0257]_
=========================

What is a Docstring?
--------------------
A docstring is a string literal that occurs as the first statement in
a module, function, class, or method definition.  Such a docstring
becomes the ``__doc__`` special attribute of that object.

All modules, all functions and all classes in a module **should have**
docstrings. Public methods (including the ``__init__`` constructor) should also
have docstrings.  A package may be documented in the module docstring of
the ``__init__.py`` file in the package directory.

String literals occurring elsewhere in Python code may also act as
documentation.  They are not recognized by the Python bytecode
compiler and are not accessible as runtime object attributes (i.e. not
assigned to ``__doc__``), but two types of extra docstrings may be
extracted by software tools:

1. String literals occurring immediately after a simple assignment at
   the top level of a module, class, or ``__init__`` method are called
   "attribute docstrings".

2. String literals occurring immediately after another docstring are
   called "additional docstrings".

Please see PEP 0258, "Docutils Design Specification" [#PEP0258]_, for a
detailed description of attribute and additional docstrings.

For consistency, always use ``"""triple double quotes"""`` around
docstrings.  Use ``r"""raw triple double quotes"""`` if you use any
backslashes in your docstrings.  For Unicode docstrings, use
``u"""Unicode triple-quoted strings"""``.

There are two forms of docstrings: one-liners and multi-line
docstrings.


One-line Docstrings
-------------------
One-liners as obvious from name *should* really fit on one line.  For example::

    def kos_root():
        """Return the pathname of the KOS root directory."""
        global _kos_root
        if _kos_root: return _kos_root
        ...

Notes:

-   Triple quotes **should be** used even though the string fits on one line.
    This makes it easy to later expand it.

-   The closing quotes are on the same line as the opening quotes.

-   There is no blank line before the docstring.

-   The docstring is a phrase ending in a period.  It prescribes the
    function or method's effect as a command ("Do this", "Return that"),
    not as a description; e.g. don't write "Returns the pathname ...".

-   The one-line docstring should NOT be a "signature" reiterating the
    function/method parameters (which can be obtained by introspection).
    Don't do::

        def function(a, b):
            """function(a, b) -> list"""

    The preferred form for such a docstring would be something like::

        def function(a, b):
            """Do X and return a list."""

    (Of course "Do *X*" is to be replaced by a useful description!)


Multi-line Docstrings
---------------------
Multi-line docstrings consist of a summary line just *like a one-line
docstring*, followed by a blank line, followed by a more elaborate
description.  It is important that it fits on one line and is separated from
the rest of the docstring by a blank line.  The summary line should be placed
on the next line as the opening triple quotes. The entire
docstring is indented the same as the quotes at its first line (see
example below).

Insert a blank line after all docstrings (one-line or multi-line) that
document a class -- generally speaking, the class's methods are
separated from each other by a single blank line, and the docstring
needs to be offset from the first method by a blank line.

The docstring for a **module** should generally list the classes,
exceptions and functions (and any other objects) that are exported by
the module, with a one-line summary of each.  (These summaries
generally give less detail than the summary line in the object's
docstring.)

The docstring for a **package** (i.e., the docstring of the
package's ``__init__.py`` module) should also list the modules and
subpackages exported by the package.

The docstring for a **function** or method should summarize its behavior
and document its arguments, return value(s), side effects, exceptions
raised, and restrictions on when it can be called (all if applicable).
Optional arguments should be indicated.  It should be documented
whether keyword arguments are part of the interface.

The docstring for a **class** should summarize its behavior and list the
public methods and instance variables.  If the class is intended to be
subclassed, and has an additional interface for subclasses, this
interface should be listed separately (in the docstring).  The class
constructor should be documented in the docstring for its ``__init__``
method.  Individual methods should be documented by their own
docstring.

If a class subclasses another class and its behavior is mostly
inherited from that class, its docstring should mention this and
summarize the differences.  Use the verb "override" to indicate that a
subclass method replaces a superclass method and does not call the
superclass method; use the verb "extend" to indicate that a subclass
method calls the superclass method (in addition to its own behavior).

Python is case sensitive and the argument names can be used for keyword
arguments, so the docstring should document the correct argument names.
It is best to list each argument on a separate line.  For example::

    def complex(real = 0.0, imag = 0.0):
        """
        Form a complex number.

        Keyword arguments:
        real -- the real part (default 0.0)
        imag -- the imaginary part (default 0.0)
        """

        if imag == 0.0 and real == 0.0:
            return complex_zero
        ...

Place the closing quotes on a line by themselves, followed by a blank line,
separating it from the immediate code.


Handling Docstring Indentation
------------------------------
Docstring processing tools will strip a uniform amount of indentation
from the second and further lines of the docstring, equal to the
minimum indentation of all non-blank lines after the first line.  Any
indentation in the first line of the docstring (i.e., up to the first
newline) is insignificant and removed.  Relative indentation of later
lines in the docstring is retained.  Blank lines should be removed
from the beginning and end of the docstring.

Since code is much more precise than words, here is an implementation
of the algorithm::

    def trim(docstring):
        if not docstring:
            return ''
        # Convert tabs to spaces (following the normal Python rules)
        # and split into a list of lines:
        lines = docstring.expandtabs().splitlines()
        # Determine minimum indentation (first line doesn't count):
        indent = sys.maxint
        for line in lines[1:]:
            stripped = line.lstrip()
            if stripped:
                indent = min(indent, len(line) - len(stripped))
        # Remove indentation (first line is special):
        trimmed = [lines[0].strip()]
        if indent < sys.maxint:
            for line in lines[1:]:
                trimmed.append(line[indent:].rstrip())
        # Strip off trailing and leading blank lines:
        while trimmed and not trimmed[-1]:
            trimmed.pop()
        while trimmed and not trimmed[0]:
            trimmed.pop(0)
        # Return a single string:
        return '\n'.join(trimmed)

The docstring in this example contains two newline characters and is
therefore 3 lines long.  The first and last lines are blank::

    def foo():
        """
        This is the second line of the docstring.
        """

To illustrate::

    >>> print repr(foo.__doc__)
    '\n    This is the second line of the docstring.\n    '
    >>> foo.__doc__.splitlines()
    ['', '    This is the second line of the docstring.', '    ']
    >>> trim(foo.__doc__)
    'This is the second line of the docstring.'

Once trimmed, these docstrings are equivalent::

    def foo():
        """A multi-line
        docstring.
        """

    def bar():
        """
        A multi-line
        docstring.
        """

Napoleon & Google Python Style Guide
====================================
**ReStructuredText** is great, but it creates visually dense, hard to read
*docstrings*. It can tiring to write docstrings that look like this::

    :param path: The path of the file to wrap
    :type path: str
    :param field_storage: The :class:`FileStorage` instance to wrap
    :type field_storage: FileStorage
    :param temporary: Whether or not to delete the file when the File
       instance is destructed
    :type temporary: bool
    :returns: A buffered writable file descriptor
    :rtype: BufferedFileStorage

Compare this above jumble to the same thing rewritten according to the
`Google Python Style Guide <http://google.github.io/styleguide/pyguide.html>`_::

    Args:
        path (str): The path of the file to wrap
        field_storage (FileStorage): The :class:`FileStorage` instance to wrap
        temporary (bool): Whether or not to delete the file when the File
           instance is destructed

    Returns:
        BufferedFileStorage: A buffered writable file descriptor


which makes ``docstring`` documentation more succinct and manageable.

Napoleon is a *Sphinx extension* that enables Sphinx to parse both **NumPy**
and **Google** style docstrings.

Napoleon is a pre-processor that parses *NumPy* and *Google* style
docstrings and converts them to reStructuredText before Sphinx attempts to
parse them. This happens in an intermediate step while Sphinx is processing
the documentation, so it doesn't modify any of the docstrings in your actual
source code files.

Napoleon interprets every docstring that ``Sphinx autodoc`` can find,
including docstrings on: ``modules``, ``classes``, ``attributes``,
``methods``, ``functions``, and ``variables``. Inside each docstring,
specially formatted `Supported Docstring Sections`_ are parsed and converted to
reStructuredText.

All standard reStructuredText formatting still works as expected.

Napoleon supports two styles of docstrings: **Google** and **NumPy**. The
main difference between the two styles is that Google uses indention to
separate sections, whereas NumPy uses underlines.

NumPy style tends to require more vertical space, whereas Google style
tends to use more horizontal space. Google style tends to be easier to
read for short and simple docstrings, whereas NumPy style tends be easier
to read for long and in-depth docstrings.

The style used in `RekhtaNaveesApplication` is the Google style.


..  secSupportedDocstringSections:

Supported Docstring Sections
----------------------------

All of the following section headers are supported:

*   ``Args`` *(alias of Parameters)*
*   ``Arguments`` *(alias of Parameters)*
*   ``Attributes``
*   ``Example``
*   ``Examples``
*   ``Keyword Args`` *(alias of Keyword Arguments)*
*   ``Keyword Arguments``
*   ``Methods``
*   ``Note``
*   ``Notes``
*   ``Other Parameters``
*   ``Parameters``
*   ``Return`` *(alias of Returns)*
*   ``Returns``
*   ``Raises``
*   ``References``
*   ``See Also``
*   ``Todo``
*   ``Warning``
*   ``Warnings`` *(alias of Warning)*
*   ``Warns``
*   ``Yield`` *(alias of Yields)*
*   ``Yields``

A Complete Example
------------------
..  literalinclude:: exampleGoogle.py
    :language: python
    :linenos:


References
==========
..  [#PEP0257] :pep:`0257` --- Docstring Conventions

..  [#PEP0258] :pep:`0258` --- Docutils Design Specification

..  seealso::

    -   :pep:`0008` --- Style Guide for Python Code
    -   :doc:`/usage/tutorials/howto-CreateContent`
    -   :doc:`/usage/tutorials/howto-OrganizeDocumentation`


.. raw:: latex

   \pagebreak

