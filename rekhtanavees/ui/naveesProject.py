# ******************************************************************************
# Copyright (c) 2025. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QObject, Signal, QUrl

from rekhtanavees.audio import AudioClip, loadTranscript, saveTranscript, writeSrtFile, Segment
from rekhtanavees.audio.audioproject import AudioProject


# ******************************************************************************
@dataclass
class Recording:
    audioUrl: QUrl
    audioData: AudioClip  # Or whatever type audioData is
    speechSegments: list[Segment] # Adjust the type based on your segments
    videoUrl: QUrl

# ******************************************************************************
class NaveesProject(QObject):
    """Project class based on QObject to interact with the UI."""

    # --------------------------------------------------------------------------
    projectModified = Signal(bool)
    """Indicates change in project modification status."""

    # --------------------------------------------------------------------------
    def __init__(self, parent: QObject):
        super(NaveesProject, self).__init__(parent)

        self.data: AudioProject | None = None
        self.recordings: list[Recording] = []

    # --------------------------------------------------------------------------
    def modificationStatusChanged(self):
        assert self.data is None

    # --------------------------------------------------------------------------
    def new(self, folder: Path, name: str, author: str, email: str, description: str):
        assert self.data is None
        # Create project directory
        folder.mkdir(parents=True, exist_ok=True)
        qApp.logger.debug(f'Project directory "{folder}" successfully created')

        self.data = AudioProject(path=folder, name=name)

        self.data.title = name
        self.data.authorName = author
        self.data.authorEmail = email
        self.data.description = description

        def projectChanged(status: bool) -> None:
            self.projectModified.emit(status)
        self.data.notifyObserver = projectChanged

        self.data.saveProject()
        qApp.logger.info(f'New project file "{self.data.filename}" created in {self.data.folder}')

    # --------------------------------------------------------------------------
    def open(self, projectFilePath: Path):
        assert self.data is None
        self.data = AudioProject(path=projectFilePath)
        self.data.loadProject()

    # --------------------------------------------------------------------------
    def save(self):
        assert self.data

        self.data.saveProject()

    # --------------------------------------------------------------------------
    def saveAs(self, filePath: Path):
        assert self.data

        self.data.setFilePath(filePath)
        self.data.saveProject()

    # --------------------------------------------------------------------------
    def close(self, save: bool = True):
        if self.data is None:
            return

        if save and self.data.isModified:
            self.data.saveProject()

        self.data = None
        self.recordings = []

    # --------------------------------------------------------------------------
    def loadRecordings(self):
        if self.data.hasRecordings():
            self.recordings = []
            for recording in self.data.recordings:
                af = self.data.folder / recording.audioFile
                rec = Recording(
                    audioUrl=QUrl.fromLocalFile(af.resolve()),
                    audioData=AudioClip.createAudioClip(af),
                    speechSegments=loadTranscript(self.data.folder / recording.transcriptFile),
                    videoUrl=QUrl.fromLocalFile(self.data.folder / recording.videoFile) if recording.hasVideo() else QUrl()
                )
                self.recordings.append(rec)

    # **************************************************************************
    def saveRecordings(self):
        if self.length == 0:
            return

        for i, recording in enumerate(self.recordings):
            transcriptFile = (Path(self.data.folder) / self.data.recordings[i].transcriptFile).resolve()
            qApp.logger.debug(f'Saving {transcriptFile!s}')

            # Save the transcript file
            saveTranscript(transcriptFile, recording.speechSegments)

            # TODO: Add config option to automatic/manual SRT export
            # Save the SRT file if automatic export to SRT is selected
            # srtFile = transcriptFile.with_suffix('.srt')
            # writeSrtFile(srtFile, transcript)
            qApp.logger.info(f'Saved {transcriptFile!s}')

    # **************************************************************************
    def saveSrt(self, index: int, filename: str) -> None:
        if self.length == 0:
            return

        if index < 0 or index >= self.length:
            raise ValueError(f'Invalid recording index: {index}')

        if not filename:
            raise ValueError(f'Invalid filename for saving SRT: {filename}')

        writeSrtFile(filename, self.recordings[index].speechSegments)

    # --------------------------------------------------------------------------
    @property
    def length(self):
        return len(self.recordings)


# ******************************************************************************
