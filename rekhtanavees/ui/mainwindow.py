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

from PySide6.QtCore import QUrl, Qt, QTimer, QPoint, QEvent, QSize
from PySide6.QtGui import (
    QAction, QIcon, QPixmap, QKeyEvent, QPainter, QBrush,
    QColor, QResizeEvent, QFont, QTextOption, QFontMetrics, QFontDatabase,
    QSyntaxHighlighter, QTextCharFormat
)
from PySide6.QtMultimedia import QMediaPlayer, QMediaDevices, QAudioOutput
from PySide6.QtMultimediaWidgets import QGraphicsVideoItem
from PySide6.QtWidgets import (
    QMainWindow, QMessageBox, QWidget,
    QGraphicsScene, QGraphicsTextItem, QStyleOption, QStyle
)

from rekhtanavees.audio.audioclip import AudioClip
from rekhtanavees.audio.clipimage import ClipImage
from rekhtanavees.audio.transcript import loadTranscript, saveTranscript
from rekhtanavees.audio.audioproject import AudioProject, AudioProjectException
from rekhtanavees.constants import Rx
from rekhtanavees.settings import RSettings
from rekhtanavees.ui.mainwindow_ui import Ui_rekhtaNavees
from rekhtanavees.ui.projectwizard import RProjectWizard
from rekhtanavees.ui.recordingwidget_ui import Ui_recordingWidget


# ******************************************************************************
def tms(x: int | float) -> int:
    """Convert seconds to milliseconds (int)"""
    return int(x * 1000)


# ******************************************************************************
class RHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(RHighlighter, self).__init__(parent)
        self._mappings = {}

    def addMapping(self, pattern: str, format_: QTextCharFormat):
        self._mappings[pattern] = format_

    def highlightBlock(self, text):
        for pattern, format_ in self._mappings.items():
            for match in re.finditer(pattern, text):
                start, end = match.span()
                self.setFormat(start, end - start, format_)


# ******************************************************************************
class ClipWidget(QWidget):
    # **************************************************************************
    def __init__(self, parent: QWidget = None):
        super(ClipWidget, self).__init__(parent)
        self.ui = Ui_recordingWidget()
        self.ui.setupUi(self)


# ******************************************************************************
class OverlayLabel(QWidget):
    def __init__(self, parent: QWidget):
        super(OverlayLabel, self).__init__(parent)
        self.darkBrush = QBrush(QColor(100, 100, 100, 128))
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        if parent:
            self.resize(parent.geometry().size())
            self.raise_()
            self.show()

    def paintEvent(self, event: QEvent):
        p = QPainter()
        p.begin(self)
        p.fillRect(self.rect(), self.darkBrush)

        white = QColor(Qt.white)
        white.setAlpha(192)
        p.setPen(white)
        p.setFont(QFont('Noto Naskh Arabic', 18))
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, "مموریکانغصیتبھنغ")
        p.end()


# ******************************************************************************
class MainWindow(QMainWindow):
    """Application MainWindow class"""

    # **************************************************************************
    def eventFilter(self, watched, event):
        if watched is self.ui.videoView and isinstance(event, QResizeEvent):
            # print(watched, event)
            sz = self.ui.videoView.geometry().size()
            self.videoItem.setSize(sz)
            c = self.ui.videoView.rect().center()
            c.setX(0)
            self.cc.setPos(c)
            self.cc.setTextWidth(sz.width())
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

        self.highlighter = RHighlighter(self)
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold)
        fmt.setForeground(Qt.gray)
        self.highlighter.addMapping(r'\s+', fmt)
        # fmt = QTextCharFormat()
        # fmt.setForeground(Qt.blue)
        # self.highlighter.addMapping(r'\S+', fmt)
        self.highlighter.setDocument(doc)

        self.ui.actionNew.triggered.connect(self.onNew)
        self.ui.actionOpen.triggered.connect(self.onOpen)
        self.ui.actionSave.triggered.connect(self.onSave)
        self.ui.actionOpenSource.triggered.connect(self.onOpenSource)
        self.ui.actionClose.triggered.connect(self.onProjectClose)
        self.ui.actionExit.triggered.connect(self.onExit)
        self.ui.actionAbout.triggered.connect(self.onAbout)
        self.ui.actionAboutQt.triggered.connect(qApp.aboutQt)

        self.autoSaveTimer = QTimer(self)
        self.autoSaveTimer.timeout.connect(self.onAutoSave)

        # Recent files
        self.maxRecentCount = RSettings().Main.RecentMaxCount

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

        self.audioProject = None
        self.audioRecordings = []

        self.scene = QGraphicsScene()

        self.cc = QGraphicsTextItem()
        self.cc.setZValue(100)
        self.cc.setFont(QFont('Noto Naskh Arabic', 18))
        self.cc.setDefaultTextColor(Qt.white)
        to = self.cc.document().defaultTextOption()
        to.setTextDirection(Qt.LayoutDirection.RightToLeft)
        to.setAlignment(Qt.AlignmentFlag.AlignCenter)
        to.setFlags(QTextOption.ShowTabsAndSpaces | QTextOption.ShowLineAndParagraphSeparators)
        self.cc.document().setDefaultTextOption(to)
        self.scene.addItem(self.cc)

        self.videoItem = QGraphicsVideoItem()
        self.videoItem.setOffset(QPoint(0, 0))
        self.scene.addItem(self.videoItem)
        self.ui.videoView.setScene(self.scene)

        self.videoPlayer = QMediaPlayer()
        self.videoPlayer.setVideoOutput(self.videoItem)
        self.videoPlayer.setSource(QUrl("file:///D:/tools/urdu-youtube/ertugrul-ghazi/downloads/S01E01.mp4"))
        self.videoPlayer.durationChanged.connect(self.onDurationChanged)
        self.ui.playSlider.setEnabled(False)

        self.audioOutput = QAudioOutput(QMediaDevices.defaultAudioOutput())
        self.audioPlayer = QMediaPlayer()
        self.audioPlayer.setAudioOutput(self.audioOutput)
        self.audioPlayer.positionChanged.connect(self.loopBack)

        self.currentRecording: int = 0
        """Current recording  index.
        
        This index will be used to keep track of the current recording used for processing"""

        self.currentSegment: int = 0
        """
        Current transcript segment index.
        
        This segment will be used to keep track of the currently playing or displayed segment in the application.
        Initialized to 0.
        """

        self.ui.transcript.textChanged.connect(self.updateTranscript)
        self.ui.videoView.installEventFilter(self)

    # **************************************************************************
    def updateTranscript(self):
        text = self.ui.transcript.toPlainText()
        self.audioRecordings[self.currentRecording][1][self.currentSegment].text = text
        self.cc.setPlainText(text)

    # **************************************************************************
    def keyPressEvent(self, e: QKeyEvent):
        focus: QWidget = self.focusWidget()
        if focus is self:
            if e.key() == Qt.Key_Space:
                self.onTogglePlay()
            elif e.key() == Qt.Key_Right:
                self.updateSegment(self.currentRecording, self.currentSegment + 1)
            elif e.key() == Qt.Key_Left:
                self.updateSegment(self.currentRecording, self.currentSegment - 1)
            elif e.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.ui.transcript.setFocus()
        elif focus is self.ui.transcript:
            if e.key() in (Qt.Key_Escape, Qt.Key_Return, Qt.Key_Enter):
                self.setFocus()
        else:
            super(MainWindow, self).keyPressEvent(e)

    # **************************************************************************
    def onTogglePlay(self):
        if self.audioPlayer.playbackState() == QMediaPlayer.PlayingState:
            self.pauseSegment()
        else:
            self.playSegment()

    # **************************************************************************
    def onDurationChanged(self, duration):
        self.ui.playSlider.setMaximum(duration)

    # **************************************************************************
    def updateSegment(self, rec: int, i: int):
        segments = self.audioRecordings[rec][1]
        self.currentSegment = max(min(len(segments) - 1, i), 0)

        if segments:
            s = segments[self.currentSegment]
            ci = ClipImage(self.audioRecordings[rec][0], widthPerSec=256, height=96, direction=Qt.LayoutDirection.RightToLeft, cmap='viridis')
            img = ci.renderWords(image=ci.renderSpectrum(startTime=tms(s.start - 1),
                                                         endTime=tms(s.end + 1)),
                                 label=f'#{s.id}', words=s.words)

            self.ui.lblSpectrum.setPixmap(QPixmap(img))
            self.ui.transcript.setPlainText(s.text)
            self.ui.lblSegment.setText(f'{self.currentSegment+1:03}/{len(segments)}')

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
        s = self.audioRecordings[self.currentRecording][1][self.currentSegment]
        self.audioPlayer.setPosition(tms(s.start))
        self.videoPlayer.setPosition(tms(s.start))
        self.audioPlayer.play()
        self.videoPlayer.play()

    # **************************************************************************
    def pauseSegment(self):
        self.audioPlayer.pause()
        self.videoPlayer.pause()

    # **************************************************************************
    def loopBack(self, pos):
        self.ui.playSlider.setValue(pos)
        segment = self.audioRecordings[self.currentRecording][1][self.currentSegment]
        if pos > tms(segment.end):
            print('Looping back...')
            self.pauseSegment()
            QTimer.singleShot(1000, self.playSegment)
        elif pos < tms(segment.start):
            self.playSegment()

    # **************************************************************************
    def onOpenSource(self) -> None:
        # pdf = fitz.open(r'C:\Users\driyo\Documents\qtextlayout.h.pdf')
        # pg = pdf[0]
        # px = pg.get_pixmap(dpi=300, alpha=False)
        # img = QImage(px.samples, px.width, px.height, px.stride, QImage.Format_RGB888)
        # self.ui.transcriptionSource.setImage(img)
        self.playSegment()

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
        qApp.logger.debug(f"Adjusting recent list for {projectFilename}")
        settings = RSettings()
        recentFiles: List[Path] = settings.Main.RecentFiles
        qApp.logger.info(f"Total recents[{len(recentFiles)}] {recentFiles}")

        while projectFilename in recentFiles:
            recentFiles.remove(projectFilename)
        recentFiles.insert(0, projectFilename)
        if len(recentFiles) > self.maxRecentCount:
            del recentFiles[self.maxRecentCount:]
        settings.Main.RecentFiles = recentFiles
        settings.save()
        qApp.logger.debug(f"Updated recents[{len(recentFiles)}] {recentFiles}")

        self.updateRecentFileList()

    # **************************************************************************
    def updateRecentFileList(self):
        settings = RSettings()
        recentFiles: List[Path] = settings.Main.RecentFiles
        total: int = min(len(recentFiles), settings.Main.RecentMaxCount)
        qApp.logger.info(f"Total recents[{total}] {recentFiles}")

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
        settings = RSettings()
        settings.Main.RecentFiles.clear()
        settings.save()
        self.updateRecentFileList()

    # **************************************************************************
    def loadAudioProject(self, projectFilename: Path):
        qApp.logger.info(f'Loading {projectFilename!s}...')
        self.setWindowFilePath(str(projectFilename))
        self.adjustRecentListForCurrent(projectFilename)

        self.clearRecordings()
        self.ui.actionClose.setEnabled(False)

        projectFolder: Path = projectFilename.parent
        try:
            audioProject = AudioProject()
        except AudioProjectException as ae:
            qApp.logger.error(str(ae))
            return

        audioProject.projectFolder = str(projectFolder)
        audioProject.title = projectFilename.stem
        audioProject.loadProject()

        for recording in audioProject.recordings:
            ac = AudioClip.createAudioClip(projectFolder / recording.audioFile)
            ts = loadTranscript(projectFolder / recording.transcriptFile)
            self.audioRecordings.append((ac, ts))

        self.audioProject = audioProject
        self.ui.lblRecordings.setText(f'Audio Recordings: <b>{self.audioProject.title}</b> [{len(self.audioProject.recordings)}]')
        for recording in self.audioRecordings:
            self.ui.lsvListing.addItem(str(recording[0]))
            self.ui.lsvListing.addItem(str(recording[1]))
        self.currentRecording = 0
        self.audioPlayer.setSource(QUrl.fromLocalFile(projectFolder / audioProject.recordings[self.currentRecording].audioFile))
        self.currentSegment = 0
        self.updateSegment(self.currentRecording, self.currentSegment)

        self.ui.actionClose.setEnabled(True)
        self.autoSaveTimer.start(RSettings().Main.AutoSaveInterval * 60 * 1000)
        self.statusBar().showMessage(f'Loaded project {audioProject.name}({audioProject.projectFolder})', 3000)

        self.setFocus()


    # **************************************************************************
    def saveRecordings(self):
        if self.audioProject is None or not self.audioRecordings:
            return

        qApp.logger.info(f'Saving recordings...')
        audioProject = self.audioProject

        for i, (audioClip, transcript) in enumerate(self.audioRecordings):
            transcriptFile = audioProject.projectFolder / audioProject.recordings[i].transcriptFile
            qApp.logger.info(f'Saving {transcriptFile.resolve()}')

            # Save the transcript file
            saveTranscript(transcriptFile, transcript)

        self.statusBar().showMessage(f'Saved project {audioProject.name}({audioProject.projectFolder})', 3000)

    # **************************************************************************
    def clearRecordings(self):
        self.ui.lsvListing.clear()

    # **************************************************************************
    def onAutoSave(self):
        qApp.logger.info(f"Autosaving project {self.audioProject.name}({self.audioProject.projectFolder})")
        self.onSave()

    # **************************************************************************
    def onSave(self):
        self.saveRecordings()

    # **************************************************************************
    def onProjectClose(self):
        qApp.logger.info(f"Closing project {self.audioProject.name}({self.audioProject.projectFolder})")
        self.ui.lblRecordings.setText("")
        self.ui.lsvListing.clear()
        self.autoSaveTimer.stop()
        self.statusBar().showMessage(f"AutosaveTimer: {self.autoSaveTimer.isActive()}", 5000)
        self.ui.actionClose.setEnabled(False)


# ******************************************************************************
