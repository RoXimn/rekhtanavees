# -*- coding: utf-8 -*-
# ******************************************************************************
# Copyright (c) 2024. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
import io
from pathlib import Path

import librosa
import numpy as np
from PySide6.QtCore import QBuffer, QIODevice
from numpy.typing import NDArray
from scipy.io import wavfile


# ******************************************************************************
class AudioClip(object):
    """Audio class representing an audio signal.

    An audio signal wrapper class for convenient audio signal processing and
    management.

    Attributes:
        audioSignal (numpy.ndarray): Numpy array representing the audio signal data
        sampleRate (int): Number of samples recorded per second
    """

    # **************************************************************************
    def __init__(self):
        self.audioSignal: NDArray = None
        self.sampleRate: int = 0

    # **************************************************************************
    def __len__(self) -> int:
        """Length of audio clip in milliseconds"""
        return self.audioSignal.shape[0] // (self.sampleRate * 1000)

    # **************************************************************************
    def sample2time(self, sample: int) -> int:
        """Get time(ms) of the given sample"""
        return sample * 1000 // self.sampleRate

    # **************************************************************************
    def time2sample(self, time: int) -> int:
        """Get the audio sample corresponding to the given time(milliseconds)"""
        return time * self.sampleRate // 1000

    # **************************************************************************
    @staticmethod
    def createAudioClip(filePath: Path) -> 'AudioClip':
        """Create an audio clip object from the given audio file.

        Uses librosa to load audio files, hence all formats supported by librosa can
        be used.

        Args:
            filePath (Path): filename of the audio file to load. Should be a valid and existing filepath.
        """
        assert filePath is not None and isinstance(filePath, Path)
        assert filePath.is_file()

        ac = AudioClip()
        ac.audioSignal, ac.sampleRate = librosa.load(filePath, sr=None, mono=True)
        return ac

    # **************************************************************************
    def getSlice(self, startTime: int = None, endTime: int = None) -> NDArray:
        assert self.audioSignal is not None and isinstance(self.audioSignal, np.ndarray)
        assert self.audioSignal.ndim == 1, f"Single channel audio required; [{self.audioSignal.ndim}] channel given"
        LAST = self.audioSignal.shape[0]
        if LAST < 0:
            return np.array([])

        firstSample = 0 if startTime is None else self.time2sample(startTime)
        lastSample = LAST if endTime is None else self.time2sample(endTime)
        firstSample = max(min(firstSample, LAST), 0)    # Clip to [0-LAST]
        lastSample = max(min(lastSample, LAST), 0)        # Clip to [0-LAST]
        if firstSample > lastSample:                     # Ensure lastSample > firstSample
            firstSample, lastSample = lastSample, firstSample
        elif firstSample == lastSample:
            return np.array([])

        return self.audioSignal[firstSample:lastSample]

    # **************************************************************************
    def getIoBuffer(self, startTime: int = None, endTime: int = None) -> QBuffer:
        wavData = io.BytesIO()
        wavfile.write(wavData, self.sampleRate, self.getSlice(startTime, endTime))

        # copy the bytes to a QBuffer
        ioBuffer = QBuffer()
        ioBuffer.setData(wavData.getvalue())
        ioBuffer.open(QIODevice.ReadOnly)
        return ioBuffer

    # **************************************************************************
    def createSpectrogram(self, startTime: int = None, endTime: int = None,
                          melBins: int = 48, hopLength: int = 512,
                          nFFT: int = 2048) -> tuple[NDArray[np.uint8], int, int]:
        """Create a Mel Spectrogram of the mono audio signal in the given time interval

        Note:
            The essential parameter to understanding the output dimensions of
            spectrogram is the distance between consecutive FFTs, the hopLength.

            When computing an STFT, FFT is computed for a number of short
            segments. These segments have the length nFFT. Usually these
            segments overlap (in order to avoid information loss), so the distance
            between two segments is often not nFFT, but something like nFFT/2.
            The name for this distance is hopLength.

            So when you have 1000 audio samples, and the hopLength is 100,
            you get 10 features frames (note that, if nFFT is greater than
            hopLength, it may need to padded).

            For example, the default hopLength of 512. So for audio sampled at
            22050 Hz, the feature frame rate is

            frameRate = sampleRate / hopLength = 22050 Hz / 512 = 43 Hz

            So for 10s of audio at 22050 Hz, the spectrogram array has
            dimensions (128, 430), where 128 is the number of Mel bins and
            430 is the number of features (43 frame in one second x 10 seconds).

        Args:
            startTime (Optional[int]): start time interval (ms). Defaults to ``None``,
                indicating beginning of the clip.
            endTime (Optional[int]): end time interval (ms). Defaults to ``None``,
                indicating end of the clip.
            hopLength (int): Interval between windows of Short FFT sampling
            nFFT (int): The window length of the SFFT sampling
            melBins (int): Number of bins in Mel Spectrogram (height of the spectrogram image)

        Returns:
            (tuple[NDArray[np.uint8], int, int]): A 2D map of the db normalized
                mel spectrogram, and its starting and ending time in milliseconds.
        """
        assert self.audioSignal is not None and isinstance(self.audioSignal, np.ndarray)
        assert self.audioSignal.ndim == 1, f"Single channel audio required; [{self.audioSignal.ndim}] channel given"
        LAST = self.audioSignal.shape[0]
        if LAST < 0:
            return np.array([]), 0, 0

        firstSample = 0 if startTime is None else self.time2sample(startTime)
        lastSample = LAST if endTime is None else self.time2sample(endTime)
        firstSample = max(min(firstSample, LAST), 0)    # Clip to [0-LAST]
        lastSample = max(min(lastSample, LAST), 0)        # Clip to [0-LAST]
        if firstSample > lastSample:                     # Ensure lastSample > firstSample
            firstSample, lastSample = lastSample, firstSample
        elif firstSample == lastSample:
            return np.array([]), firstSample, lastSample

        melSpectrum: NDArray = librosa.feature.melspectrogram(
            y=self.audioSignal[firstSample:lastSample],
            sr=self.sampleRate,
            n_mels=melBins,
            n_fft=nFFT,
            hop_length=hopLength
        )

        dbMelSpectrum: NDArray = librosa.power_to_db(melSpectrum, ref=np.max)
        # Normalize and scale to 0..255 values
        byteNormalizedSpectrum: NDArray[np.uint8] = (255 * (dbMelSpectrum - np.min(dbMelSpectrum))
                                                     / np.ptp(dbMelSpectrum)).astype('uint8')
        # flip vertically so low frequencies are at the bottom
        byteMap: NDArray[np.uint8] = np.flip(byteNormalizedSpectrum, axis=0)

        return byteMap, self.sample2time(firstSample), self.sample2time(lastSample)

# ******************************************************************************
