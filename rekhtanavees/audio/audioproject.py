
# ******************************************************************************
# Copyright (c) 2025. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
import os
from datetime import datetime, UTC
from enum import auto
from pathlib import Path
from typing import Callable

import tomlkit
from pydantic import (
    BaseModel, FilePath
)
from strenum import StrEnum
from tomlkit.exceptions import TOMLKitError

from rekhtanavees.constants import Rx
from rekhtanavees.misc.utils import isValidProjectName, slugify


# ******************************************************************************
class AudioProjectException(Exception):
    pass


# ******************************************************************************
class Age(StrEnum):
    Child = auto()
    Teenage = auto()
    Adult = auto()
    MiddleAged = auto()
    Old = auto()


class Gender(StrEnum):
    Male = auto()
    Female = auto()
    Unknown = auto()


class Speaker(BaseModel):
    title: str
    age: Age
    gender: Gender

    class Config:
        use_enum_values = True


# ******************************************************************************
class Recording(BaseModel):
    audioFile: FilePath
    """Filename of the recorded audio clip, path relative to the project file"""
    transcriptFile: FilePath
    """Filename of the transcribed text file, path relative to the project file"""
    videoFile: FilePath | None = None
    """Optional filename of the associated video file, path relative to the project file"""

    def hasVideo(self) -> bool:
        return self.videoFile is not None


# ******************************************************************************
class AudioProject:
    # **************************************************************************
    def __init__(self, path: Path, name: str = None):
        """
        Represents an audio project.

        Args:
            path (Path): Existing project directory or the path to the
                project file. Should exit in filesystem.
            name (str, optional): The name of the project (without suffix).
                If provided, it is used as the name of the project file and
                 the path should be the destination folder.
        """
        self.setFilePath(path, name)

        self._title: str = ''
        self._originator: str = ''
        self._email: str = ''
        self._narrative: str = ''
        self._dirty = False

        self.createdOn: datetime = datetime.now(UTC)
        self.lastSavedOn: datetime | None = None
        self.recordings: list[Recording] = []
        self.notifyObserver: Callable[[bool], None] | None = None

    # **************************************************************************
    @property
    def folder(self) -> Path:
        """Audio project folder path"""
        return self.filePath.parent if self.filePath else Path()

    # **************************************************************************
    @property
    def filename(self) -> str:
        """Project filename (with extension) but without path"""
        return self.filePath.name if self.filePath else ''

    # **************************************************************************
    def setFilePath(self, path: Path, name: str = None) -> None:
        """Set project filename and folder"""
        assert isinstance(path, Path)
        assert path.exists()

        if name:
            assert path.is_dir()
            assert isValidProjectName(name)
            self.filePath: Path = (path / f'{name}.toml').resolve()
        else:
            assert path.is_file()
            assert path.suffix == '.toml'
            self.filePath: Path = path

    # **************************************************************************
    @property
    def title(self) -> str:
        """Audio project title"""
        return self._title

    @title.setter
    def title(self, title: str):
        assert isinstance(title, str)

        title = title.strip()
        if title and isValidProjectName(title) and self._title != title:
            self._title = title
            self.isModified = True

    # **************************************************************************
    @property
    def authorName(self) -> str:
        """Project author name"""
        return self._originator

    @authorName.setter
    def authorName(self, author: str):
        assert isinstance(author, str)

        author = author.strip()
        if author and author != self._originator:
            self._originator = author
            self.isModified = True

    # **************************************************************************
    @property
    def authorEmail(self) -> str:
        """Project author email"""
        return self._email

    @authorEmail.setter
    def authorEmail(self, authorEmail: str):
        assert isinstance(authorEmail, str)

        authorEmail = authorEmail.strip()
        if authorEmail and authorEmail != self._email:
            self._email = authorEmail
            self.isModified = True

    # **************************************************************************
    @property
    def author(self) -> str:
        """Project author identity"""
        return f'{self._originator}' + (f'<{self._email}>' if self._email else '')

    # **************************************************************************
    @property
    def description(self) -> str:
        """Project description"""
        return self._narrative

    @description.setter
    def description(self, description: str):
        assert isinstance(description, str)

        description = description.strip()
        if description != self._narrative:
            self._narrative = description
            self.isModified = True

    # **************************************************************************
    @property
    def isModified(self) -> bool:
        """Is project data modified since creation"""
        return self._dirty

    # **************************************************************************
    @isModified.setter
    def isModified(self, dirty: bool):
        """Is project data modified since creation"""
        assert  isinstance(dirty, bool)
        if self._dirty != dirty:
            self._dirty = dirty
            # broadcast modification status
            if self.notifyObserver:
                self.notifyObserver(self._dirty)

    # **************************************************************************
    @property
    def isSaved(self) -> bool:
        """Is project saved since creation"""
        return self.lastSavedOn is not None

    # **************************************************************************
    def hasRecordings(self) -> bool:
        return bool(self.recordings) and len(self.recordings) > 0

    # **************************************************************************
    def loadProject(self) -> None:
        """Load project data from the TOML file"""
        # projectFile: str = self.projectFilename()
        if not self.filePath.exists():
            raise AudioProjectException(f'Loading non-existent project file {self.filePath!s}')

        os.chdir(self.folder)
        try:
            with open(self.filePath, mode='rb') as tomlFile:
                tdoc: tomlkit.TOMLDocument = tomlkit.load(tomlFile)
        except tomlkit.exceptions.TOMLKitError as e:
            raise AudioProjectException(f'{e!s} in {self.filePath!s}')
        else:
            try:
                self.fromTomlDoc(tdoc)
                self.isModified = False
            except AssertionError as ae:
                raise AudioProjectException(str(ae))

    # **************************************************************************
    def saveProject(self) -> None:
        """Save project data to the TOML file"""
        projectFilePath: Path = self.filePath

        if not self.filePath.exists():
            tdoc = self.toTomlDoc()
        else:
            try:
                with projectFilePath.open(mode='rb') as tomlFile:
                    tdoc = tomlkit.load(tomlFile)
                    self.updateTomlDoc(tdoc)
            except tomlkit.exceptions.TOMLKitError:
                # Backup the toml file with error and get a new TOML representation of the project
                projectFileBackup: Path = projectFilePath.with_name(f'{projectFilePath.name}.bak')
                projectFileBackup.unlink(missing_ok=True)  # remove any previous backup file of same name
                projectFilePath.rename(projectFileBackup)
                tdoc = self.toTomlDoc()

        # update last saved time
        tdoc['general']['lastSavedOn'] = datetime.now(UTC)
        try:
            with projectFilePath.open(mode='wb+') as tomlFile:
                tomlFile.write(tomlkit.dumps(tdoc).encode('utf-8'))
                self.isModified = False
        except tomlkit.exceptions.TOMLKitError as ex:
            raise AudioProjectException(f'{ex!s} in {projectFilePath!s}')

    # **************************************************************************
    def fromTomlDoc(self, tdoc: tomlkit.TOMLDocument):
        """Validation helper function to load the project data from TOML document.

        Raises:
            AssertionError: if the TOML document is not valid.
        """
        assert 'RekhtaNaveesVersion' in tdoc, '"RekhtaNaveesVersion" key is absent'
        assert tdoc['RekhtaNaveesVersion'] == str(Rx.ApplicationVersion), \
            (f'"RekhtaNaveesVersion" mismatch Application v{str(Rx.ApplicationVersion)} '
             f'vs Project v{tdoc["RekhtaNaveesVersion"]}')

        assert 'general' in tdoc, '"general" table is absent'
        general: dict = tdoc['general']  # type: ignore

        assert 'title' in general, '"title" key is absent'
        self._title = general['title']
        assert 'authorName' in general, '"authorName" key is absent'
        self._originator = general['authorName']
        assert 'authorEmail' in general, '"authorEmail" key is absent'
        self._email = general['authorEmail']
        if 'description' in general:
            self._narrative = general['description']
        if 'createdOn' in general:
            self.createdOn = general['createdOn']
        if 'lastSavedOn' in general:
            self.lastSavedOn = general['lastSavedOn']

        self.recordings.clear()  # reset any previous recordings
        if 'recordings' in tdoc:
            for i, record in enumerate(tdoc['recordings']):  # type: ignore
                assert 'audioFile' in record, f'"audioFile" key is absent in recording #{i}'
                assert 'transcriptFile' in record, f'"transcriptFile" key is absent in recording #{i}'
                videoFile = Path(record['videoFile']) if 'videoFile' in record else None
                recording = Recording(audioFile=Path(record['audioFile']),
                                      transcriptFile=Path(record['transcriptFile']),
                                      videoFile=videoFile)

                self.recordings.append(recording)

    # **************************************************************************
    def toTomlDoc(self) -> tomlkit.TOMLDocument:
        """Helper function to convert the project data to a TOML document.

        Raises:
            AssertionError: if the project data is not valid.
        """
        tdoc = tomlkit.TOMLDocument()
        # Header Section
        (tdoc
         .add(tomlkit.comment("*" * 78))
         .add(tomlkit.comment("Rekhta Navees audio project file."))
         .add(tomlkit.nl())
         .add('RekhtaNaveesVersion', str(Rx.ApplicationVersion))
         .add(tomlkit.nl()).add(tomlkit.comment("*" * 78)))

        # General Section
        general = tomlkit.table()
        assert self._title != '', 'Title not provided'
        general['title'] = self._title
        assert self._originator != '', 'Author not provided'
        general['authorName'] = self._originator
        assert self._email != '', 'Author email not provided'
        general['authorEmail'] = self._email
        if self._narrative:
            general.add('description', tomlkit.string(f'\n{self._narrative}\n', multiline=True))
        general.add('createdOn', self.createdOn)
        if self.lastSavedOn:
            general.add('lastSavedOn', self.lastSavedOn)
        tdoc.add('general', general)
        tdoc.add(tomlkit.nl()).add(tomlkit.comment("*" * 78))

        # Recordings list Section
        recordings = tomlkit.aot()
        for i, record in enumerate(self.recordings):
            recordings.append(
                tomlkit.table()
                .add('audioFile', str(record.audioFile))
                .add('transcriptFile', str(record.transcriptFile))
                .add('videoFile', str(record.videoFile))
            )
        tdoc.add('recordings', recordings)
        tdoc.add(tomlkit.nl()).add(tomlkit.comment("*" * 78))

        return tdoc

    # **************************************************************************
    def updateTomlDoc(self, tdoc: tomlkit.TOMLDocument):
        """Helper function to convert the project data to existing TOML document.

        Raises:
            AssertionError: if the project data is not valid.
        """
        tdoc['RekhtaNaveesVersion'] = str(Rx.ApplicationVersion)

        general = tdoc['general'] if 'general' in tdoc else toml.table()  # type: ignore
        assert self._title != '', 'Title not provided'
        general['title'] = self._title
        assert self._originator != '', 'Author not provided'
        general['authorName'] = self._originator
        assert self._email != '', 'Author email not provided'
        general['authorEmail'] = self._email
        if self._narrative:
            general['description'] = tomlkit.string(f'\n{self._narrative}\n', multiline=True)
        elif 'description' in general:
            general.pop('description')
        general['createdOn'] = self.createdOn
        if self.lastSavedOn:
            general.add('lastSavedOn', self.lastSavedOn)
        tdoc['general'] = general

        recordings = tdoc['recordings'] if 'recordings' in tdoc else tomlkit.aot()  # type: ignore
        R, r = len(self.recordings), len(recordings)
        hasMore: bool = R > r
        recordingsToUpdate = self.recordings[:(r if hasMore else R)]
        for i, record in enumerate(recordingsToUpdate):
            recordings[i].update({
                'audioFile': str(record.audioFile),
                'transcriptFile': str(record.transcriptFile),
                'videoFile': str(record.videoFile)
            })
        if hasMore:
            for i, record in enumerate(self.recordings[r:]):
                recordings.append(
                    tomlkit.table()
                    .add('audioFile', str(record.audioFile))
                    .add('transcriptFile', str(record.transcriptFile))
                    .add('videoFile', str(record.videoFile))
                )
        else:
            del recordings[R:]
        tdoc['recordings'] = recordings


# ******************************************************************************
