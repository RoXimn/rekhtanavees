..  ****************************************************************************
    Copyright(c) 2024 RoXimn. All rights reserved.

    This work is licensed under the Creative Commons Attribution 4.0 International License.
    To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.

    Author:      RoXimn <roximn@rixir.org>
    ****************************************************************************

*******************************
Guidelines for Creating Content
*******************************
..  contents:: Contents
    :local:
    :class: well


Rules of Technical Writing [#XpertPyBook]_
==========================================
Writing good documentation is easier in many aspects than writing a code. Most
developers think it is very hard, but by following a simple set of rules it becomes
really easy.

We are not talking here about writing a book of poems but a comprehensive piece of
text that can be used to understand a design, an API, or anything that makes up the
code base.

Every developer is able to produce such material, and this section provides seven
rules that can be applied in all cases.

#.  `Write in Two Steps`_:
        *Focus* on ideas, and then on *reviewing* and shaping
        your text.
#.  `Target the Readership`_:
        *Who* is going to read it?
#.  `Use a Simple Style`_:
        Keep it straight and simple. Use *good* grammar.
#.  `Limit the Scope of the Information`_:
        Introduce *one* concept at a time.
#.  `Use Realistic Code Examples`_:
        *Foo*\ s and *bar*\ s should be dropped.
#.  `Use a Light but Sufficient Approach`_:
        You are not writing a *book*!
#.  `Use Templates`_:
        Help the readers to get *habits*.


Write in Two Steps
------------------
Peter Elbow, in `Writing with Power <https://global.oup.com/academic/product/writing-with-power-9780195120189>`_,
explains that it is almost impossible for any
human being to produce a perfect text in one shot. The problem is that many
developers write documentation and try to directly come up with a perfect text.

The only way they succeed in this exercise is by stopping the writing after every
two sentences to read them back, and do some corrections. This means that they are
focusing both on the content and the style of the text.

This is too hard for the brain and the result is often not as good as it could be. A lot
of time and energy is spent in polishing the style and shape of the text, before its
meaning is completely thought through.

Another approach is to drop the style and organization of the text and focus on
its content. All ideas are laid down on paper, no matter how they are written. The
developer starts to write a continuous stream and does not pause when he or she
makes grammatical mistakes, or for anything that is not about the content. For
instance, it does not matter if the sentences are barely understandable as long as the
ideas are written down. He or she just writes down what he wants to say, with a
rough organization.

By doing this, the developer focuses on what he or she wants to say and will
probably get more content out of his or her brain than he or she initially thought he
or she would.

Another side-effect when doing free writing is that other ideas that are not directly
related to the topic will easily go through the mind. A good practice is to write them
down on a second paper or screen when they appear, so they are not lost, and then
get back to the main writing.

The second step consists of reading back the whole text and polishing it so that it is
comprehensible to everyone. Polishing a text means enhancing its style, correcting its
faults, reorganizing it a bit, and removing any redundant information it has.

When the time dedicated to write documentation is limited, a good practice is to cut
this time in two equal durations—one for writing the content, and one to clean and
organize the text.

..  note::

    Focus on the content, and then on style and cleanliness.


Target the Readership
---------------------
When starting a text, there is a simple question the writer should consider: *Who is
going to read it*\ ?

This is not always obvious, as a technical text explains how a piece of software works,
and is often written for every person who might get and use the code. The reader can
be a manager who is looking for an appropriate technical solution to a problem, or a
developer who needs to implement a feature with it. A designer might also read it to
know if the package fits his or her needs from an architectural point of view.

Let's apply a simple rule: Each text should have only one kind of readers.

This philosophy makes the writing easier. The writer precisely knows what kind
of reader he or she is dealing with. He or she can provide a concise and precise
documentation that is not vaguely intended for all kinds of readers.
A good practice is to provide a small introductory text that explains in one sentence
what the documentation is about, and guides the reader to the appropriate part: ::

    Atomisator is a product that fetches RSS feeds and saves them in a database, with a filtering process.
    If you are a developer, you might want to look at the API description (api.txt)
    If you are a manager, you can read the features list and the FAQ (features.txt)
    If you are a designer, you can read the architecture and infrastructure notes (arch.txt)

By taking care of directing your readers in this way, you will probably produce
better documentation.

..  note::

    Know your readership before you start to write.


Use a Simple Style
------------------
Seth Godin is one of the best-selling writers on marketing topics. You might
want to read `Unleashing The Ideavirus <http://www.sethgodin.com/ideavirus/downloads/IdeavirusReadandShare.pdf>`_,
which is available for free on the Internet.

Lately, he made an analysis on his blog to try to understand why his books sold
so well. He made a list of all best sellers in the marketing area and compared the
average number of words per sentences in each one of them.

He realized that his books had the lowest number of words per sentence (thirteen
words). This simple fact, Seth explained, proved that readers prefer short and simple
sentences, rather than long and stylish ones.

By keeping sentences short and simple, your writings will consume less brain power
for their content to be extracted, processed, and then understood. Writing technical
documentation aims to provide a software guide to readers. It is not a fiction story,
and should be closer to your microwave notice than to the latest Stephen King novel.

A few tips to keep in mind are:

-   Use simple sentences; they should not be longer than two lines.
-   Each paragraph should be composed of three or four sentences, at the most,
    that express one main idea. Let your text breathe.
-   Don't repeat yourself too much: Avoid journalistic styles where ideas are
    repeated again and again to make sure they are understood.
-   Don't use several tenses. Present tense is enough most of the time.
-   Do not make jokes in the text if you are not a really fine writer. Being funny
    in a technical book is really hard, and few writers master it. If you really
    want to distill some humor, keep it in code examples and you will be fine.

..  note::

    You are not writing fiction, so keep the style as simple as possible.


Limit the Scope of the Information
----------------------------------
There's a simple sign of bad documentation in a software: You are looking for some
information that you know is present somewhere, but you cannot find it. After
spending some time reading the table of contents, you are starting to grep the files
trying several word combinations, but cannot get what you are looking for.

This happens when writers are not organizing their texts in topics. They might
provide tons of information, but it is just gathered in a monolithic or non-logical
way. For instance, if a reader is looking for a big picture of your application, he or
she should not have to read the API documentation: that is a low-level matter.

To avoid this effect, paragraphs should be gathered under a meaningful title for
a given section, and the global document title should synthesize the content in a
short phrase.

A table of contents could be made of all the section's titles.

A simple practice to compose your titles is to ask yourself: What phrase would I type
in Google to find this section?


Use Realistic Code Examples
---------------------------
Foo and bar are bad citizens. When a reader tries to understand how a piece of
code works with a usage example, having an unrealistic example will make it harder
to understand.

Why not use a real-world example? A common practice is to make sure that each
code example can be cut and pasted in a real program.

An example of bad usage is:

We have a parse function:

    >>> from atomisator.parser import parse

Let's use it:

    >>> stuff = parse('some-feed.xml')
    >>> stuff.next()
    {'title': 'foo', 'content': 'blabla'}

A better example would be when the parser knows how to return a feed content with
the parse function, available as a top-level function:

    >>> from atomisator.parser import parse

Let's use it:

    >>> my_feed = parse('http://tarekziade.wordpress.com/feed')
    >>> my_feed.next()
    {'title': 'eight tips to start with python',
    'content': 'The first tip is..., ...'}

This slight difference might sound overkill, but in fact it makes your documentation
a lot more useful. A reader can copy those lines into a shell, understands that ``parse``
uses a URL as a parameter, and that it returns an iterator that contains blog entries.

..  note::

    Code examples should be directly reusable in real programs.


Use a Light but Sufficient Approach
-----------------------------------
In most agile methodologies, documentation is not the first citizen. Making software
that works is the most important thing, over detailed documentation. So a good
practice, as Scott Ambler explains in his book *Agile Modeling: Effective Practices for
Extreme Programming and the Unified Process*, is to define the real documentation
needs, rather than creating an exhaustive set of documents.

For instance, a single document that explains how Atomisator works for
administrators is sufficient. There is no other need for them than to know how to
configure and run the tool. This document limits its scope to answer to one question:
How do I run Atomisator on my server?

Besides readership and scope, limiting the size of each section written for the
software to a few pages is a good idea. By making each section four pages long at
the most, the writer will have to synthesize his or her thought. If it needs more, it
probably means that the software is too complex to explain or use.

..  note::

    Working software over comprehensive documentation

    --- The Agile Manifesto.


Use Templates
-------------
Every page on Wikipedia is similar. There are boxes on the left side that are used
to summarize dates or facts. At the beginning of the document is a table of contents
with links that refer to anchors in the same text. There is always a reference section
at the end.

Users get used to it. For instance, they know they can have a quick look at the table
of contents, and if they do not find the info they are looking for, they will go directly
to the reference section to see if they can find another website on the topic. This
works for any page on Wikipedia. You learn the *Wikipedia way* to be more efficient.

So using templates forces a common pattern for documents, and therefore makes
people more efficient in using them. They get used to the structure and know how to
read it quickly.

Providing a template for each kind of document also provides a quick start
for writers.

In this chapter, we will see the various kinds of documents a piece of software can
have, and use Paster to provide skeletons for them. But the first thing to do is to
describe the markup syntax that should be used in Python documentation.


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
