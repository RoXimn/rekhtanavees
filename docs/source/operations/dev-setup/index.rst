..  ****************************************************************************
    Copyright(c) 2024 RoXimn. All rights reserved.

    This work is licensed under the Creative Commons Attribution 4.0 International License.
    To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.

    Author:      RoXimn <roximn@rixir.org>
    ****************************************************************************

================================================================================
Development Setup
================================================================================

==============  ================================================================
Author          RoXimn <roximn@rixir.org>
Tags            tutorial, setup, development
Description     Tutorial to setup the development environment.
Target          Developer
Created         16 May 2024
Updated         16 May 2024
==============  ================================================================

..  contents:: Contents
    :local:
    :class: well

.. todo :: Revise **Development Setup** guide

This tutorial guides through the steps required to setup the development
environment on various platforms.

System Prerequisites
================================================================================
The following software packages are required to be installed on your system:

*   `Python 3.11 <https://www.python.org>`_
*   `poetry <https://python-poetry.org/>`_
*   `Inno Setup <https://jrsoftware.org/isinfo.php>`_ *for MS Windows*

See the specific instructions for your platform below.

*   :ref:`debian-ubuntu`
*   :ref:`centos-fedora-rhel`
*   :ref:`windows`

..  note:: The application is bit size independent and works on both 32 and
    64 bit architectures.

..  _debian-ubuntu:

Debian / Ubuntu
--------------------------------------------------------------------------------
Install the prerequisites using APT: ::

    sudo apt-get update
    sudo apt-get install curl git build-essential libssl-dev python3-dev \
        python3-pip python3-virtualenv

..  _centos-fedora-rhel:

CentOS / Fedora / Red Hat Enterprise Linux
--------------------------------------------------------------------------------
For CentOS and Red Hat Enterprise Linux, enable the
`Extra Packages for Enterprise Linux <https://fedoraproject.org/wiki/EPEL>`_
YUM repository: ::

   sudo yum install epel-release

Install the prerequisites using YUM: ::

   sudo yum install gcc-c++ make curl git python-devel python-pip


..  _windows:

Windows
--------------------------------------------------------------------------------
*   Download and install the `Windows MSI Installer <https://www.python.org/downloads/windows/>`_
    for the Python 3.11 release (at lest) from the Python website.

*   Install `poetry`_ package manager

Installation
================================================================================

Editor / IDE
--------------------------------------------------------------------------------

Python virtualenv
--------------------------------------------------------------------------------

Install with pip
--------------------------------------------------------------------------------

Install from Git Checkout
--------------------------------------------------------------------------------

Running
================================================================================

Distribution
================================================================================

Windows
--------------------------------------------------------------------------------
Creating the distribution package consists of two steps,

* generating the executable of the python code, and
* packaging everything together as a nice single setup file for the end user.

This can be done by running the convenience batch file within the python
environment, with prerequisites installed, ::

    scripts\generate-win-setup.bat

or performing these steps separately, as per the requirement.

1. Compiling
^^^^^^^^^^^^
The MS Windows executable is created using PyInstaller. From project *root*
directory with python environment active, run::

    pyinstaller rekhtanavees.app.spec

This will create two folders ``build`` and ``dist`` in the *root* directory.
The ``dist/rekhtanavees`` folder will contain the final executable.

2. Packaging
^^^^^^^^^^^^
`Inno Setup`_ is used to create the installer for distribution to the end user.

#. Download and install the `Inno Setup program <https://jrsoftware.org/isdl.php#stable>`_,
   if not already done.
#. Assuming the **Inno Setup** is installed to ``C:\Program Files (x86)\Inno Setup 6``, run::

    "C:\Program Files (x86)\Inno Setup 6"\ISCC.exe installer\rekhtanavees-installer.iss

   The generated output setup file should be in the same folder as the installer script.


..  seealso::
    ..

.. raw:: latex

   \pagebreak
