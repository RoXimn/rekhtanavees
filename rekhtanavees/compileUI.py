# -*- coding: utf-8 -*-

# ******************************************************************************
# Copyright (c) 2022. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************import subprocess
import os
import sys
import site
import subprocess

# ******************************************************************************
UIC = os.path.join(site.getsitepackages()[1], 'PySide6/uic.exe')
RCC = os.path.join(site.getsitepackages()[1], 'PySide6/rcc.exe')


# ******************************************************************************
def compileUI(filename: str) -> None:
    """Compile Qt UI file to python code.

    Compile time conversion of the UI design files into python code to be
    integrated into Qt applications.

    Only filename with full path should be given, without file extension. The
    `.ui` extension is added to read the file and `_ui.py` suffix is added to
    the output file. For example to convert `c:\\path\\to\\interface-file.ui`,
    provide `c:\\path\\to\\interface-file` without the `.ui` suffix.

    Args:
        filename (str): Filename of the UI file with full path *without*
            file extension.

    Output:
        The `PySide2/uic` is used to compile the provided UI file to
        python file and adds a `_ui.py` suffix to the output file.
    """
    inFile, outFile = filename + '.ui', filename + '_ui.py'
    subprocess.run([UIC, '-g', 'python', '--from-imports', '-o', outFile, inFile])
    print('Compiled UI', inFile, '->', outFile)


# ******************************************************************************
def compileRC(filename: str) -> None:
    """Compile Qt RCC file to python code.

    Compile time conversion of the resource files into python code to be
    integrated into Qt applications.

    Only filename with full path should be given, without file extension. The
    `.ui` extension is added to read the file and `_ui.py` suffix is added to
    the output file. For example to convert `c:\\path\\to\\interface-file.ui`,
    provide `c:\\path\\to\\interface-file` without the `.ui` suffix.

    Args:
        filename (str): Filename of the UI file with full path *without*
            file extension.

    Output:
        The `PySide2/uic` is used to compile the provided UI file to
        python file and adds a `_ui.py` suffix to the output file.
    """
    inFile, outFile = filename + '.qrc', filename + '_rc.py'
    subprocess.run([RCC, '-g', 'python', '-o', outFile, inFile])
    print('Compiled QRC', inFile, '->', outFile)


# ******************************************************************************
if __name__ == '__main__':
    commonFiles = [
        'ui\\main',
    ]

    # Compile User Interface files
    uiFiles = commonFiles[:]
    uiFiles.extend([
        'ui\\recordingwidget',
    ])
    for filename in uiFiles:
        compileUI(filename)

    # Compile Resource files
    rcFiles = commonFiles[:]
    rcFiles.extend([
    ])
    for filename in rcFiles:
        compileRC(filename)

# ******************************************************************************
