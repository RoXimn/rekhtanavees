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
import uuid
from datetime import datetime, UTC
from pathlib import Path

import pytest
import tomlkit

from rekhtanavees.audio.audioproject import (
    AudioProject, AudioProjectException, Recording
)


# ******************************************************************************
def touchFiles(folder: Path, files: list[str]) -> None:
    """Create the specified dummy files in the given folder.

    Args:
        folder (Path): Path to the folder where the files should be created.
        files (list[str]): A list of filenames to create.
    """
    os.chdir(folder)
    for f in files:
        (folder / f).touch(exist_ok=True)


# ******************************************************************************
class TestNaveesProject:
    PROJECT_TOML = (
        '# Rekhta Navees audio project file.\n'
        '\n'
        'RekhtaNaveesVersion = "0.1"\n'
        '\n'
        '[general]\n'
        'title = "Lmnop Qrst"\n'
        'authorName = "abcdefghi"\n'
        'authorEmail = "abcdef@gmail.com"\n'
        'description = """'
        'A description of the project'
        '"""\n'
        'createdOn = 1979-05-27T00:32:00+00:00\n'
        '\n'
        '[[recordings]]\n'
        'audioFile = "recording001.flac"\n'
        'transcriptFile = "recording001.txt"\n'
        'videoFile = "recording001.mp4"\n'
        '\n'
        '[[recordings]]\n'
        'audioFile = "recording002.flac"\n'
        'transcriptFile = "recording002.txt"\n'
        '\n'
        '[[recordings]]\n'
        'audioFile = "recording003.flac"\n'
        'transcriptFile = "recording003.txt"\n'
    )

    # **************************************************************************
    def refProjectTomlDoc(self, folder: Path)-> tomlkit.TOMLDocument:
        """Create a project TOML document and its associated files in the given folder"""

        # Extract referenced data files from the TOML document and create them
        tdoc: tomlkit.TOMLDocument = tomlkit.loads(self.PROJECT_TOML)
        a = [rec['audioFile'] for rec in tdoc['recordings']]
        t = [rec['transcriptFile'] for rec in tdoc['recordings']]
        v = [rec['videoFile'] for rec in tdoc['recordings'] if 'videoFile' in rec]
        touchFiles(folder, a + t + v)

        return tdoc

    # **************************************************************************
    @staticmethod
    def projectFromTomlDoc(name: str, folder: Path,
                           tdoc: tomlkit.TOMLDocument) -> AudioProject:
        """Create an AudioProject instance from given TOML document"""

        audioProject = AudioProject(path=folder, name=name)

        audioProject.title = tdoc['general']['title']
        audioProject.authorName = tdoc['general']['authorName']
        audioProject.authorEmail = tdoc['general']['authorEmail']
        audioProject.description = tdoc['general']['description']

        audioProject.createdOn = tdoc['general']['createdOn']
        audioProject.lastSavedOn = tdoc['general'].get('lastSavedOn', None)

        # As the paths in project document are relative to project file,
        # changing to the directory ensures the pydantic can do its
        # validation correctly
        os.chdir(audioProject.folder)

        for r in tdoc['recordings']:
            audioProject.recordings.append(
                Recording(audioFile=r['audioFile'],
                          transcriptFile=r['transcriptFile'],
                          videoFile=r.get('videoFile', None))
            )

        return audioProject

    # **************************************************************************
    @pytest.fixture
    def refUnsavedProject(self, tmp_path) -> AudioProject:
        """An unsaved AudioProject instance and associated files"""

        name = str(uuid.uuid4())
        tdoc = self.refProjectTomlDoc(tmp_path)

        audioProject = self.projectFromTomlDoc(name, tmp_path, tdoc)

        return audioProject

    # **************************************************************************
    @pytest.fixture
    def refSavedProject(self, tmp_path) -> AudioProject:

        name = str(uuid.uuid4())
        tdoc = self.refProjectTomlDoc(tmp_path)

        tomlPath: Path = tmp_path / f'{name}.toml'
        tdoc['general']['lastSavedOn'] = datetime.now(UTC)
        tomlPath.write_text(tdoc.as_string(), encoding='utf8')

        audioProject = self.projectFromTomlDoc(name, tmp_path, tdoc)

        return audioProject

    # **************************************************************************
    def test_ProjectAttributes(self, tmp_path):

        name = str(uuid.uuid4())
        audioProject = AudioProject(path=tmp_path, name=name)

        assert isinstance(audioProject, AudioProject)

        assert hasattr(audioProject, 'filename')
        assert audioProject.filename == f'{name}.toml'
        assert hasattr(audioProject, 'folder')
        assert audioProject.folder == tmp_path

        assert hasattr(audioProject, 'title')
        assert audioProject.title == ''
        assert hasattr(audioProject, 'authorName')
        assert audioProject.authorName == ''
        assert hasattr(audioProject, 'authorEmail')
        assert audioProject.authorEmail == ''
        assert hasattr(audioProject, 'author')
        assert audioProject.author == ''
        assert hasattr(audioProject, 'description')
        assert audioProject.description == ''

        assert hasattr(audioProject, 'isModified')
        assert audioProject.isModified == False
        assert hasattr(audioProject, 'isSaved')
        assert audioProject.isSaved == False

        assert hasattr(audioProject, 'createdOn')
        assert hasattr(audioProject, 'lastSavedOn')
        assert hasattr(audioProject, 'recordings')
        assert audioProject.recordings == []

    # **************************************************************************
    @pytest.mark.parametrize('assigned, expected', [
        ('   ', ''),
        ('\t', ''),
        ('\n', ''),
        ('H@ll(0)', ''),
        ('       hello', 'hello'),
        ('hello       ', 'hello'),
        ('   hello    ', 'hello'),
        ('   hello world      ', 'hello world'),
        ('   hello world  out   there    ', 'hello world  out   there'),
    ])
    def test_ProjectNameSetter(self, assigned, expected, tmp_path):
        name = str(uuid.uuid4())
        audioProject = AudioProject(path=tmp_path, name=name)

        assert audioProject.name == ''

        audioProject.name = assigned
        assert audioProject.name == expected

    # **************************************************************************
    @pytest.mark.parametrize('prjName, prjFolder', [
        ('', Path(':')),
        ('a valid filename', Path(':')),
        ('a valid filename', Path('/path/to/nowhere')),
        ('Invalid:filename', str(Path(__file__).parent))
    ])
    def test_ProjectSetInvalidPath(self, prjName, prjFolder, tmp_path):
        name = str(uuid.uuid4())
        audioProject = AudioProject(path=tmp_path, name=name)

        with pytest.raises(AssertionError):
            audioProject.setFilePath(folder=prjFolder, name=prjName)

    # **************************************************************************
    def test_ProjectLoadValidContent(self, refSavedProject):
        audioProject = refSavedProject

        print(audioProject.filePath)

        audioProject.loadProject()

        assert audioProject.title == 'Lmnop Qrst'
        assert audioProject.authorName == 'abcdefghi'
        assert audioProject.authorEmail == 'abcdef@gmail.com'
        assert audioProject.description == 'A description of the project'

        assert audioProject.createdOn == datetime.fromisoformat('1979-05-27T00:32:00+00:00')
        assert audioProject.lastSavedOn is not None

        assert len(audioProject.recordings) == 3
        for i, record in enumerate(audioProject.recordings):
            assert str(record.audioFile) == f'recording{i + 1:03}.flac'
            assert str(record.transcriptFile) == f'recording{i + 1:03}.txt'
            if record.videoFile:
                assert str(record.videoFile) == f'recording{i + 1:03}.mp4'

    # **************************************************************************
    def test_ProjectSaveValidContent(self, refUnsavedProject):

        refUnsavedProject.saveProject()

        with open(refUnsavedProject.filePath, 'r') as f:
            tdocLoaded = tomlkit.load(f)

        assert tdocLoaded['general']['title'] == refUnsavedProject.title
        assert tdocLoaded['general']['authorName'] == refUnsavedProject.authorName
        assert tdocLoaded['general']['authorEmail'] == refUnsavedProject.authorEmail
        assert tdocLoaded['general']['description'].strip() == refUnsavedProject.description

        assert tdocLoaded['general']['createdOn'] == refUnsavedProject.createdOn
        assert tdocLoaded['general']['lastSavedOn'] is not None

        assert len(tdocLoaded['recordings']) == len(refUnsavedProject.recordings)
        for a, b in zip(tdocLoaded['recordings'], refUnsavedProject.recordings):
            assert a['audioFile'] == str(b.audioFile)
            assert a['transcriptFile'] == str(b.transcriptFile)
            assert a['videoFile'] == str(b.videoFile)

    # **************************************************************************
    @pytest.mark.parametrize('attribute, value', [
        ('description', 'another description to shed light on the unilluminated\n'),
        ('title', 'a new title of the old project\n'),
        ('authorName', 'roximn'),
        ('authorEmail', 'roximn@rixir.org'),
        ('createdOn', datetime.now(UTC)),
    ])
    def test_ProjectSaveModifiedContent(self, refSavedProject, attribute, value):
        setattr(refSavedProject, attribute, value)
        refSavedProject.saveProject()

        with open(refSavedProject.filePath, 'r') as f:
            tdocLoaded = tomlkit.load(f)
        assert tdocLoaded['general'][attribute] == value

    # **************************************************************************
    @pytest.mark.parametrize('R, r', [(5, 10), (10, 10), (15, 10), (10, 0), (0, 10)])
    def test_ProjectSaveModifiedRecordings(self, refUnsavedProject, R, r):
        # Prepare saved project with `r` recordings
        prj = refUnsavedProject
        prj.recordings.clear()
        a = [f'ac{n}' for n in range(r)]
        t = [f't{n}' for n in range(r)]
        touchFiles(prj.folder, a + t)
        prj.recordings = [Recording(audioFile=f'ac{n}', transcriptFile=f't{n}') for n in range(r)]
        prj.saveProject()

        # Confirm `r` recordings in toml
        with open(prj.filePath, 'r') as f:
            tdocLoaded = tomlkit.load(f)
        assert (r == 0 and 'recordings' not in tdocLoaded) ^ (r != 0 and len(tdocLoaded['recordings']) == r)

        # Modify to have `R` recordings
        a = [f'ac{n}' for n in range(R)]
        t = [f't{n}' for n in range(R)]
        touchFiles(prj.folder, a + t)
        prj.recordings = [Recording(audioFile=f'ac{n}', transcriptFile=f't{n}') for n in range(R)]
        prj.saveProject()

        # Confirm `R` recordings in toml
        with open(prj.filePath, 'r') as f:
            tdocLoaded = tomlkit.load(f)
        assert (R == 0 and 'recordings' not in tdocLoaded) ^ (R != 0 and len(tdocLoaded['recordings']) == R)

# ******************************************************************************
