# -*- coding: utf-8 -*-
# ******************************************************************************
# Copyright (c) 2022. All rights reserved.
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
    QFont, QTextOption, QFontMetrics, QFontDatabase,
    QSyntaxHighlighter, QTextCharFormat
)
from PySide6.QtMultimedia import QMediaPlayer, QMediaDevices, QAudioOutput
from PySide6.QtMultimediaWidgets import QGraphicsVideoItem
from PySide6.QtWidgets import (
    QMainWindow, QMessageBox, QWidget,
    QGraphicsScene, QGraphicsTextItem, QStyleOption, QStyle, QFileDialog
)

from rekhtanavees.audio import AudioClip, loadTranscript, saveTranscript, writeSrtFile
from rekhtanavees.audio.audioproject import AudioProject, AudioProjectException
from rekhtanavees.constants import Rx
from rekhtanavees.misc.utils import hmsTimestamp, tms
from rekhtanavees.settings import RSettings
from rekhtanavees.ui.mainwindow_ui import Ui_rekhtaNavees
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

        for fnt in [":/fonts/fonts/NotoNaskhArabic-Regular.ttf",
                    ":/fonts/fonts/NotoSans-Regular.ttf",
                    ":/fonts/fonts/Mehr_Nastaliq_Web_v2.0.ttf",
                    ":/fonts/fonts/NotoSansMono-Regular.ttf",
                    ":/fonts/fonts/NotoSansMono-Condensed-Regular.ttf"]:
            QFontDatabase.addApplicationFont(fnt)

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

        self.audioProject: AudioProject | None = None
        self.audioRecordings: list = []
        self.currentRecording: int = 0
        """Current recording  index.

        This index will be used to keep track of the current recording used for processing"""

        self.currentSegment: int = 0
        """
        Current transcript segment index.

        This segment will be used to keep track of the currently playing or displayed segment in the application.
        Initialized to 0.
        """

        self.clearRecordingsUi()
        self.setRecordingUiEnabled(False)

        self.clearProjectUi()
        self.setProjectUiEnabled(False)

    # **************************************************************************
    def setProjectUiEnabled(self, enabled: bool):
        if enabled:
            self.ui.actionSave.setEnabled(True)
            self.ui.actionClose.setEnabled(True)

            self.ui.actionDetails.setEnabled(True)
            self.ui.dckProjectDetailsContents.setEnabled(True)

            self.ui.autoSaveTimer.start(RSettings().Main.AutoSaveInterval * 60 * 1000)

        else:
            self.ui.actionSave.setDisabled(True)
            self.ui.actionClose.setDisabled(True)

            self.ui.actionDetails.setDisabled(True)
            self.ui.dckProjectDetailsContents.setDisabled(True)

            self.ui.autoSaveTimer.stop()

    # **************************************************************************
    def setRecordingUiEnabled(self, enabled: bool):
        if enabled:
            recording = self.audioRecordings[0]
            self.ui.sbxIndex.setMinimum(1)
            self.ui.sbxIndex.setMaximum(len(recording[1]))
            self.ui.sbxIndex.setSuffix(f"/{len(recording[1])}")
            self.ui.sbxIndex.setEnabled(True)

            self.ui.btnPlay.setEnabled(True)
            self.ui.cbxLoop.setEnabled(True)

            self.ui.menuRecordings.setEnabled(True)
            self.ui.recordingToolBar.setVisible(True)
            self.ui.actionExportSRT.setEnabled(True)

            self.ui.videoView.setEnabled(True)
            self.ui.tbvListing.setEnabled(True)
            self.ui.transcript.setEnabled(True)
        else:
            self.ui.sbxIndex.setMinimum(0)
            self.ui.sbxIndex.setMaximum(0)
            self.ui.sbxIndex.setSuffix("")
            self.ui.sbxIndex.setDisabled(True)
            self.ui.sbxIndex.valueChanged.connect(self.onIndexChanged)

            self.ui.btnPlay.setDisabled(True)
            self.ui.cbxLoop.setDisabled(True)

            self.ui.menuRecordings.setDisabled(True)
            self.ui.recordingToolBar.setHidden(True)
            self.ui.actionExportSRT.setEnabled(True)

            self.ui.videoView.setDisabled(True)
            self.ui.tbvListing.setDisabled(True)
            self.ui.transcript.setDisabled(True)

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
        if self.audioRecordings:
            self.audioRecordings[self.currentRecording][1][self.currentSegment].text = text
            self.ui.sceneCaption.setPlainText(text)

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
        if len(self.audioRecordings) == 0:
            return

        self.updateCurrentSegment(idx - 1)

    # **************************************************************************
    def onTogglePlay(self):
        if len(self.audioRecordings) == 0:
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
        if len(self.audioRecordings) == 0:
            return

        segments = self.audioRecordings[self.currentRecording][1]
        if segments:
            s = segments[self.currentSegment]

            self.ui.transcript.setPlainText(s.text)
            self.ui.lblSegment.setText(
                f'[E: {hmsTimestamp(tms(s.end), shorten=True)}({s.end:,.3f}) - '
                f'S: {hmsTimestamp(tms(s.start), shorten=True)}({s.start:,.3f}), '
                f'\u0394{tms(s.end)-tms(s.start):,}ms] '
                f'{self.currentSegment+1:03}/{len(segments)}')

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
            prjDir = Path(wizard.field('BaseDirectory').strip()) / wizard.field('ProjectName').strip()
            try:
                # Create project directory
                prjDir.mkdir(parents=True, exist_ok=True)
                qApp.logger.info(f'Project directory "{prjDir}" successfully created')  # type: ignore

                # Create new Project object and save to the directory
                audioProject = AudioProject()
                audioProject.name = wizard.field('ProjectName')
                audioProject.folder = str(prjDir)
                audioProject.authorName = wizard.field('AuthorName')
                audioProject.authorEmail = wizard.field('AuthorEmail')
                audioProject.description = wizard.field('ProjectDescription')
                audioProject.saveProject()
                qApp.logger.info(f'New project file "{audioProject.projectFilename()}" created')  # type: ignore

                # Load the saved project
                self.loadAudioProject(Path(audioProject.projectFilename()))
                self.statusBar().showMessage(f'New project created: {audioProject.name}', 3000)

            except Exception as e:
                qApp.logger.error(f'Project Directory: "{prjDir}" could not be created: {e!r}')  # type: ignore

    # **************************************************************************
    def onOpen(self) -> None:
        wizard = RProjectWizard(newProject=False)
        result = wizard.exec()
        if result:
            prjFilename: str = wizard.field('ProjectFile')
            self.loadAudioProject(Path(prjFilename))

    # **************************************************************************
    def playSegment(self):
        if len(self.audioRecordings) == 0:
            return

        s = self.audioRecordings[self.currentRecording][1][self.currentSegment]
        self.ui.audioPlayer.setPosition(tms(s.start))
        self.ui.videoPlayer.setPosition(tms(s.start))
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

        if len(self.audioRecordings) == 0:
            self.pauseSegment()
            return

        segment = self.audioRecordings[self.currentRecording][1][self.currentSegment]
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
                self.audioProject.projectFolder, 'SRT Files (*.srt)')
            if filePath:
                try:
                    writeSrtFile(filePath, self.audioRecordings[self.currentRecording][1])
                except Exception as e:
                    qApp.logger.error(f"Failed to export SRT: {e!s}")
                else:
                    qApp.logger.info(f"Exported SRT to {filePath}")
                    self.statusBar().showMessage(f"Exported SRT to {filePath}", 5000)

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
        qApp.logger.debug(f"Total recents[{len(recentFiles)}] {', '.join(f'{rf!s}' for rf in recentFiles)}")

        while projectFilename in recentFiles:
            recentFiles.remove(projectFilename)
        recentFiles.insert(0, projectFilename)
        if len(recentFiles) > self.ui.maxRecentCount:
            del recentFiles[self.ui.maxRecentCount:]
        settings.Main.RecentFiles = recentFiles
        settings.save()
        qApp.logger.debug(f"Updated recents[{len(recentFiles)}] {', '.join(f'{rf!s}' for rf in recentFiles)}")

        self.updateRecentFileList()

    # **************************************************************************
    def updateRecentFileList(self):
        settings = RSettings()
        recentFiles: List[Path] = settings.Main.RecentFiles
        total: int = min(len(recentFiles), settings.Main.RecentMaxCount)
        qApp.logger.debug(f"Total recents[{total}] {', '.join(f'{rf!s}' for rf in recentFiles)}")

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
        segments = self.audioRecordings[self.currentRecording][1]
        idx = max(min(len(segments) - 1, idx), 0)
        if idx != self.currentSegment:
            self.currentSegment = idx
            self.displayCurrentSegment()

    # **************************************************************************
    def loadAudioProject(self, projectFilename: Path):
        qApp.logger.info(f'Loading {projectFilename!s}...')
        self.setWindowFilePath(str(projectFilename))
        self.adjustRecentListForCurrent(projectFilename)

        self.clearRecordingsUi()
        self.ui.actionClose.setEnabled(False)

        projectFolder: Path = projectFilename.parent
        try:
            audioProject = AudioProject()
        except AudioProjectException as ae:
            qApp.logger.error(str(ae))
            return

        timer = QElapsedTimer()
        timer.start()

        audioProject.projectFolder = str(projectFolder)
        audioProject.title = projectFilename.stem
        audioProject.loadProject()

        self.audioProject = audioProject

        self.ui.leProjectTitle.setText(self.audioProject.title)
        self.ui.leProjectFolder.setText(self.audioProject.folder)
        self.ui.leCreation.setText(f"{self.audioProject.createdOn!s}")
        self.ui.leAuthorName.setText(self.audioProject.authorName)
        self.ui.leAuthorEmail.setText(self.audioProject.authorEmail)
        self.ui.tbxDescription.setPlainText(self.audioProject.description)

        self.setProjectUiEnabled(True)

        if self.audioProject.hasRecordings():
            for recording in audioProject.recordings:
                ac = AudioClip.createAudioClip(projectFolder / recording.audioFile)
                ts = loadTranscript(projectFolder / recording.transcriptFile)
                vid = QUrl.fromLocalFile(projectFolder / recording.videoFile) if recording.hasVideo() else QUrl()
                self.audioRecordings.append((ac, ts, vid))

            t1 = timer.elapsed()
            timer.restart()

            self.ui.lblRecordingsTitle.setText(f'Audio Recordings: <b>{self.audioProject.title}</b> [{len(self.audioProject.recordings)}]')
            # for recording in self.audioRecordings:
            #     self.ui.lblRecordingsTitle.setText(str(recording[0]))

            self.currentRecording = 0
            recording = self.audioRecordings[self.currentRecording]
            self.ui.audioPlayer.setSource(QUrl.fromLocalFile(projectFolder / audioProject.recordings[self.currentRecording].audioFile))
            self.ui.audioSpectrumArea.audioSpectrum.setSource(recording[0], recording[1])
            self.recordingsModel.setSegments(self.audioRecordings[self.currentRecording][1])
            self.ui.tbvListing.resizeColumnsToContents()

            self.currentSegment = 0
            self.displayCurrentSegment()

            self.ui.videoPlayer.setSource(self.audioRecordings[self.currentRecording][2])
            self.ui.lblCurrentPosition.setText(hmsTimestamp(0, shorten=True, fixedPrecision=True))
            self.ui.lblTotalLength.setText(hmsTimestamp(len(recording[0]), shorten=True, fixedPrecision=True))

            self.setRecordingUiEnabled(True)

            t2 = timer.elapsed()
        else:
            t1 = timer.elapsed()
            timer.restart()

            self.clearRecordingsUi()
            self.setRecordingUiEnabled(False)

            t2 = timer.elapsed()

        self.ui.autoSaveTimer.start(RSettings().Main.AutoSaveInterval * 60 * 1000)
        self.statusBar().showMessage(f'Loaded project {audioProject.name}({audioProject.projectFolder})', 3000)
        qApp.logger.debug(f'Project {audioProject.name} loaded in {t1} ms, UI loaded in {t2} ms.')

    # **************************************************************************
    def saveRecordings(self):
        if self.audioProject is None or not self.audioRecordings:
            return

        audioProject = self.audioProject

        for i, (audioClip, transcript, video) in enumerate(self.audioRecordings):
            transcriptFile = Path(audioProject.projectFolder) / audioProject.recordings[i].transcriptFile
            qApp.logger.info(f'Saving {transcriptFile.resolve()}')

            # Save the transcript file
            saveTranscript(transcriptFile, transcript)

            # TODO: Add config option to SRT export
            # Save the SRT file if automatic export to SRT is selected
            # srtFile = transcriptFile.with_suffix('.srt')
            # writeSrtFile(srtFile, transcript)

        self.statusBar().showMessage(f'Saved project {audioProject.name}({audioProject.projectFolder})', 3000)

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
        self.audioRecordings = []

    # **************************************************************************
    def onAutoSave(self):
        qApp.logger.info(f"Autosaving project {self.audioProject.name}({self.audioProject.projectFolder})")
        self.onSave()

    # **************************************************************************
    def onSave(self):
        if self.audioProject:
            self.audioProject.saveProject()
            self.saveRecordings()

    # **************************************************************************
    def onProjectClose(self):
        # TODO: Check unsaved data before exit

        if self.audioProject:
            qApp.logger.info(f"Closing project {self.audioProject.name}({self.audioProject.projectFolder})")
            self.clearRecordingsUi()
            self.audioRecordings = []
            self.setRecordingUiEnabled(False)

            self.clearProjectUi()
            self.audioProject = None
            self.setProjectUiEnabled(False)


# ******************************************************************************
