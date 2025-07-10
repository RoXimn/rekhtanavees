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
import os
from datetime import datetime, timezone
from enum import auto
from pathlib import Path
from typing import Optional, List, Annotated

import tomlkit
from pydantic import (
    BaseModel, Field, EmailStr, FilePath, ValidationError,
    StringConstraints
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


# ******************************************************************************
class ProjectInfo(BaseModel):
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3,
                                            max_length=255, pattern='^[A-Za-z0-9 _-]+$')]
    authorName: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3)]
    authorEmail: EmailStr
    description: Annotated[str, StringConstraints(strip_whitespace=True)] = Field(default='')
    speakers: Optional[List[Speaker]] | None = None
    createdOn: datetime = Field(default=datetime.now(Rx.Timezone), frozen=True)


# ******************************************************************************
def createProjectToml() -> tomlkit.TOMLDocument:
    """Create a de novo project document in TOML format"""
    tdoc = tomlkit.TOMLDocument()
    seperator = tomlkit.comment("*" * 78)

    # Header Section
    (tdoc
     .add(seperator)
     .add(tomlkit.comment(f"{Rx.ApplicationName} audio project"))
     .add(tomlkit.comment(f'Application version: {Rx.ApplicationVersion!s}'))
     .add(tomlkit.nl()))

    tdoc['general'] = tomlkit.table()
    tdoc['recordings'] = tomlkit.aot()

    # Footer
    tdoc.add(seperator)

    return tdoc


# ******************************************************************************
class NaveesProject(BaseModel):
    projectFile: FilePath
    info: ProjectInfo
    clips: List[Recording] = []
    isModified: bool = False

    def generateFilename(self, folder: str) -> str:
        """Generate a filename at given directory from project title"""
        return str((Path(folder) / f'{slugify(self.info.title)}.toml').resolve())

    def exists(self) -> bool:
        """Project file exists or not"""
        return self.projectFile is not None

    def save(self):
        """Write current configuration to file.

        The current configuration file is loaded and updated. The overhead of loading
        everytime for saving should be small.

        Raises:
            ValueError: If the configuration file does not exist and
                `denovo` is `False`.
        """
        log = logging.getLogger(Rx.ApplicationName)
        try:
            tdoc: tomlkit.TOMLDocument = tomlkit.loads(self.projectFile.read_text(encoding='utf-8'))
        except TOMLKitError as e:
            log.warning(f'Error decoding {self.projectFile!s}: {e!s}')
            print(f'Error decoding {self.projectFile!s}: {e!s}')
            log.debug('Resetting the toml document...')
            print('Resetting the toml document...')
            tdoc = createProjectToml()

        tdoc['general'] = tomlkit.item(self.info.model_dump(exclude_none=True))

        # Recordings list Section
        recordings = tdoc['recordings'] if 'recordings' in tdoc else tomlkit.aot()
        for _, clip in enumerate(self.clips):
            c = clip.model_dump(exclude_none=True)
            print(c)
            i = tomlkit.item(c)
            print(type(recordings))
            recordings.append(i)
        tdoc['recordings'] = recordings

        # Write toml file
        self.projectFile.write_text(tomlkit.dumps(tdoc))
        log.debug(f'Project file saved. ({self.projectFile.resolve()!s})')


def loadProject(filename: str) -> NaveesProject:
    assert isinstance(filename, str)
    filePath = Path(filename)
    if not filePath.is_file():
        raise AudioProjectException(f'Loading non-existent project file {filename}')

    try:
        tdoc: tomlkit.TOMLDocument = tomlkit.loads(filePath.read_text(encoding='utf-8'))
    except TOMLKitError as e:
        raise AudioProjectException(f'{e!s} in {filename}')

    try:
        info = ProjectInfo.model_validate(tdoc['general'])
    except ValidationError as ve:
        raise AudioProjectException(str(ve))

    clips = []
    if 'recordings' in tdoc:
        # Change working directory so that file paths can be validated
        # by pydantic, relative of it.
        os.chdir(filePath.parent)

        for i, record in enumerate(tdoc['recordings']):
            try:
                print(record)
                print(record.as_string)
                clips.append(Recording.model_validate(record))
            except ValidationError as ve:
                raise AudioProjectException(f'Error at {i}: {str(ve)}')

    return NaveesProject(projectFile=filePath, info=info, clips=clips)


# ******************************************************************************
class AudioProject:
    # **************************************************************************
    def __init__(self):
        self.title: str = ''
        self.projectFolder: str = ''
        self.originator: str = ''
        self.email: str = ''
        self.narrative: str = ''
        self.createdOn: datetime = datetime.now(timezone.utc)
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
        tdoc['general']['lastSavedOn']: datetime.now(tz=timezone.utc)  # type: ignore
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
                recording = Recording(audioFile=Path(record['audioFile']),
                                      transcriptFile=Path(record['transcriptFile']))

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
            general.add('description', self.narrative)
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
            general['description'] = self.narrative
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
                'transcriptFile': str(record.transcriptFile)
            })
        if hasMore:
            for i, record in enumerate(self.recordings[r:]):
                recordings.append(
                    tomlkit.table()
                    .add('audioFile', str(record.audioFile))
                    .add('transcriptFile', str(record.transcriptFile))
                )
        else:
            del recordings[R:]
        tdoc['recordings'] = recordings


# ******************************************************************************
if __name__ == '__main__':
    f = Path(r"C:\Users\driyo\Documents\test\abc\abc.toml")
    p = loadProject(str(f))
    print(p.model_dump())
    os.chdir(f.parent)
    for i in range(1, 4):
        r = Recording(audioFile=f'rec{i}.wav', transcriptFile=f'txt{i}.txt')
        p.clips.append(r)
    print(p.model_dump())
    p.save()

# ******************************************************************************
