# -*- coding: utf-8 -*-
# ******************************************************************************
# Copyright (c) 2022. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
from datetime import datetime, timezone
from pathlib import Path

import pytest
import tomlkit
from tomlkit import TOMLDocument

from audio.audioproject import AudioProject, AudioProjectException, Recording


# ******************************************************************************
class TestNaveesProject:
    PROJECT_TOML = ('# Rekhta Navees audio project file.\n'
                    '\n'
                    'RekhtaNaveesVersion = "0.1"\n'
                    '\n'
                    '[general]\n'
                    'title = "Lmnop Qrst"\n'
                    'authorName = "Abcdef"\n'
                    'authorEmail = "abcdef@gmail.com"\n'
                    'description = "A description of the project"\n'
                    'createdOn = 1979-05-27T00:32:00-07:00\n'
                    '\n'
                    '[[recordings]]\n'
                    'audioClip = "recording001.flac"\n'
                    'transcription = "recording001.txt"\n'
                    '\n'
                    '[[recordings]]\n'
                    'audioClip = "recording002.flac"\n'
                    'transcription = "recording002.txt"\n'
                    '\n'
                    '[[recordings]]\n'
                    'audioClip = "recording003.flac"\n'
                    'transcription = "recording003.txt"\n')

    # **************************************************************************
    @pytest.fixture(scope="session")
    def referenceTomlFilePath(self, tmp_path_factory) -> Path:
        tomlPath: Path = tmp_path_factory.mktemp('data') / 'test.toml'
        with tomlPath.open('wb+') as toml:
            toml.write(self.PROJECT_TOML.encode('utf8'))
        return tomlPath

    # **************************************************************************
    @pytest.fixture(scope="session")
    def referenceUnsavedProject(self, tmpdir_factory) -> AudioProject:
        audioProject = AudioProject()
        audioProject.name = 'unsavedProject'
        audioProject.folder = str(tmpdir_factory.mktemp('test'))

        tdoc: TOMLDocument = tomlkit.loads(self.PROJECT_TOML)
        audioProject.author = tdoc['general']['author']  # type: ignore
        audioProject.description = tdoc['general']['description']  # type: ignore
        audioProject.createdOn = tdoc['general']['createdOn']  # type: ignore
        audioProject.lastSavedOn = tdoc['general']['lastSavedOn']  # type: ignore

        for r in tdoc['recordings']:  # type: ignore
            audioProject.recordings.append(
                Recording(audioClip=r['audioClip'], transcription=r['transcription'])  # type: ignore
            )
        return audioProject

    # **************************************************************************
    @pytest.fixture(scope="session")
    def referenceSavedProject(self, tmp_path_factory) -> AudioProject:
        tomlPath: Path = tmp_path_factory.mktemp('data') / 'reference.toml'
        with tomlPath.open('wb+') as toml:
            toml.write(self.PROJECT_TOML.encode('utf8'))

        audioProject = AudioProject()
        audioProject.name = str(tomlPath.stem)
        audioProject.folder = str(tomlPath.parent)
        audioProject.loadProject()

        return audioProject

    # **************************************************************************
    def test_ProjectAttributes(self):
        audioProject = AudioProject()
        assert hasattr(audioProject, 'title')
        assert audioProject.title == ''
        assert hasattr(audioProject, 'author')
        assert audioProject.author == ''
        assert hasattr(audioProject, 'description')
        assert audioProject.description == ''
        assert hasattr(audioProject, 'projectFolder')
        assert audioProject.projectFolder == ''
        assert hasattr(audioProject, 'createdOn')
        assert hasattr(audioProject, 'lastSavedOn')
        assert hasattr(audioProject, 'recordings')
        assert audioProject.recordings == []

    # **************************************************************************
    @pytest.mark.parametrize('assigned, expected', [
        ('   ', ''),
        ('\t', ''),
        ('\n', ''),
        (None, ''),
        ('H@ll(0)', ''),
        ('       hello', 'hello'),
        ('hello       ', 'hello'),
        ('   hello    ', 'hello'),
        ('   hello world      ', 'hello world'),
        ('   hello world  out   there    ', 'hello world  out   there'),
    ])
    def test_ProjectNameSetter(self, assigned, expected):
        audioProject = AudioProject()
        assert audioProject.name == ''

        audioProject.name = assigned
        assert audioProject.name == expected

    # **************************************************************************
    @pytest.mark.parametrize('assigned, expected', [
        ('   ', ''),
        ('/a/path/to/nowhere', ''),
        (str(Path(__file__)), ''),
        (str(Path(__file__).parent), str(Path(__file__).parent))
    ])
    def test_ProjectFolderSetter(self, assigned, expected):
        audioProject = AudioProject()
        audioProject.folder = assigned
        assert audioProject.folder == expected

    # **************************************************************************
    @pytest.mark.parametrize('prjName, prjFolder', [
        ('', ''),
        ('a valid filename', ''),
        ('a valid filename', '/path/to/somewhere'),
        ('a valid filename', str(Path(__file__).parent))
    ])
    def test_ProjectLoadInvalidPath(self, prjName, prjFolder):
        audioProject = AudioProject()
        audioProject.name = prjName
        audioProject.folder = prjFolder

        with pytest.raises(AudioProjectException):
            audioProject.loadProject()

    # **************************************************************************
    def test_ProjectLoadValidContent(self, referenceTomlFilePath):
        audioProject = AudioProject()
        audioProject.name = str(referenceTomlFilePath.stem)
        audioProject.folder = str(referenceTomlFilePath.parent)

        audioProject.loadProject()

        assert audioProject.author == 'abcdef <abcdef@gmail.com>'
        assert audioProject.description == 'A description of the project'
        assert audioProject.createdOn == datetime.fromisoformat('1979-05-27T00:32:00-07:00')
        assert audioProject.lastSavedOn == datetime.fromisoformat('1979-05-27T00:32:00+07:00')

        assert len(audioProject.recordings) == 3
        for i, record in enumerate(audioProject.recordings):
            assert record.audioClip == f'recording00{i+1}.flac'
            assert record.transcription == f'recording00{i+1}.txt'

    # **************************************************************************
    def test_ProjectSaveValidContent(self, referenceUnsavedProject):

        referenceUnsavedProject.saveProject()

        with open(referenceUnsavedProject.projectFilename(), 'r') as f:
            tdocLoaded = tomlkit.load(f)

        assert tdocLoaded['general']['author'] == referenceUnsavedProject.author
        assert tdocLoaded['general']['description'] == referenceUnsavedProject.description
        assert tdocLoaded['general']['createdOn'] == referenceUnsavedProject.createdOn
        assert tdocLoaded['general']['lastSavedOn'] == referenceUnsavedProject.lastSavedOn

        assert len(tdocLoaded['recordings']) == len(referenceUnsavedProject.recordings)
        for a, b in zip(tdocLoaded['recordings'], referenceUnsavedProject.recordings):
            assert a['audioClip'] == b.audioClip
            assert a['transcription'] == b.transcription

    # **************************************************************************
    @pytest.mark.parametrize('attribute, value', [
        ('description', 'another description to shed light on the unilluminated'),
        ('author', 'roximn <roximn@rixir.org>'),
        ('createdOn', datetime.now(timezone.utc)),
        ('lastSavedOn', datetime.now(timezone.utc)),
    ])
    def test_ProjectSaveModifiedContent(self, referenceSavedProject, attribute, value):
        setattr(referenceSavedProject, attribute, value)
        referenceSavedProject.saveProject()

        with open(referenceSavedProject.projectFilename(), 'r') as f:
            tdocLoaded = tomlkit.load(f)
        assert tdocLoaded['general'][attribute] == value

    # **************************************************************************
    @pytest.mark.parametrize('R, r', [(5, 10), (10, 10), (15, 10), (10, 0), (0, 10)])
    def test_ProjectSaveModifiedRecordings(self, referenceUnsavedProject, R, r):
        # Prepare saved project with `r` recordings
        prj = referenceUnsavedProject
        prj.recordings.clear()
        prj.recordings = [Recording(audioClip=f'ac{n}', transcription=f't{n}') for n in range(r)]
        prj.saveProject()

        # Confirm `r` recordings in toml
        with open(prj.projectFilename(), 'r') as f:
            tdocLoaded = tomlkit.load(f)
        assert (r == 0 and 'recordings' not in tdocLoaded) ^ (r != 0 and len(tdocLoaded['recordings']) == r)

        # Modify to have `R` recordings
        prj.recordings = [Recording(audioClip=f'ac{n}', transcription=f't{n}') for n in range(R)]
        prj.saveProject()

        # Confirm `R` recordings in toml
        with open(prj.projectFilename(), 'r') as f:
            tdocLoaded = tomlkit.load(f)
        assert (R == 0 and 'recordings' not in tdocLoaded) ^ (R != 0 and len(tdocLoaded['recordings']) == R)
