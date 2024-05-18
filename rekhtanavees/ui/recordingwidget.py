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
from pathlib import Path

import humanize
import numpy as np
from PySide6.QtCore import (QByteArray, QObject, QUrl, Signal, Slot)
from PySide6.QtGui import (QFont, QFontMetrics)
from PySide6.QtMultimedia import (QAudioDevice, QAudioFormat, QAudioOutput,
                                  QAudioSource, QMediaDevices, QMediaPlayer)
from PySide6.QtWidgets import (QWidget)

from rekhtanavees.ui.recordingwidget_ui import Ui_recordingWidget
from rekhtanavees.audio.audioclip import AudioClip
from rekhtanavees.audio.audioproject import Recording


# ******************************************************************************
class AudioRecorder(QObject):
    """Audio recorder class representing a microphone for audio input.

    This QObject based class takes an audio input device and forms a convenient
    wrapper around it for audio management.

    First recording should be done with `initialRun` method call, and subsquent
    calls can be made directly to audioInput methods.

    Attributes:
        audioInput (QAudioSource): the underlying audio source used.
        audioSignal (AudioClip): the recorded audio signal
        isInitialized (bool): `False` at instantiation. The first recording should
            be started with `initialRun` method call, so that internal IO setup
            can be initiated and sets isInitialized to `True`.

    Args:
        audioDevice (:obj:`QAudioDevice`): The input device to use
        parent (:obj:`QObject`, optional=None) The parent object
    """
    SAMPLE_RATE: int = 44100
    """int: Audio sampling rate"""
    CHANNEL_COUNT: int = 1
    """int: Audio recording channels count (ONLY 1 Channel is supported)"""
    SAMPLE_FORMAT: QAudioFormat.SampleFormat = QAudioFormat.Int16
    """:py:`QAudioFormat.SampleFormat`: Audio sampling data type"""
    AUDIO_FORMATS: dict[QAudioFormat.SampleFormat, str] = {
        QAudioFormat.UInt8: 'uint8',
        QAudioFormat.Int16: 'int16',
        QAudioFormat.Int32: 'int32'}
    """dict[QAudioFormat.SampleFormat, str]: QAudioFormat.SampleFormat to Numpy datatype mapping"""

    dataChanged = Signal()

    # **************************************************************************
    def __init__(self, audioDevice: QAudioDevice, parent=None) -> None:
        super(AudioRecorder, self).__init__(parent)

        audioFormat = QAudioFormat()
        audioFormat.setSampleRate(self.SAMPLE_RATE)
        audioFormat.setChannelCount(self.CHANNEL_COUNT)
        audioFormat.setSampleFormat(self.SAMPLE_FORMAT)
        self.audioInput: QAudioSource = QAudioSource(audioDevice, audioFormat)
        self.audioInput.stateChanged.connect(self.audioSourceStateChanged)  # type: ignore

        self.audioSignal: AudioClip = AudioClip(sampleRate=self.SAMPLE_RATE)
        self.isInitialized: bool = False

    # **************************************************************************
    def audioSourceStateChanged(self, state):
        print(state)

    # **************************************************************************
    @Slot()
    def initialRun(self):
        if self.isInitialized:
            return

        self.audioInput.setBufferSize(self.SAMPLE_RATE * 2)
        io = self.audioInput.start()

        # **********************************************************************
        def dataReady():
            length = self.audioInput.bytesAvailable()
            buffer: QByteArray = io.read(length)

            assert self.SAMPLE_FORMAT in self.AUDIO_FORMATS
            assert self.CHANNEL_COUNT == 1

            npDType: np.dtype = np.dtype(self.AUDIO_FORMATS[self.SAMPLE_FORMAT])
            audioBuffer = np.frombuffer(buffer, dtype=npDType, count=length // npDType.itemsize)

            self.audioSignal.appendAudio(audioBuffer, self.SAMPLE_RATE)
            self.dataChanged.emit()

        io.readyRead.connect(dataReady)
        self.isInitialized = True

    # **************************************************************************
    def resetAudio(self):
        self.audioSignal: AudioClip = AudioClip(sampleRate=self.SAMPLE_RATE)
        self.audioInput.reset()
        self.isInitialized = False


# ******************************************************************************
class RecordingItemWidget(QWidget):
    # **************************************************************************
    def __init__(self, parent: QWidget, filePath: Path, recording: Recording):
        assert isinstance(filePath, Path)
        assert filePath.exists()
        assert filePath.is_dir()
        assert recording is not None
        assert isinstance(recording, Recording)

        super(RecordingItemWidget, self).__init__(parent)
        self.ui = Ui_recordingWidget()
        self.ui.setupUi(self)
        self.filePath = filePath
        self.recording = recording

        audioClip = self.filePath / recording.audioClip
        fileSize = 0
        hasAudio = audioClip.exists()
        if hasAudio:
            fileSize = os.stat(audioClip).st_size
            self.audioClip = AudioClip()
            self.audioClip.loadAudio(str(audioClip))
            self.ui.lblSpectrum.audio = self.audioClip

        self.ui.btnPlay.setEnabled(hasAudio)
        self.ui.btnRecord.setEnabled(True)
        self.ui.btnSave.setEnabled(hasAudio)
        self.ui.textEdit.setEnabled(hasAudio)

        self.ui.groupBox.setTitle(f'{recording.audioClip} ({humanize.naturalsize(fileSize)})')
        fnt = QFont(['Noto Naskh Arabic', 'Noto Sans'], 14)
        self.ui.textEdit.setFont(fnt)
        fm = QFontMetrics(fnt)
        self.ui.textEdit.setMaximumHeight(fm.height() * 2)
        txtFile = self.filePath / recording.transcription
        if txtFile.exists():
            self.ui.textEdit.setPlainText(txtFile.read_text('utf-8'))

        self.ui.btnPlay.clicked.connect(self.playAudio)
        self.player = QMediaPlayer()
        audioDevice = QMediaDevices.defaultAudioOutput()
        self.audioOutput = QAudioOutput()
        self.audioOutput.setDevice(audioDevice)
        self.player.setAudioOutput(self.audioOutput)

        self.player.mediaStatusChanged.connect(self.mediaPlaybackChanged)

    # **************************************************************************
    def playAudio(self):
        self.audioOutput.setVolume(100)
        self.player.setSource(QUrl.fromLocalFile(self.filePath / self.recording.audioClip))
        self.player.play()

    # **************************************************************************
    def mediaPlaybackChanged(self, status):
        print(status)

# ******************************************************************************
