# -*- coding: utf-8 -*-
# ******************************************************************************
# Copyright (c) 2022. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
from typing import Union

from PySide6.QtCore import (QSize)
from PySide6.QtGui import (QImage, QMouseEvent, QPaintEvent, QPainter, QPixmap)
from PySide6.QtWidgets import (QLabel, QToolTip, QWidget)

from rekhtanavees.audio.audioclip import AudioClip


# ******************************************************************************
class AudioLabel(QLabel):
    # **************************************************************************
    IMAGE_HEIGHT: int = 48
    IMAGE_WIDTH_RATE: int = 36
    IMAGE_CMAP: str = 'magma'
    IMAGE_MARKER_COLOR = 64
    IMAGE_MARKER_INTERVAL: int = 1

    # **************************************************************************
    def __init__(self, parent: QWidget, audio: AudioClip = None):
        super(AudioLabel, self).__init__(parent)
        self.setAutoFillBackground(True)
        self.setMouseTracking(True)

        self.audio = audio

    @property
    def audio(self) -> Union[AudioClip, None]:
        return self._audioClip

    @audio.setter
    def audio(self, audio: AudioClip):
        assert audio is None or isinstance(audio, AudioClip)
        self._audioClip = audio
        self.updateSpectrum()

    def updateSpectrum(self) -> None:
        if self._audioClip:
            self.spectrum = self._audioClip.getSpectrumImage(widthPerSec=self.IMAGE_WIDTH_RATE,
                                                             height=self.IMAGE_HEIGHT,
                                                             markerColor=self.IMAGE_MARKER_COLOR,
                                                             timeMarker=self.IMAGE_MARKER_INTERVAL,
                                                             cmap=self.IMAGE_CMAP)
        else:
            self.spectrum = QImage(0, self.IMAGE_HEIGHT, QImage.Format_ARGB32)

        self.setPixmap(QPixmap.fromImage(self.spectrum))

    def minimumSize(self) -> QSize:
        return self.spectrum.size()

    def mouseMoveEvent(self, ev: QMouseEvent) -> None:
        if 0 <= ev.x() < self.spectrum.width():
            QToolTip.showText(self.mapToGlobal(ev.position().toPoint()),
                              f'{ev.x() / self.IMAGE_WIDTH_RATE:.2f}s')

    def paintEvent(self, e: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.drawImage(0, 0, self.spectrum)
        painter.end()


# ******************************************************************************
