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

Development Environment Setup
================================================================================
This tutorial guides through the steps required to setup the development
environment on various platforms.

System Prerequisites
================================================================================
The following software packages are required to be installed on your system:

*   `Python 3.11 <https://www.python.org>`_
*   `poetry <https://python-poetry.org/>`_
*   `Install Forge <https://installforge.net/>`_ *for MS Windows*

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

*   Install `poetry` package manager

Installation
================================================================================

Editor / IDE
--------------------------------------------------------------------------------

Python virtualenv
^^^^^^^^^^^^^^^^^

Install with pip
^^^^^^^^^^^^^^^^

Install from Git Checkout
^^^^^^^^^^^^^^^^^^^^^^^^^

Run
^^^

..  seealso::
    ..

.. raw:: latex

   \pagebreak

