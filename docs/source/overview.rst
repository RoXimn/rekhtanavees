..  ****************************************************************************
    Copyright(c) 2024 RoXimn. All rights reserved.

    This work is licensed under the Creative Commons Attribution 4.0 International License.
    To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.

    Author:      RoXimn <roximn@rixir.org>
    ****************************************************************************

********************************************************************************
Overview
********************************************************************************
..  contents:: Contents
    :local:
    :class: well

Introduction
===============================================================================
Rekhta Navees is an effort to *kill two birds with one stone*,

1. Collect **audio clips**/**transcribed text** pairs for dataset creation for training an STT AI model,
2. Creating/Collecting **Urdu** language text data through transcribed audio to minimize manual text entry.

The application is geared to,

#.  record/load audio, followed by,
#.  user supervised audio segmentation,
#.  transcription with existing working solutions (currently using *OpenAI Whisper* STT model) and,
#.  aggregation of individual transcriptions to usable text.

Standing on the shoulders of,

* `PySide6 <https://pypi.org/project/PySide6/>`_ (Qt6) based UI with Python,
* `librosa <https://pypi.org/project/librosa/>`_/`Numpy <https://pypi.org/project/numpy/>`_ for audio processing,
* `faster-whisper <https://github.com/SYSTRAN/faster-whisper>`_ for audio transcription,
* `PyMuPDF <https://pypi.org/project/PyMuPDF/>`_ for pdf rendering,
* `PyInstaller <https://pypi.org/project/pyinstaller/>`_/`Install Forge <https://installforge.net/>`_ for MS Windows standalone executable creation.



Organization
===============================================================================

This documentation is organized into *three* parts,


:ref:`Design <DesignIndex>`
--------------------------------------------------------------------------------

Congregates all documents providing

-   Architecture overview
-   Class diagrams with dependencies and hierarchy relations
-   User interface wireframes
-   Infrastructure description

:ref:`Usage <UsageIndex>`
--------------------------------------------------------------------------------

Documents on how to use the software,

-   :ref:`cookbook <CookBookIndex>` (a collection of recipes)
        A recipe is a short document explaining how to do something.
        This targets one readership and focuses on one specific topic.
-   :ref:`tutorials <TutorialsIndex>`
        A step-by-step document that explains how to use a feature of
        the software.
-   :ref:`User's Manual <UsersManualIndex>`
        The all encompassing end user's manual of information about the
        software.


:ref:`Operations <OperationsIndex>`
--------------------------------------------------------------------------------

Provide guides on

-   Installation and deployment documents
-   Administration documents
-   “Frequently Asked Questions” documents that help the users when a
    failure occurs
-   Documents that explain how people can ask for help or
    provide feedback



.. raw:: latex

   \pagebreak
