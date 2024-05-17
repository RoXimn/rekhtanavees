# -*- coding: utf-8 -*-
# ******************************************************************************
# Copyright (c) 2022. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
import logging
from pathlib import Path
from typing import List

from PySide6.QtGui import QAction, QIcon, QImage
from PySide6.QtWidgets import QMainWindow, QMessageBox, QSizePolicy, QSpacerItem
import fitz

from rekhtanavees.constants import Rx
from rekhtanavees.settings import AppConfig
from rekhtanavees.ui.mainwindow_ui import Ui_rekhtaNavees
from rekhtanavees.ui.imageviewer import ImageViewer
from rekhtanavees.ui.projectwizard import RProjectWizard
from rekhtanavees.ui.recordingwidget import RecordingItemWidget
from rekhtanavees.audio.audioproject import AudioProject


# ******************************************************************************
class MainWindow(QMainWindow):
    """Application MainWindow class"""

    # **************************************************************************
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_rekhtaNavees()
        self.ui.setupUi(self)

        self.ui.actionNew.triggered.connect(self.onNew)
        self.ui.actionOpen.triggered.connect(self.onOpen)
        self.ui.actionOpenSource.triggered.connect(self.onOpenSource)
        self.ui.actionExit.triggered.connect(self.onExit)
        self.ui.actionAbout.triggered.connect(self.onAbout)
        self.ui.actionAboutQt.triggered.connect(qApp.aboutQt)

        # Recent files
        self.maxRecentCount = AppConfig().Main.RecentMaxCount

        self.ui.recentSeperator = self.ui.menuRecent.addSeparator()
        self.ui.menuRecent.insertAction(self.ui.actionClearRecent, self.ui.recentSeperator)
        self.ui.recentSeperator.setVisible(False)

        self.ui.actionClearRecent.setEnabled(False)
        self.ui.actionClearRecent.triggered.connect(self.onClearRecentFiles)

        self.recentFileActionList = []
        for i in range(self.maxRecentCount):
            act = QAction(self)
            act.setVisible(False)
            act.triggered.connect(self.onOpenRecent)
            self.recentFileActionList.append(act)
            self.ui.menuRecent.insertAction(self.ui.recentSeperator, act)

        self.updateRecentFileList()

        self.ui.transcriptionSource = ImageViewer(self)
        self.ui.splitter.insertWidget(0, self.ui.transcriptionSource)

        self.audioProject = None

    # **************************************************************************
    def onNew(self) -> None:
        logger: logging.Logger = logging.getLogger(Rx.ApplicationName)

        wizard = RProjectWizard(newProject=True)
        result = wizard.exec()
        if result:
            prjDir = Path(wizard.field('BaseDirectory').strip()) / wizard.field('ProjectName').strip()
            try:
                # Create project directory
                prjDir.mkdir(parents=True, exist_ok=True)
                qApp.log.info(f'Project directory "{prjDir}" successfully created')  # type: ignore

                # Create new Project object and save to the directory
                audioProject = AudioProject()
                audioProject.name = wizard.field('ProjectName')
                audioProject.folder = str(prjDir)
                audioProject.author = wizard.field('ProjectAuthor')
                audioProject.description = wizard.field('ProjectDescription')
                audioProject.saveProject()
                logger.info(f'New project file "{audioProject.projectFilename()}" created')  # type: ignore

                # Load the saved project
                self.loadAudioProject(Path(audioProject.projectFilename()))
                self.statusBar().showMessage(f'New project created: {audioProject.name}', 3000)

            except Exception as e:
                logger.error(f'Project Directory: "{prjDir}" could not be created: {e!r}')  # type: ignore

    # **************************************************************************
    def onOpen(self) -> None:
        wizard = RProjectWizard(newProject=False)
        result = wizard.exec()
        if result:
            prjFilename: str = wizard.field('ProjectFile')
            self.loadAudioProject(Path(prjFilename))

    # **************************************************************************
    def onOpenSource(self) -> None:
        pdf = fitz.open(r'C:\Users\driyo\Documents\qtextlayout.h.pdf')
        pg = pdf[0]
        px = pg.get_pixmap(dpi=300, alpha=False)
        img = QImage(px.samples, px.width, px.height, px.stride, QImage.Format_RGB888)
        self.ui.transcriptionSource.setImage(img)

    # **************************************************************************
    def onOpenRecent(self) -> None:
        action: QAction = self.sender()  # type: ignore
        if action:
            self.loadAudioProject(action.data())

    # **************************************************************************
    def onExit(self) -> None:
        self.clearRecordings()
        self.close()

    # **************************************************************************
    def onAbout(self) -> None:
        QMessageBox.about(
            self,
            f'{Rx.ApplicationName} - About',
            f'<h4>{Rx.ApplicationName} <tt>{Rx.ApplicationVersion}</tt><br>'
            f'{Rx.Copyright}</h4>'
            f'<p>{Rx.Licence}</p>'
            '<h4>Attributions</h4>'
            '<ul>'
            '<li>Some icons by <a href="https://github.com/KDE/oxygen-icons5">Oxygen Icons</a>, '
            'licensed under <a href="https://www.gnu.org/licenses/lgpl-3.0.en.html">'
            'GNU Lesser General Public License v3.0</a> License.</li>'
            '</ul>'
            '</div>'
            )

    # **************************************************************************
    def adjustRecentListForCurrent(self, projectFilename: Path):
        logger: logging.Logger = logging.getLogger(Rx.ApplicationName)

        logger.debug(f"Adjusting recent list for {projectFilename}")
        settings = AppConfig()
        recentFiles: List[Path] = settings.Main.RecentFiles
        logger.info(f"Total recents[{len(recentFiles)}] {recentFiles}")

        while projectFilename in recentFiles:
            recentFiles.remove(projectFilename)
        recentFiles.insert(0, projectFilename)
        if len(recentFiles) > self.maxRecentCount:
            del recentFiles[self.maxRecentCount:]
        settings.Main.RecentFiles = recentFiles
        settings.save()
        logger.debug(f"Updated recents[{len(recentFiles)}] {recentFiles}")

        self.updateRecentFileList()

    # **************************************************************************
    def updateRecentFileList(self):
        settings = AppConfig()
        recentFiles: List[Path] = settings.Main.RecentFiles
        total: int = min(len(recentFiles), settings.Main.RecentMaxCount)
        logging.getLogger(Rx.ApplicationName).info(f"Total recents[{total}] {recentFiles}")

        for i in range(total):
            recentFile = recentFiles[i]
            fn = recentFile.stem
            act = self.recentFileActionList[i]
            act.setText(f'&{i + 1}. {fn}')
            act.setIcon(QIcon(':/images/icons/folder-bookmark.png'))
            act.setVisible(True)
            act.setToolTip(str(recentFile))
            act.setData(recentFile)

        for i in range(total, self.maxRecentCount):
            self.recentFileActionList[i].setVisible(False)

        hasRecent: bool = total > 0
        self.ui.actionClearRecent.setEnabled(hasRecent)
        self.ui.recentSeperator.setVisible(hasRecent)

    # **************************************************************************
    def onClearRecentFiles(self):
        settings = AppConfig()
        settings.Main.RecentFiles.clear()
        settings.save()
        self.updateRecentFileList()

    # **************************************************************************
    def loadAudioProject(self, projectFilename: Path):
        logging.getLogger(Rx.ApplicationName).info(f'Loading {projectFilename!s}...')
        self.setWindowFilePath(str(projectFilename))
        self.adjustRecentListForCurrent(projectFilename)

        self.clearRecordings()

        projectFolderPath: Path = projectFilename.parent
        audioProject = AudioProject()
        audioProject.projectFolder = str(projectFolderPath)
        audioProject.title = projectFilename.stem
        audioProject.loadProject()

        self.audioProject = audioProject
        self.ui.lblRecordings.setText(f'Audio Recordings: <b>{self.audioProject.title}</b> [{len(self.audioProject.recordings)}]')
        for recording in self.audioProject.recordings:
            recordingWidget = RecordingItemWidget(self, projectFolderPath, recording)
            self.ui.recordingsLayout.addWidget(recordingWidget)
        verticalSpacer = QSpacerItem(1, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.ui.recordingsLayout.insertItem(-1, verticalSpacer)

        self.statusBar().showMessage(f'Loaded project {audioProject.name}({audioProject.projectFolder})', 3000)

    # **************************************************************************
    def clearRecordings(self):
        while self.ui.recordingsLayout.count():
            child = self.ui.recordingsLayout.takeAt(0)
            widget = child.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
            del child

# ******************************************************************************
