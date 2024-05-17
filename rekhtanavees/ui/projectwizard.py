# -*- coding: utf-8 -*-
# ******************************************************************************
# Copyright (c) 2022. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
from pathlib import Path

from PySide6.QtCore import QStandardPaths
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QCheckBox, QFileDialog, QFormLayout, QFrame, QHBoxLayout, QLineEdit, QMessageBox, QPlainTextEdit, QPushButton,
                               QSizePolicy, QWizard, QWizardPage)

from settings import AppConfig
from audio.audioproject import AudioProject, AudioProjectException
from rekhtanavees.constants import Rx
from misc.utils import isValidProjectName


# ******************************************************************************
class RNewProjectPage(QWizardPage):

    def __init__(self, parent, baseDirectory: str):
        super(RNewProjectPage, self).__init__(parent)

        self.setTitle("New Project")
        self.setSubTitle("Select a project name and the base directory in which to create the project.")

        self.teBaseDirectory = QLineEdit()
        self.teBaseDirectory.setReadOnly(True)
        self.teBaseDirectory.setText(baseDirectory)

        self.btnDirectorySelector = QPushButton()
        self.btnDirectorySelector.setText('...')
        self.btnDirectorySelector.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.btnDirectorySelector.setMaximumWidth(30)
        self.btnDirectorySelector.clicked.connect(self.onGetBaseDirectory)  # type: ignore
        hBox = QHBoxLayout()
        hBox.addWidget(self.teBaseDirectory, 10)
        hBox.addWidget(self.btnDirectorySelector, 0)
        hBox.setSpacing(2)

        self.cbxSetDefaultDirectory = QCheckBox('Save as default base directory')
        self.cbxSetDefaultDirectory.setChecked(False)

        self.teProjectName = QLineEdit()
        self.teProjectName.textChanged.connect(self.onProjectNameChanged)  # type: ignore
        self.teProjectName.setToolTip('Name should only contains ascii alphanumeric characters and space')

        self.teProjectAuthor = QLineEdit()
        self.teProjectAuthor.textChanged.connect(self.onProjectAuthorChanged)  # type: ignore
        self.teProjectAuthor.setToolTip('Name <email>')

        self.tbxProjectDescription = QPlainTextEdit()

        formLayout = QFormLayout()
        formLayout.addRow('Name*', self.teProjectName)
        formLayout.addRow('Author*', self.teProjectAuthor)
        formLayout.addRow('Description', self.tbxProjectDescription)

        hLine = QFrame()
        hLine.setFrameShape(QFrame.HLine)
        hLine.setFrameShadow(QFrame.Sunken)
        formLayout.addRow(hLine)

        formLayout.addRow('Base directory', hBox)
        formLayout.addRow('', self.cbxSetDefaultDirectory)
        self.setLayout(formLayout)

        self.registerField('ProjectName*', self.teProjectName)
        self.registerField('ProjectAuthor*', self.teProjectAuthor)
        self.registerField('ProjectDescription', self.tbxProjectDescription, 'plainText', 'textChanged')  # type: ignore
        self.registerField('BaseDirectory', self.teBaseDirectory)
        self.registerField('SetDefaultBaseDirectory', self.cbxSetDefaultDirectory)

    def onProjectNameChanged(self):
        self.teProjectName.setStyleSheet('/**/')

    def onProjectAuthorChanged(self):
        self.teProjectAuthor.setStyleSheet('/**/')

    def onGetBaseDirectory(self):
        baseDir = QFileDialog.getExistingDirectory(
            self,
            "Select base folder",
            self.teBaseDirectory.text(),
            QFileDialog.ShowDirsOnly
        )
        if baseDir:
            self.teBaseDirectory.setText(str(Path(baseDir).resolve()))

    def validatePage(self) -> bool:
        isValid: bool = True

        if not isValidProjectName(self.teProjectName.text()):
            self.teProjectName.setStyleSheet('background: LightCoral;')
            isValid = isValid and False
        else:
            self.teProjectName.setStyleSheet('/**/')
            isValid = isValid and True

        if self.teProjectAuthor.text() and not self.teProjectAuthor.text().isspace():
            self.teProjectAuthor.setStyleSheet('/**/')
            isValid = isValid and True
        else:
            self.teProjectAuthor.setStyleSheet('background: LightCoral;')
            isValid = isValid and False

        # The base directory is always valid
        prjFile = Path(self.teBaseDirectory.text().strip()) / self.teProjectName.text().strip() / f'{self.teProjectName.text().strip()}.toml'
        if prjFile.exists():
            QMessageBox.warning(self, Rx.ApplicationName,
                                'A project with same name already <i>exists</i> at the location!!!<br/>'
                                'Please select a different name/location for the new project.',
                                QMessageBox.Ok, QMessageBox.Ok)
            isValid = isValid and False
        return isValid

    def cleanupPage(self):
        self.teProjectName.setText('')
        self.teBaseDirectory.setText('')


# ******************************************************************************
class RExistingProjectPage(QWizardPage):
    def __init__(self, parent, baseDirectory: str):
        super().__init__(parent)
        self.cwd = baseDirectory

        self.setTitle("Open Project")
        self.setSubTitle("Select a project file to load the project.")

        self.teProjectFile = QLineEdit()
        self.teProjectFile.setReadOnly(True)
        self.teProjectFile.setText('')

        self.btnDirectorySelector = QPushButton()
        self.btnDirectorySelector.setText('...')
        self.btnDirectorySelector.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.btnDirectorySelector.setMaximumWidth(30)
        self.btnDirectorySelector.clicked.connect(self.onGetBaseDirectoryProjectFile)  # type: ignore
        hBox = QHBoxLayout()
        hBox.addWidget(self.teProjectFile, 10)
        hBox.addWidget(self.btnDirectorySelector, 0)
        hBox.setSpacing(2)

        self.tbxProjectDescription = QPlainTextEdit()
        self.tbxProjectDescription.setReadOnly(True)

        formLayout = QFormLayout()
        formLayout.addRow('Project File', hBox)
        formLayout.addRow('', self.tbxProjectDescription)
        self.setLayout(formLayout)

        self.registerField('ProjectFile*', self.teProjectFile)

    def onGetBaseDirectoryProjectFile(self):
        fileName, selectedFilter = QFileDialog.getOpenFileName(
            self, caption="Select project file",
            dir=self.cwd,
            filter='Project Files (*.toml)')
        if fileName:
            prjFilePath = Path(fileName)
            audioProject = AudioProject()
            audioProject.name = str(prjFilePath.stem)
            audioProject.folder = str(prjFilePath.parent)
            try:
                audioProject.loadProject()
                self.tbxProjectDescription.setPlainText(f'Author: {audioProject.author}\n'
                                                        f'Created: {audioProject.createdOn.strftime("%A, %d %b %Y %I:%M:%S %p %Z")}\n'
                                                        f'Recordings: {len(audioProject.recordings)}')
                self.teProjectFile.setStyleSheet('/**/')
                self.teProjectFile.setText(str(Path(fileName).resolve()))
                self.cwd = str(Path(fileName).parent)
            except AudioProjectException as ex:
                self.teProjectFile.setText('')
                self.teProjectFile.setStyleSheet('/**/')
                self.tbxProjectDescription.setPlainText(str(ex))

    def cleanupPage(self):
        self.teProjectFile.setText('')
        self.tbxProjectDescription.setPlainText('')

    def validatePage(self) -> bool:
        if self.teProjectFile.text():
            self.teProjectFile.setStyleSheet('/**/')
            return True
        else:
            self.teProjectFile.setStyleSheet('background: LightCoral;')
            return False


# ******************************************************************************
class RProjectWizard(QWizard):
    """Wizard to setting up new projects or opening existing one

    Settings
    --------
    -`ProjectDefaultBaseDirectory`
        Defaults to user's home directory. The default directory for creating
        new projects and opening existing projects.
    """
    ProjectBaseDirectorySID: str = 'ProjectBaseDirectory'
    ProjectBaseDirectoryDefault: str = QStandardPaths.writableLocation(QStandardPaths.HomeLocation)

    def __init__(self, parent=None, newProject: bool = False):
        super().__init__(parent)

        baseDirectory = AppConfig().Main.ProjectBaseDirectory
        # baseDirectory = qApp.settings.value(self.ProjectBaseDirectorySID)  # type: ignore
        # if baseDirectory is None:
        #     baseDirectory = self.ProjectBaseDirectoryDefault
        #     qApp.settings.setValue(self.ProjectBaseDirectorySID, baseDirectory)  # type: ignore

        self.setButtonLayout([QWizard.Stretch, QWizard.FinishButton, QWizard.CancelButton])
        self.isNewProject = newProject
        if self.isNewProject:
            self.addPage(RNewProjectPage(self, str(baseDirectory)))
            self.setButtonText(QWizard.FinishButton, 'Create')
        else:
            self.addPage(RExistingProjectPage(self, str(baseDirectory)))
            self.setButtonText(QWizard.FinishButton, 'Open')

        self.setWindowTitle("Project Wizard")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setWindowIcon(QPixmap(':/images/icons/feather.png'))
        self.setPixmap(QWizard.WatermarkPixmap, QPixmap(':/images/icons/rekhtanavees.png'))
        self.setMinimumWidth(640)

    def accept(self):
        if self.isNewProject:
            if self.page(0).field('SetDefaultBaseDirectory'):
                settings = AppConfig()
                settings.Main.ProjectBaseDirectory = Path(self.page(0).field('BaseDirectory').strip())
                settings.save()
                # qApp.settings.setValue(self.ProjectBaseDirectorySID,
                #                        self.page(0).field('BaseDirectory'))
        super(RProjectWizard, self).accept()


# ******************************************************************************
