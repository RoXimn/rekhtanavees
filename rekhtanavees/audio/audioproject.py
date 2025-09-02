# -*- coding: utf-8 -*-
# ******************************************************************************
# Copyright (c) 2022. All rights reserved.
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
    def __init__(self):
        self.title: str = ''
        self.projectFolder: str = ''
        self.originator: str = ''
        self.email: str = ''
        self.narrative: str = ''
        self.createdOn: datetime = datetime.now(UTC)
        self.lastSavedOn: datetime = self.createdOn
        self.recordings: list[Recording] = []
        self.isModified = True

    # **************************************************************************
    @property
    def name(self) -> str:
        """Audio project title"""
        return self.title

    @name.setter
    def name(self, title: str):
        if isinstance(title, str):
            title = title.strip()
            if title and isValidProjectName(title) and self.title != title:
                self.title = title
                self.isModified = True

    # **************************************************************************
    @property
    def folder(self) -> str:
        """Audio project folder path"""
        return self.projectFolder

    @folder.setter
    def folder(self, projectFolder: str):
        if isinstance(projectFolder, str):
            projectFolder = projectFolder.strip()
            if projectFolder == '' or (Path(projectFolder).exists() and Path(projectFolder).is_dir()):
                self.projectFolder = projectFolder
                self.isModified = True

    # **************************************************************************
    @property
    def authorName(self) -> str:
        """Project author name"""
        return self.originator

    @authorName.setter
    def authorName(self, author: str):
        assert isinstance(author, str)

        author = author.strip()
        if author and author != self.originator:
            self.originator = author
            self.isModified = True

    # **************************************************************************
    @property
    def authorEmail(self) -> str:
        """Project author email"""
        return self.email

    @authorEmail.setter
    def authorEmail(self, authorEmail: str):
        assert isinstance(authorEmail, str)

        authorEmail = authorEmail.strip()
        if authorEmail and authorEmail != self.email:
            self.email = authorEmail
            self.isModified = True

    # **************************************************************************
    @property
    def author(self) -> str:
        """Project author identity"""
        return f'{self.originator} <{self.email}>'

    # **************************************************************************
    @property
    def description(self) -> str:
        """Project description"""
        return self.narrative

    @description.setter
    def description(self, description: str):
        if isinstance(description, str):
            description = description.strip()
            if description != self.narrative:
                self.narrative = description
                self.isModified = True

    # **************************************************************************
    @property
    def isDirty(self) -> bool:
        """Is project modified since loading"""
        return self.isModified

    # **************************************************************************
    def projectFilename(self) -> str:
        """Project filename with complete path"""
        if self.title:
            return str((Path(self.projectFolder) / f'{slugify(self.title)}.toml').resolve())
        else:
            return ''

    # **************************************************************************
    def projectFileExists(self) -> bool:
        """Check if the project file exists on the filesystem"""
        prjFilename = self.projectFilename()
        return bool(prjFilename) and Path(prjFilename).exists()

    # **************************************************************************
    def hasRecordings(self) -> bool:
        return bool(self.recordings) and len(self.recordings) > 0

    # **************************************************************************
    def loadProject(self) -> None:
        projectFile: str = self.projectFilename()
        if not self.projectFileExists():
            raise AudioProjectException(f'Loading non-existent project file {projectFile}')

        os.chdir(self.projectFolder)
        try:
            with open(projectFile, mode='rb') as tomlFile:
                tdoc: tomlkit.TOMLDocument = tomlkit.load(tomlFile)
        except tomlkit.exceptions.TOMLKitError as e:
            raise AudioProjectException(f'{e!s} in {projectFile}')
        else:
            try:
                self.renderTomlToProject(tdoc)
            except AssertionError as ae:
                raise AudioProjectException(str(ae))

    # **************************************************************************
    def saveProject(self) -> None:
        """Save project data to the toml file"""
        projectFilePath: Path = Path(self.projectFilename())

        if not self.projectFileExists():
            tdoc = self.renderProjectToToml()
        else:
            try:
                with projectFilePath.open(mode='rb') as tomlFile:
                    tdoc = tomlkit.load(tomlFile)
                    self.updateProjectToToml(tdoc)
            except tomlkit.exceptions.TOMLKitError:
                # Backup the toml file with error and get a new TOML representation of the project
                projectFileBackup: Path = projectFilePath.with_name(f'{projectFilePath.name}.bak')
                projectFileBackup.unlink(missing_ok=True)  # remove any previous backup file of same name
                projectFilePath.rename(projectFileBackup)
                tdoc = self.renderProjectToToml()

        # update last saved time
        tdoc['general']['lastSavedOn']: datetime.now(UTC)
        try:
            with projectFilePath.open(mode='wb+') as tomlFile:
                tomlFile.write(tomlkit.dumps(tdoc).encode('utf-8'))
        except tomlkit.exceptions.TOMLKitError as ex:
            raise AudioProjectException(f'{ex!s} in {projectFilePath!s}')

    # **************************************************************************
    def renderTomlToProject(self, tdoc: tomlkit.TOMLDocument):
        assert 'RekhtaNaveesVersion' in tdoc, '"RekhtaNaveesVersion" key is absent'
        assert tdoc['RekhtaNaveesVersion'] == str(Rx.ApplicationVersion), \
            (f'"RekhtaNaveesVersion" mismatch Application v{str(Rx.ApplicationVersion)} '
             f'vs Project v{tdoc["RekhtaNaveesVersion"]}')

        assert 'general' in tdoc, '"general" table is absent'
        general: dict = tdoc['general']  # type: ignore

        assert 'authorName' in general, '"authorName" key is absent'
        self.originator = general['authorName']
        assert 'authorEmail' in general, '"authorEmail" key is absent'
        self.email = general['authorEmail']
        if 'description' in general:
            self.narrative = general['description']
        if 'createdOn' in general:
            self.createdOn = general['createdOn']
        if 'lastSavedOn' in general:
            self.lastSavedOn = general['lastSavedOn']

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
    def renderProjectToToml(self) -> tomlkit.TOMLDocument:
        """Update the existing TOML document from the project

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
        assert self.originator != '', 'Author not provided'
        general['authorName'] = self.originator
        assert self.email != '', 'Author email not provided'
        general['authorEmail'] = self.email
        if self.narrative:
            general.add('description', tomlkit.string(f'\n{self.narrative}\n', multiline=True))
        general.add('createdOn', self.createdOn).add('lastSavedOn', self.lastSavedOn)
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
    def updateProjectToToml(self, tdoc: tomlkit.TOMLDocument):
        """Update the existing TOML document from the project"""
        tdoc['RekhtaNaveesVersion'] = str(Rx.ApplicationVersion)

        general = tdoc['general'] if 'general' in tdoc else toml.table()  # type: ignore
        assert self.originator != '', 'Author not provided'
        general['authorName'] = self.originator
        assert self.email != '', 'Author email not provided'
        general['authorEmail'] = self.email
        if self.narrative:
            general['description'] = tomlkit.string(f'\n{self.narrative}\n', multiline=True)
        elif 'description' in general:
            general.pop('description')
        general['createdOn'] = self.createdOn
        general['lastSavedOn'] = self.lastSavedOn
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
