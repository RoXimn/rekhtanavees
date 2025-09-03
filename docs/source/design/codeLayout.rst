..  ****************************************************************************
    Copyright(c) 2024 RoXimn. All rights reserved.

    This work is licensed under the Creative Commons Attribution 4.0 International License.
    To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.

    Author:      RoXimn <roximn@rixir.org>
    ****************************************************************************

********************************************************************************
Source Code Organization
********************************************************************************

Folder Hierarchy
================================================================================
The organization of the source code is described here to familiarize the reader
with the high level breakup of the code and the role of each part.

* **root folder**
    The parent folder, containing the application code ``rekhtanavees``,
    ``tests``, ``docs`` and the MS Windows ``installer`` files.

    * ``rekhtanavees``
        All the application source code resides in this folder. The `Qt` gui
        application is instantiated in the :py:mod:`main <rekhtanavees.main>`.
        The application loads preferences from :py:attr:`ConfigPath <rekhtanavees.constants.RConstants.ConfigPath>`
        using :py:mod:`settings <rekhtanavees.settings>` and logs its processing
        to log file at :py:attr:`DataPath <rekhtanavees.constants.RConstants.DataPath>`.

        * :py:mod:`main <rekhtanavees.main>`
            API endpoint definitions under versioned folders.

            `depends <raxis.api.depends>` module contains the universal
            dependencies of the api endpoints, for example, the user
            authentication middleware.

        * :py:attr:`constants <rekhtanavees.constants>`
            This module contains central application runtime supportive
            modules, not specific to any subsection but globally usable in the
            application.

        * :py:mod:`settings <rekhtanavees.settings>`
            The module contains central application runtime supportive
            modules, not specific to any subsection but globally usable in the
            application.

        * :py:mod:`audio <rekhtanavees.audio>`
            The folder contains audio related modules, classes and functions.

        * ``tests``
            Application unit tests.

    * ``docs``
        * ``source``
            Documentation source folder.

    * ``installer``
        The `Install Forge <https://installforge.net/>`_ setup creator file and the requisite resources.

.. raw:: latex

   \pagebreak


..  ****************************************************************************