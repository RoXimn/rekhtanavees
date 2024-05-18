# -*- coding: utf-8 -*-
# ******************************************************************************
# Copyright (c) 2024. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
from pathlib import Path
from typing import Any

import librosa
import numpy as np
from PySide6.QtGui import QImage

from rekhtanavees.audio.spectra import COLOR_MAPS_8BIT


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
        self.audioSignal: np.ndarray = np.array([], dtype='float32')
        self.sampleRate: int = 48000

    # **************************************************************************
    @staticmethod
    def createAudioClip(filePath: Path) -> 'AudioClip':
        """Create an audio clip object from the given audio file.

        Uses librosa to load audio files, hence all formats supported by lbrosa can
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
    def createSpectrogram(self, startTime: int = None, endTime: int = None,
                          melBins: int = 48, hopLength: int = 512,
                          nFFT: int = 2048,
                          vtickTime: int = 1, vtickValue: int = 192) -> np.ndarray[Any, np.dtype]:
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
            vtickTime (int): Time interval to mark on the spectrogram in seconds. Use 0 to turn off
            vtickValue (int): Pixel value to use for seconds tick mark in spectrogram, from the colormap
            cmap (list[int]): 256 `AARRGGBB` pixel value colormap for the spectrogram
        """

        assert self.audioSignal.ndim == 1
        LAST = self.audioSignal.shape[0] - 1
        if LAST < 0:
            return np.array([])

        startTime = 0 if startTime is None else startTime * self.sampleRate // 1000
        endTime = LAST if endTime is None else endTime * self.sampleRate // 1000
        startTime = np.clip(startTime, a_min=0, a_max=LAST)
        endTime = np.clip(endTime, a_min=0, a_max=LAST)
        if startTime > endTime:
            startTime, endTime = endTime, startTime

        melSpectrum = librosa.feature.melspectrogram(y=self.audioSignal[startTime:endTime],
                                                     sr=self.sampleRate,
                                                     n_mels=melBins,
                                                     n_fft=nFFT,
                                                     hop_length=hopLength)
        dbMelSpectrum = librosa.amplitude_to_db(melSpectrum)
        # Normalize and scale to 0..255 values
        byteNormalizedSpectrum = (255 * (dbMelSpectrum - np.min(dbMelSpectrum)) / np.ptp(dbMelSpectrum)).astype('uint8')
        # flip vertically so low frequencies are at the bottom
        byteMap = np.flip(byteNormalizedSpectrum, axis=0)
        if vtickTime > 0:
            # Add second ticks to the spectrogram image
            imgHeight, imgWidth = byteMap.shape
            frameRate = self.sampleRate // hopLength
            vtickInterval = vtickTime * frameRate
            secondStops = np.arange(start=vtickInterval, stop=imgWidth, step=vtickInterval)
            vtickValue = vtickValue % 256
            for xt in secondStops:
                byteMap[:, xt] = vtickValue
        return byteMap

    # **************************************************************************
    def getSpectrumImage(self, startTime: int = None, endTime: int = None,
                         widthPerSec: int = 24, height: int = 48,
                         nFFT: int = 2048,
                         timeMarker: int = 1, markerColor: int = 192,
                         cmap: str = 'magma') -> QImage:
        """Create Mel Spectrogram QImage of the recorded audio signal.

        Args:
            startTime (Optional[int]): start time interval (ms). Defaults to ``None``,
                indicating beginning of the clip.
            endTime (Optional[int]): end time interval (ms). Defaults to ``None``,
                indicating end of the clip.
            widthPerSec (int): Width of spectrogram image corresponding to one second
            height (int): Height of spectrogram image
            nFFT (int): Window length of Short FFT sampling of audio signal
            timeMarker (int): Time marker placement interval, 0 to turn off.
            markerColor (int): Pixel value to use for seconds tick mark in spectrogram, from the colormap
            cmap (str): Colormap name to use for the spectrogram. Opt from ``magma``
                and ``grayscale``. Add ``_r`` to name for reverse map.
        """

        byteMap = self.createSpectrogram(startTime=startTime, endTime=endTime,
                                         melBins=height,
                                         hopLength=self.sampleRate//widthPerSec,
                                         nFFT=nFFT,
                                         vtickTime=timeMarker,
                                         vtickValue=markerColor)
        imgHeight, imgWidth = byteMap.shape
        imgSpectrum = QImage(np.ascontiguousarray(byteMap).data,
                             imgWidth, imgHeight, imgWidth,
                             QImage.Format_Indexed8)
        imgSpectrum.setColorTable(COLOR_MAPS_8BIT.get(cmap, COLOR_MAPS_8BIT['magma']))
        return imgSpectrum


# ******************************************************************************
