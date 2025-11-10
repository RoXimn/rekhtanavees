# ******************************************************************************
# Copyright (c) 2025. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
import re
from pathlib import Path
from typing import List

from PySide6.QtCore import (
    QUrl, Qt, QTimer, QPoint, QSize, QElapsedTimer, QModelIndex,
    QItemSelectionModel
)
from PySide6.QtGui import (
    QAction, QIcon, QKeyEvent, QResizeEvent,
    QFont, QTextOption, QFontMetrics, QSyntaxHighlighter, QTextCharFormat
)
from PySide6.QtMultimedia import QMediaPlayer, QMediaDevices, QAudioOutput
from PySide6.QtMultimediaWidgets import QGraphicsVideoItem
from PySide6.QtWidgets import (
    QMainWindow, QMessageBox, QWidget,
    QGraphicsScene, QGraphicsTextItem, QStyleOption, QStyle, QFileDialog
)

from rekhtanavees.audio.audioproject import AudioProjectException
from rekhtanavees.constants import Rx
from rekhtanavees.misc.utils import hmsTimestamp, tms
from rekhtanavees.settings import RSettings
from rekhtanavees.ui.mainwindow_ui import Ui_rekhtaNavees
from rekhtanavees.ui.naveesProject import NaveesProject
from rekhtanavees.ui.projectwizard import RProjectWizard
from rekhtanavees.ui.recordingsModel import RecordingsTableModel


# ******************************************************************************
class TextHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(TextHighlighter, self).__init__(parent)
        self._mappings = {}

    def addMapping(self, pattern: str, format_: QTextCharFormat):
        self._mappings[pattern] = format_

    def highlightBlock(self, text):
        for pattern, format_ in self._mappings.items():
            for match in re.finditer(pattern, text):
                start, end = match.span()
                self.setFormat(start, end - start, format_)


# ******************************************************************************
class MainWindow(QMainWindow):
    """Application MainWindow class"""

    # **************************************************************************
    def eventFilter(self, watched, event):
        if watched is self.ui.videoView and isinstance(event, QResizeEvent):
            # print(watched, event)
            sz = self.ui.videoView.geometry().size()
            self.ui.videoItem.setSize(sz)
            c = self.ui.videoView.rect().center()
            c.setX(0)
            self.ui.sceneCaption.setPos(c)
            self.ui.sceneCaption.setTextWidth(sz.width())
        return super(MainWindow, self).eventFilter(watched, event)

    # **************************************************************************
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_rekhtaNavees()
        self.ui.setupUi(self)

        self.ui.transcript.setFont(QFont(['Noto Naskh Arabic', 'Noto Sans'], 24, QFont.Normal))

        fm = QFontMetrics(self.ui.transcript.font())
        h: int = max(fm.height(), 14) + 4
        w: int = fm.horizontalAdvance('x') * 17 + 4
        opt = QStyleOption()
        opt.initFrom(self.ui.transcript)
        sz = self.style().sizeFromContents(QStyle.CT_LineEdit, opt, QSize(w, h), self)
        self.ui.transcript.setFixedHeight(sz.height()*1.5)

        doc = self.ui.transcript.document()
        doc.setDefaultStyleSheet("color: blue;")
        to = doc.defaultTextOption()
        to.setTextDirection(Qt.LayoutDirection.RightToLeft)
        to.setAlignment(Qt.AlignmentFlag.AlignRight)
        to.setFlags(QTextOption.ShowTabsAndSpaces | QTextOption.ShowLineAndParagraphSeparators)
        doc.setDefaultTextOption(to)

        self.ui.highlighter = TextHighlighter(self)
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold)
        fmt.setForeground(Qt.gray)
        self.ui.highlighter.addMapping(r'\s+', fmt)
        # fmt = QTextCharFormat()
        # fmt.setForeground(Qt.blue)
        # self.highlighter.addMapping(r'\S+', fmt)
        self.ui.highlighter.setDocument(doc)

        self.ui.actionNew.triggered.connect(self.onNew)
        self.ui.actionOpen.triggered.connect(self.onOpen)
        self.ui.actionSave.triggered.connect(self.onSave)
        self.ui.actionClose.triggered.connect(self.onProjectClose)
        self.ui.actionExit.triggered.connect(self.onExit)

        self.ui.actionExportSRT.triggered.connect(self.onExportSrt)

        self.ui.actionAbout.triggered.connect(self.onAbout)
        self.ui.actionAboutQt.triggered.connect(qApp.aboutQt)

        self.ui.autoSaveTimer = QTimer(self)
        self.ui.autoSaveTimer.timeout.connect(self.onAutoSave)

        # Recent files
        self.ui.maxRecentCount = RSettings().Main.RecentMaxCount

        self.ui.recentSeperator = self.ui.menuRecent.addSeparator()
        self.ui.menuRecent.insertAction(self.ui.actionClearRecent, self.ui.recentSeperator)
        self.ui.recentSeperator.setVisible(False)

        self.ui.actionClearRecent.setEnabled(False)
        self.ui.actionClearRecent.triggered.connect(self.onClearRecentFiles)

        self.ui.recentFileActionList = []
        for i in range(self.ui.maxRecentCount):
            act = QAction(self)
            act.setVisible(False)
            act.triggered.connect(self.onOpenRecent)
            self.ui.recentFileActionList.append(act)
            self.ui.menuRecent.insertAction(self.ui.recentSeperator, act)

        self.updateRecentFileList()

        self.ui.scene = QGraphicsScene()

        self.ui.sceneCaption = QGraphicsTextItem()
        self.ui.sceneCaption.setZValue(100)
        # TODO: Add caption formating to RSettings
        self.ui.sceneCaption.setFont(QFont('Noto Naskh Arabic', 18))
        self.ui.sceneCaption.setDefaultTextColor(Qt.white)
        to = self.ui.sceneCaption.document().defaultTextOption()
        to.setTextDirection(Qt.LayoutDirection.RightToLeft)
        to.setAlignment(Qt.AlignmentFlag.AlignCenter)
        to.setFlags(QTextOption.ShowTabsAndSpaces | QTextOption.ShowLineAndParagraphSeparators)
        self.ui.sceneCaption.document().setDefaultTextOption(to)
        self.ui.scene.addItem(self.ui.sceneCaption)

        self.ui.videoItem = QGraphicsVideoItem()
        self.ui.videoItem.setOffset(QPoint(0, 0))
        self.ui.scene.addItem(self.ui.videoItem)
        self.ui.videoView.setScene(self.ui.scene)

        self.ui.videoPlayer = QMediaPlayer()
        self.ui.videoPlayer.setVideoOutput(self.ui.videoItem)
        self.ui.playSlider.setEnabled(False)

        self.ui.audioOutput = QAudioOutput(QMediaDevices.defaultAudioOutput())
        self.ui.audioPlayer = QMediaPlayer()
        self.ui.audioPlayer.setAudioOutput(self.ui.audioOutput)
        self.ui.audioPlayer.durationChanged.connect(self.onDurationChange)
        self.ui.audioPlayer.positionChanged.connect(self.onPositionChange)

        self.ui.btnPlay.clicked.connect(self.onTogglePlay)

        self.ui.transcript.textChanged.connect(self.updateTranscriptSegment)
        self.ui.videoView.installEventFilter(self)

        self.recordingsModel = RecordingsTableModel(segments=None, parent=self)
        self.ui.tbvListing.setLayoutDirection(Qt.RightToLeft)
        self.ui.tbvListing.setModel(self.recordingsModel)
        self.ui.tbvListing.doubleClicked.connect(self.onListingDoubleClick)

        self.ui.actionDetails.setChecked(False)
        self.ui.dckProjectDetails.setHidden(True)
        self.ui.leAuthorName.textChanged.connect(self.updateAuthorName)
        self.ui.leAuthorEmail.textChanged.connect(self.updateAuthorEmail)
        self.ui.tbxDescription.textChanged.connect(self.updateDescription)

        # self.audioProject: AudioProject | None = None
        self.audioProject: NaveesProject = NaveesProject(self)
        self.currentRecording: int = 0
        """Current recording  index.

        This index will be used to keep track of the current recording used for processing"""

        self.currentSegment: int = 0
        """
        Current transcript segment index.

        This segment will be used to keep track of the currently playing or displayed segment in the application.
        Initialized to 0.
        """
        self.ui.sbxIndex.valueChanged.connect(self.onIndexChanged)

        self.clearRecordingsUi()
        self.setRecordingUiEnabled(False)

        self.clearProjectUi()
        self.setProjectUiEnabled(False)

    # **************************************************************************
    def clearProjectUi(self):
        self.ui.leProjectTitle.clear()
        self.ui.leProjectFolder.clear()
        self.ui.leCreation.clear()
        self.ui.leAuthorName.clear()
        self.ui.leAuthorEmail.clear()
        self.ui.tbxDescription.clear()

    # **************************************************************************
    def clearRecordingsUi(self):
        self.ui.lblRecordingsTitle.setText("")
        self.ui.lblSegment.setText("")
        self.ui.lblCurrentPosition.setText("--:--")
        self.ui.lblTotalLength.setText("--:--")

        self.ui.videoPlayer.setSource(QUrl())
        self.ui.audioPlayer.setSource(QUrl())

        self.ui.transcript.clear()
        self.ui.audioSpectrumArea.audioSpectrum.setSource(None, None)
        self.recordingsModel.setSegments(None)

    # **************************************************************************
    def setProjectUiEnabled(self, enabled: bool):
        self.ui.actionSave.setEnabled(enabled)
        self.ui.actionClose.setEnabled(enabled)

        self.ui.actionDetails.setEnabled(enabled)
        self.ui.dckProjectDetailsContents.setEnabled(enabled)
        if enabled:
            self.ui.autoSaveTimer.start(RSettings().Main.AutoSaveInterval * 60 * 1000)
        else:
            self.ui.autoSaveTimer.stop()

    # **************************************************************************
    def setRecordingUiEnabled(self, enabled: bool):
        if enabled and self.audioProject.length:
            recording = self.audioProject.recordings[self.currentRecording]
            self.ui.sbxIndex.setMinimum(1)
            self.ui.sbxIndex.setMaximum(len(recording.speechSegments))
            self.ui.sbxIndex.setSuffix(f"/{len(recording.speechSegments)}")
            self.ui.sbxIndex.setEnabled(True)
        else:
            self.ui.sbxIndex.setMinimum(0)
            self.ui.sbxIndex.setMaximum(0)
            self.ui.sbxIndex.setSuffix("")
            self.ui.sbxIndex.setDisabled(True)

        self.ui.btnPlay.setEnabled(enabled)
        self.ui.cbxLoop.setEnabled(enabled)

        self.ui.menuRecordings.setEnabled(enabled)
        self.ui.recordingToolBar.setVisible(enabled)
        self.ui.actionExportSRT.setEnabled(enabled)

        self.ui.videoView.setEnabled(enabled)
        self.ui.tbvListing.setEnabled(enabled)
        self.ui.transcript.setEnabled(enabled)

    # **************************************************************************
    def updateDescription(self):
        if self.audioProject:
            text = self.ui.tbxDescription.toPlainText()
            self.audioProject.description = text

    # **************************************************************************
    def updateAuthorName(self):
        if self.audioProject:
            self.audioProject.authorName = self.ui.leAuthorName.text()

    # **************************************************************************
    def updateAuthorEmail(self):
        if self.audioProject:
            self.audioProject.authorEmail = self.ui.leAuthorEmail.text()

    # **************************************************************************
    def updateTranscriptSegment(self):
        text = self.ui.transcript.toPlainText()
        self.ui.sceneCaption.setPlainText(text)
        if self.audioProject and self.audioProject.length > 0:
            recording = self.audioProject.recordings[self.currentRecording]
            segment = recording.speechSegments[self.currentSegment]
            segment.text = text

    # **************************************************************************
    def keyPressEvent(self, e: QKeyEvent):
        focus: QWidget = self.focusWidget()
        if focus is self:
            if e.key() == Qt.Key_Space:
                # self.onTogglePlay()
                pass
            elif e.key() == Qt.Key_Down:
                self.updateCurrentSegment(self.currentSegment + 1)
            elif e.key() == Qt.Key_Up:
                self.updateCurrentSegment(self.currentSegment - 1)
            elif e.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.ui.transcript.setFocus()
        elif focus is self.ui.transcript:
            if e.key() in (Qt.Key_Escape, Qt.Key_Return, Qt.Key_Enter):
                self.setFocus()
        else:
            super(MainWindow, self).keyPressEvent(e)

    # **************************************************************************
    def onIndexChanged(self, idx: int):
        if not self.audioProject or self.audioProject.length <= 0:
            return

        self.updateCurrentSegment(idx - 1)

    # **************************************************************************
    def onTogglePlay(self):
        if not self.audioProject or self.audioProject.length <= 0:
            return

        if self.ui.audioPlayer.playbackState() == QMediaPlayer.PlayingState:
            self.pauseSegment()
        else:
            self.playSegment()

    # **************************************************************************
    def onDurationChange(self, duration):
        self.ui.playSlider.setMaximum(duration)

    # **************************************************************************
    def displayCurrentSegment(self):
        if not self.audioProject or self.audioProject.length <= 0:
            return

        recording = self.audioProject.recordings[self.currentRecording]
        if recording.speechSegments:
            segment = recording.speechSegments[self.currentSegment]

            self.ui.transcript.setPlainText(segment.text)
            self.ui.lblSegment.setText(
                f'[E: {hmsTimestamp(tms(segment.end), shorten=True)}({segment.end:,.3f}) - '
                f'S: {hmsTimestamp(tms(segment.start), shorten=True)}({segment.start:,.3f}), '
                f'\u0394{tms(segment.end)-tms(segment.start):,}ms] '
                f'{self.currentSegment+1:03}/{len(recording.speechSegments)}')

            self.ui.audioSpectrumArea.audioSpectrum.currentSegment = self.currentSegment
            self.ui.audioSpectrumArea.showSegment(self.currentSegment)

            self.ui.tbvListing.selectRow(self.currentSegment)
            idx = self.recordingsModel.index(self.currentSegment, 0)
            self.ui.tbvListing.selectionModel().select(
                idx,
                QItemSelectionModel.ClearAndSelect |
                QItemSelectionModel.SelectionFlag.Rows
            )
            self.ui.tbvListing.scrollTo(idx)

            if self.ui.audioPlayer.playbackState() == QMediaPlayer.PlayingState:
                self.playSegment()

            if self.ui.sbxIndex.value() - 1 != self.currentSegment:
                self.ui.sbxIndex.setValue(self.currentSegment + 1)

    # **************************************************************************
    def onNew(self) -> None:
        wizard = RProjectWizard(newProject=True)
        result = wizard.exec()
        if result:
            projectFolder = (Path(wizard.field('BaseDirectory').strip()) /
                             wizard.field('ProjectName').strip())
            try:
                self.audioProject.new(folder=projectFolder,
                                      name=wizard.field('ProjectName').strip(),
                                      author=wizard.field('AuthorName').strip(),
                                      email=wizard.field('AuthorEmail').strip(),
                                      description=wizard.field('ProjectDescription'))
                path = self.audioProject.data.filePath
                # Close the project model object to save it to disc and set the data to None
                # so that loadAudioProject gets an empty model
                self.audioProject.close(save=True)

                self.loadAudioProject(path)
                self.statusBar().showMessage(
                    text=f'New project created: {self.audioProject.data.title}',
                    timeout=3000)
            except Exception as e:
                qApp.logger.error(f'Project Directory: "{projectFolder} '
                                  f'could not be created: {e!r}')

    # **************************************************************************
    def onOpen(self) -> None:
        wizard = RProjectWizard(newProject=False)
        result = wizard.exec()
        if result:
            prjFilename: str = wizard.field('ProjectFile')
            self.loadAudioProject(Path(prjFilename))

    # **************************************************************************
    def playSegment(self):
        if not self.audioProject or self.audioProject.length <= 0:
            return

        recording = self.audioProject.recordings[self.currentRecording]
        segment = recording.speechSegments[self.currentSegment]
        self.ui.audioPlayer.setPosition(tms(segment.start))
        self.ui.videoPlayer.setPosition(tms(segment.start))
        self.ui.audioPlayer.play()
        self.ui.videoPlayer.play()

        self.ui.btnPlay.setText("Pause")
        icon = QIcon(':/images/icons/media-playback-pause.png')
        self.ui.btnPlay.setIcon(icon)

    # **************************************************************************
    def pauseSegment(self):
        self.ui.audioPlayer.pause()
        self.ui.videoPlayer.pause()

        self.ui.btnPlay.setText("Play")
        icon = QIcon(':/images/icons/media-playback-start.png')
        self.ui.btnPlay.setIcon(icon)

    # **************************************************************************
    def onPositionChange(self, pos):
        self.ui.playSlider.setValue(pos)
        self.ui.lblCurrentPosition.setText(hmsTimestamp(pos, shorten=True))

        if not self.audioProject or self.audioProject.length <= 0:
            self.pauseSegment()
            return

        recording = self.audioProject.recordings[self.currentRecording]
        segment = recording.speechSegments[self.currentSegment]
        if pos > tms(segment.end):
            self.pauseSegment()
            if self.ui.cbxLoop.isChecked():
                QTimer.singleShot(1000, self.playSegment)

    # **************************************************************************
    def onOpenRecent(self) -> None:
        action: QAction = self.sender()  # type: ignore
        if action:
            self.loadAudioProject(action.data())

    # **************************************************************************
    def onExportSrt(self) -> None:
        if self.audioProject:
            filePath, _ = QFileDialog.getSaveFileName(
                self,'Export SRT',
                str(self.audioProject.data.folder), 'SRT Files (*.srt)')
            if filePath:
                try:
                    self.audioProject.saveSrt(self.currentRecording, filePath)
                except Exception as e:
                    qApp.logger.error(f"Failed to export SRT: {e!s}")
                else:
                    qApp.logger.info(f"Exported SRT to {filePath}")
                    self.statusBar().showMessage(text=f"Exported SRT to {filePath}",
                                                 timeout=5000)

    # **************************************************************************
    def onExit(self) -> None:
        self.onProjectClose()
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
        qApp.logger.debug(f"Adjusting recent list for {projectFilename}")
        settings = RSettings()
        recentFiles: List[Path] = settings.Main.RecentFiles
        qApp.logger.debug(f"Total recents[{len(recentFiles)}] "
                          f"{', '.join(f'{rf!s}' for rf in recentFiles)}")

        while projectFilename in recentFiles:
            recentFiles.remove(projectFilename)
        recentFiles.insert(0, projectFilename)
        if len(recentFiles) > self.ui.maxRecentCount:
            del recentFiles[self.ui.maxRecentCount:]
        settings.Main.RecentFiles = recentFiles
        settings.save()
        qApp.logger.debug(f"Updated recents[{len(recentFiles)}] "
                          f"{', '.join(f'{rf!s}' for rf in recentFiles)}")

        self.updateRecentFileList()

    # **************************************************************************
    def updateRecentFileList(self):
        settings = RSettings()
        recentFiles: List[Path] = settings.Main.RecentFiles
        total: int = min(len(recentFiles), settings.Main.RecentMaxCount)
        qApp.logger.debug(f"Total recents[{total}] "
                          f"{', '.join(f'{rf!s}' for rf in recentFiles)}")

        for i in range(total):
            recentFile = recentFiles[i]
            fn = recentFile.stem
            act = self.ui.recentFileActionList[i]
            act.setText(f'&{i + 1}. {fn}')
            act.setIcon(QIcon(':/images/icons/folder-bookmark.png'))
            act.setVisible(True)
            act.setToolTip(str(recentFile))
            act.setData(recentFile)

        for i in range(total, self.ui.maxRecentCount):
            self.ui.recentFileActionList[i].setVisible(False)

        hasRecent: bool = total > 0
        self.ui.actionClearRecent.setEnabled(hasRecent)
        self.ui.recentSeperator.setVisible(hasRecent)

    # **************************************************************************
    def onClearRecentFiles(self):
        settings = RSettings()
        settings.Main.RecentFiles.clear()
        settings.save()
        self.updateRecentFileList()

    # **************************************************************************
    def onListingDoubleClick(self, index: QModelIndex):
        row = index.row()
        self.updateCurrentSegment(row)

    # **************************************************************************
    def updateCurrentSegment(self, idx: int):
        recording = self.audioProject.recordings[self.currentRecording]
        segmentCount = len(recording.speechSegments)
        idx = max(min(segmentCount - 1, idx), 0)
        if idx != self.currentSegment:
            self.currentSegment = idx
            self.displayCurrentSegment()

    # **************************************************************************
    def loadAudioProject(self, projectFilePath: Path):
        qApp.logger.info(f'Loading {projectFilePath!s}...')
        self.setWindowFilePath(str(projectFilePath))
        self.adjustRecentListForCurrent(projectFilePath)

        self.clearRecordingsUi()
        self.ui.actionClose.setEnabled(False)

        timer = QElapsedTimer()
        timer.start()

        # Load project model
        try:
            self.audioProject.open(projectFilePath)
        except AudioProjectException as ae:
            qApp.logger.error(str(ae))
            return

        t1 = timer.elapsed()
        timer.restart()

        # Update project view
        projectData = self.audioProject.data
        projectFolder: Path = projectData.folder

        self.ui.leProjectTitle.setText(projectData.title)
        self.ui.leProjectFolder.setText(str(projectData.folder))
        self.ui.leCreation.setText(f"{projectData.createdOn!s}")
        self.ui.leAuthorName.setText(projectData.authorName)
        self.ui.leAuthorEmail.setText(projectData.authorEmail)
        self.ui.tbxDescription.setPlainText(projectData.description)

        self.setProjectUiEnabled(True)

        if projectData.hasRecordings():
            # Load all the recordings data
            self.audioProject.loadRecordings()

            self.ui.lblRecordingsTitle.setText(f'Audio Recordings: <b>'
                                               f'{projectData.title}</b> '
                                               f'[{len(projectData.recordings)}]')
            # for recording in self.audioRecordings:
            #     self.ui.lblRecordingsTitle.setText(str(recording[0]))

            self.currentRecording = 0
            recording = self.audioProject.recordings[self.currentRecording]
            self.ui.audioPlayer.setSource(recording.audioUrl)
            self.ui.audioSpectrumArea.audioSpectrum.setSource(recording.audioData, recording.speechSegments)
            self.recordingsModel.setSegments(recording.speechSegments)
            self.ui.tbvListing.resizeColumnsToContents()

            self.currentSegment = 0
            self.displayCurrentSegment()

            self.ui.videoPlayer.setSource(recording.videoUrl)
            self.ui.lblCurrentPosition.setText(hmsTimestamp(0, shorten=True, fixedPrecision=True))
            self.ui.lblTotalLength.setText(hmsTimestamp(len(recording.speechSegments), shorten=True, fixedPrecision=True))

            self.setRecordingUiEnabled(True)
        else:
            self.clearRecordingsUi()
            self.setRecordingUiEnabled(False)

        t2 = timer.elapsed()

        self.ui.autoSaveTimer.start(RSettings().Main.AutoSaveInterval * 60 * 1000)
        self.statusBar().showMessage(f'Loaded project {projectData.title}({projectData.folder})', 3000)
        qApp.logger.debug(f'Project {projectData.title} loaded in {t1} ms, UI loaded in {t2} ms.')

    # **************************************************************************
    def onAutoSave(self):
        qApp.logger.info(f"Autosaving project {self.audioProject.data.title}({self.audioProject.data.folder})")
        self.onSave()

    # **************************************************************************
    def onSave(self):
        if self.audioProject:
            self.audioProject.save()
            projectData = self.audioProject.data
            self.statusBar().showMessage(f'Saved project {projectData.title}({projectData.folder})', 3000)

    # **************************************************************************
    def onProjectClose(self):
        if self.audioProject:
            if self.audioProject.data.isModified:
                button = QMessageBox.warning(
                    self,
                    "Unsaved project",
                    "You have unsaved project data. How do you want to continue?",
                    buttons=QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                    defaultButton=QMessageBox.Save,
                )
                if button == QMessageBox.Cancel:
                    return
                self.audioProject.close(save=(button == QMessageBox.Save))

            projectData = self.audioProject.data
            qApp.logger.info(f"Closing project {projectData.title}({projectData.folder})")

            self.clearRecordingsUi()
            self.setRecordingUiEnabled(False)

            self.audioProject = None
            self.clearProjectUi()
            self.setProjectUiEnabled(False)


# ******************************************************************************
