# -*- coding: utf-8 -*-
# ******************************************************************************
# Copyright (c) 2024. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
from typing import Optional

import numpy as np
from PySide6.QtCore import (Qt, QRectF, QPointF, QMargins)
from PySide6.QtGui import (QImage, QPainter, QBrush, QFont, QTransform, QColor)

from rekhtanavees.audio.audioclip import AudioClip
from rekhtanavees.audio.transcript import Word
from rekhtanavees.audio.spectra import COLOR_MAPS_8BIT


# **************************************************************************
class ClipImage:
    """Image rendering of an audio signal.

    Handles rendering of an audio signal as mel-spectrogram image and the
    words segments.

    Attributes:
        audioClip (AudioClip): the audio clip this image represents
        widthPerSec (Optional[int]): Width of spectrogram image corresponding to one second
        height (Optional[int]): Height of spectrogram image
        direction (Optional[Qt.LayoutDirection]): Defaults to Qt.LayoutDirection.LeftToRight
        cmap (Optional[str]): Colormap name to use for the spectrogram. Opt from ``magma``,
            ``viridis`` and ``grayscale``. Add ``_r`` to name for reverse map.
    """
    # **************************************************************************
    def __init__(self,
                 audioClip: AudioClip,
                 widthPerSec: int = 24,
                 height: int = 48,
                 cmap: str = 'magma',
                 direction: Qt.LayoutDirection = Qt.LayoutDirection.LeftToRight):

        assert audioClip is not None
        self.audioClip: AudioClip = audioClip
        self.widthPerSec: int = widthPerSec
        self.height: int = height
        self.cmap: list[int] = COLOR_MAPS_8BIT.get(cmap, COLOR_MAPS_8BIT['magma'])
        self.direction: Qt.LayoutDirection = direction

    # **************************************************************************
    def pixel2time(self, x: int, clipStart: int = 0) -> int:
        """Get time(ms) of the given sample"""
        return clipStart + x * 1000 // self.widthPerSec

    # **************************************************************************
    def time2pixel(self, t: int, clipStart: int = 0) -> int:
        """Get the x coordinate corresponding to the given time(ms)"""
        return (t - clipStart) * self.widthPerSec // 1000

    # **************************************************************************
    def renderSpectrum(self, startTime: int = None, endTime: int = None, nFFT: int = 2048,
                       markers: dict[int, list[int]] = None) -> QImage:
        """Create Mel Spectrogram QImage of the given audio clip.

        Args:
            startTime (Optional[int]): indicating beginning of the clip (ms). Defaults to ``None``
            endTime (Optional[int]): indicating end of the clip (ms). Defaults to ``None``
            nFFT (Optional[int]): Window length of Short FFT sampling of audio signal
            markers (Optional[dict[int, list[int]]]): a `dict` with color as key,
                mapping to a list of time markers (in milliseconds).
                For example, `{192: [1000, 2000, 3000], 128: [50, 1120, 2455]}`,
                different colored markers can indicate regular time interval,
                word boundaries, confidence, probability, etc.

        Note:
            All times are global, i.e. relative to the beginning of the `audioClip`.
        """

        spectrum, start, end = self.audioClip.createSpectrogram(
            startTime=startTime, endTime=endTime,
            melBins=self.height,
            hopLength=self.audioClip.sampleRate//self.widthPerSec,
            nFFT=nFFT
        )
        duration: int = end - start
        if spectrum.ndim == 2:
            imgHeight, imgWidth = spectrum.shape
            # print(f'Spectrum {imgWidth}x{imgHeight}: {start}-{end}[{duration}ms]')

            if markers is not None:
                assert isinstance(markers, dict)
                for c, ticks in markers.items():
                    tickValue = c % 256
                    ticks: list[int] = [t for t in ticks if start <= t <= end]
                    marks = [self.time2pixel(t, start) for t in ticks]
                    for xt in marks:
                        spectrum[:, xt] = tickValue

            if self.direction == Qt.LayoutDirection.RightToLeft:
                spectrum = np.flip(spectrum, axis=1)

            image = QImage(np.ascontiguousarray(spectrum).data,
                           imgWidth, imgHeight, imgWidth,
                           QImage.Format_Indexed8)
            image.setColorTable(self.cmap)
        else:
            image = QImage()

        image = image.convertToFormat(QImage.Format_ARGB32)
        image.startTime = start
        return image

    # **************************************************************************
    def renderWords(self, image: QImage, label: str, words: list[Word]) -> QImage:
        """Write the words at respective timeframes upon the image.

        Args:
            image (QImage): image to render upon
            label (str): segment label
            words (Word): list of words to render

        Note:
            Needs the ``startTime`` attribute on the given ``image``.

        TODO:
            Add user rendering config
        """
        assert image.format() == QImage.Format_ARGB32 and hasattr(image, 'startTime')
        if image.isNull():
            return image

        p = QPainter()
        p.begin(image)
        p.setRenderHint(QPainter.Antialiasing)

        for w in words:
            lt = self.time2pixel(int(w.start * 1000), image.startTime)
            rt = self.time2pixel(int(w.end * 1000), image.startTime)
            top = 0
            btm = image.height() - 1

            wordBox = QRectF(QPointF(lt, top), QPointF(rt, btm))
            if self.direction == Qt.LayoutDirection.RightToLeft:
                transform: QTransform = QTransform()
                # start at right edge
                transform.translate(image.width(), 0)
                # flip x-axis
                transform.scale(-1, 1)
                wordBox = transform.mapRect(wordBox)

            p.setPen(Qt.darkGray)
            p.drawRect(wordBox)
            # p.drawLine(box.topLeft(), box.bottomRight())
            # p.drawLine(box.bottomLeft(), box.topRight())

            white = QColor(Qt.white)
            white.setAlpha(int(w.probability*255))
            p.setPen(white)
            p.setFont(QFont('Noto Naskh Arabic', 18))
            p.drawText(wordBox, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, w.word)

            p.setPen(Qt.black)
            p.setFont(QFont('Courier New', 12, weight=900))
            pc = f'{int(w.probability*100)}%'
            p.drawText(wordBox, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, pc)

        lt = 0
        rt = image.width() - 1
        top = 0
        btm = image.height() - 1
        imageBox = QRectF(QPointF(lt, top), QPointF(rt, btm))

        align = Qt.AlignmentFlag.AlignVCenter | (Qt.AlignmentFlag.AlignRight
                                                 if self.direction == Qt.LayoutDirection.RightToLeft
                                                 else Qt.AlignmentFlag.AlignLeft)
        p.setFont(QFont('Courier New', 18, weight=900))
        bb = p.boundingRect(imageBox, align, label).marginsAdded(QMargins(6, 1, 6, 1))
        if self.direction == Qt.LayoutDirection.RightToLeft:
            bb.moveRight(imageBox.right())
        else:
            bb.moveLeft(imageBox.left())
        p.setBrush(QBrush(QColor(Qt.yellow)))
        p.drawRoundedRect(bb, 3.0, 3.0)

        p.setPen(Qt.black)
        p.drawText(bb, Qt.AlignmentFlag.AlignCenter, label)

        p.end()

        return image


# ******************************************************************************
if __name__ == '__main__':
    import orjson as json
    from pathlib import Path
    from PySide6.QtGui import QColor, QGuiApplication
    from rekhtanavees.audio.transcript import Segment
    app = QGuiApplication()

    tms = lambda x: int(x * 1000)
    j = json.loads(Path(r"D:\tools\urdu-youtube\zia-mohyeddin\Dawood Rehber ｜ Zia Mohyeddin Ke Sath Aik Shaam Vol.24 [cHUQ1P2kb58].json").read_text(encoding='utf-8'))
    ac = AudioClip.createAudioClip(Path(r"D:\tools\urdu-youtube\zia-mohyeddin\Dawood Rehber ｜ Zia Mohyeddin Ke Sath Aik Shaam Vol.24 [cHUQ1P2kb58].opus"))
    print(ac.audioSignal.ndim, ac.audioSignal.dtype, ac.audioSignal.dtype.itemsize, ac.sampleRate)
    ci = ClipImage(ac, widthPerSec=256, height=96, direction=Qt.LayoutDirection.RightToLeft, cmap='viridis')

    for segment in [Segment.parse_obj(s) for s in j['segments'][:10]]:
        img = ci.renderSpectrum(startTime=tms(segment.start), endTime=tms(segment.end))
        img = ci.renderWords(image=img, label=f'#{segment.id}', words=segment.words)
        print(f'saving segment{segment.id:002}.png')
        img.save(f'segment{segment.id:002}.png')
