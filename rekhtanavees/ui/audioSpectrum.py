# -*- coding: utf-8 -*-
# ******************************************************************************
# Copyright (c) 2025. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
from enum import Enum
from pathlib import Path

from PySide6.QtCore import Qt, QSize, QPoint, QPointF, Signal, QRect
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPolygonF, QResizeEvent, QTransform
from PySide6.QtWidgets import QWidget, QScrollArea, QSizePolicy, QGroupBox, QRadioButton, QGraphicsDropShadowEffect

from audio import AudioRenderer, loadTranscript
from rekhtanavees.audio import AudioClip
from rekhtanavees.misc.utils import hmsTimestamp


# ******************************************************************************
class TimeInterval(Enum):
    Millisecond = 1.0
    Millisecond50 = 0.5
    Centisecond = 0.1
    Centisecond50 = 0.05
    Decisecond = 0.01
    Decisecond50 = 0.005
    Second = 0.001
    Second30 = 0.0005
    Minute = 0.001 / 60.0
    Minute30 = 0.0005 / 60.0
    Hour = 0.001 / 3600.0

    def next(self):
        members = list(self.__class__)
        index = members.index(self)
        lastValidIndex = len(members) - 1
        nextIndex = min(index + 1, lastValidIndex)
        return members[nextIndex]

    def prev(self):
        members = list(self.__class__)
        index = members.index(self)
        firstValidIndex = 0
        prevIndex = max(index - 1, firstValidIndex)
        return members[prevIndex]


# ******************************************************************************
_ShortSegment: int = 5
_IntermediateSegment: int = 8
_LongSegment: int = 18

_ThinSegment: int = 1
_ThickSegment: int = 3

_TextPadding: int = 1

_MarkerWidth: int = 2
_MarkerCorner: int = 5
_MarkerOpacity: float = 0.5
"""Percent opacity of the marker; 0.0 (fully transparent) to 1.0 (completely opaque)."""

_StepSmall: int = 5
_StepRegular: int = 50
_StepLarge: int = 200

_MarkerMargin: int = 100


# ******************************************************************************
class AudioSpectrumWidget(QWidget):
    markerChanged = Signal(int)

    RulerScale: dict[TimeInterval, tuple[int, int, int]] = {
        TimeInterval.Millisecond: (50, 250, 500),
        TimeInterval.Millisecond50: (50, 250, 500),
        TimeInterval.Centisecond: (10, 50, 100),
        TimeInterval.Centisecond50: (10, 50, 100),
        TimeInterval.Decisecond: (10, 50, 100),
        TimeInterval.Decisecond50: (10, 50, 100),
        TimeInterval.Second: (5, 30, 120),
        TimeInterval.Second30: (5, 30, 120),
        TimeInterval.Minute: (5, 15, 60),
        TimeInterval.Minute30: (5, 15, 60),
        TimeInterval.Hour: (6, 24, 7 * 24)
    }

    def time2pix(self, t: int):
        return int(t * self._scaleFactor.value)

    def pix2time(self, x: int):
        return int(x / self._scaleFactor.value)

    @property
    def interval(self) -> TimeInterval:
        return self._scaleFactor

    @interval.setter
    def interval(self, factor: TimeInterval):
        assert isinstance(factor, TimeInterval)
        if factor == self._scaleFactor:
            return

        oldSize = self.sizeHint()
        self._scaleFactor = factor
        self.renderer.widthPerSec = factor.value * 1000.0
        newSize = self.sizeHint()
        resizeEvent = QResizeEvent(newSize, oldSize)
        QApplication.postEvent(self, resizeEvent)
        self.update()

    def __init__(self, parent=None, direction: Qt.LayoutDirection = Qt.RightToLeft):
        super(AudioSpectrumWidget, self).__init__(parent)
        self.direction: Qt.LayoutDirection = direction
        self.start = 0
        self.end = 50
        self._scaleFactor: TimeInterval = TimeInterval.Second

        self.segments = loadTranscript(Path(r"C:\Users\driyo\Documents\Ertugrul Urdu\S1E1-ErtugrulGhaziUrdu-15min.json"))
        self.ac = AudioClip.createAudioClip(Path(r"C:\Users\driyo\Documents\Ertugrul Urdu\S1E1-ErtugrulGhaziUrdu-15min.flac"))
        self.renderer = AudioRenderer(self.ac, widthPerSec=self.interval.value * 1000.0, height=128, direction=direction, cmap='magma')

        self.totalTime: int = len(self.ac)

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

        self.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Fixed
        )

    # def focusInEvent(self, event):
    #     super().focusInEvent(event)
    #     shadow_effect = QGraphicsDropShadowEffect(self)
    #     shadow_effect.setBlurRadius(5)  # Adjust blur radius for shadow softness
    #     shadow_effect.setColor(QColor(255, 0, 0, 100))  # Set shadow color (RGBA: black with 100 alpha)
    #     shadow_effect.setOffset(2, 2)  # Set x and y offset for shadow position
    #     self.setGraphicsEffect(shadow_effect)
    #
    # def focusOutEvent(self, event):
    #     super().focusOutEvent(event)
    #     self.setGraphicsEffect(None)

    def sizeHint(self):
        return QSize(self.time2pix(self.totalTime), 128)

    def setStartMarker(self, start: int):
        if start == self.start:
            return
        prevStart = self.start

        # Ensure start and end are within the widget bounds
        self.start = max(0, min(self.width(), start))

        # Ensure start > end
        if self.start > self.end:
            self.start, self.end = self.end, self.start

        if prevStart != self.start:
            self.markerChanged.emit(self.start)

    def setEndMarker(self, end: int):
        if end == self.end:
            return
        prevEnd = self.end

        # Ensure end is within the widget bounds
        self.end = max(0, min(self.width(), end))

        # Ensure start > end
        if self.start > self.end:
            self.start, self.end = self.end, self.start

        if prevEnd != self.end:
            self.markerChanged.emit(self.end)

    def createMarker(self, dx, height, width, corner, rtl: bool) -> QPolygonF:
        # Create a marker polygon
        x1 = dx + width if rtl else dx - width
        x2 = dx
        x3 = x2 - corner if rtl else dx + corner

        y1 = 0
        y2 = corner
        y3 = height

        points = [
            QPointF(x1, y1),
            QPointF(x1, y3),
            QPointF(x2, y3),
            QPointF(x2, y2),
            QPointF(x3, y1),
        ]
        return QPolygonF(points)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = painter.device().width(), painter.device().height()
        # if self.direction == Qt.LayoutDirection.RightToLeft:
        #     transform: QTransform = QTransform()
        #     # start at right edge
        #     transform.translate(w, 0)
        #     # flip x-axis
        #     transform.scale(-1, 1)
        #     # Apply the RTL transformation to the painter
        #     painter.setWorldTransform(transform)

        viewport = self.parent()
        vx0, vw = viewport.parent().horizontalScrollBar().value(), viewport.width()
        minor, intermediate, major = self.RulerScale[self._scaleFactor]

        w0 = min(vw, w)
        x0 = vx0 - vx0 % major

        # Background fill
        # brush = QBrush(Qt.gray)
        # brush.setStyle(Qt.SolidPattern)
        # rect = QRect(x0, 0, x0 + w0 + major, h)
        # painter.fillRect(rect, brush)

        # Spectrum
        st, et = self.pix2time(x0), self.pix2time(x0 + w0 + major)
        img = self.renderer.renderSpectrum(startTime=st, endTime=et)
        # img = self.renderer.renderWords(img)
        painter.drawImage(x0, 0, img)

        # Focus indicator
        if self.hasFocus():
            # Draw focus rectangle
            dottedPen = QPen(Qt.black, 1, Qt.DotLine)
            rect = QRect(vx0, 0, vw, h)
            painter.setPen(dottedPen)
            painter.drawRect(rect)

        # Ruler
        thinTicks = QPen(Qt.white, _ThinSegment)
        thickTicks = QPen(Qt.white, _ThickSegment)
        textColor = QPen(Qt.yellow)

        font = painter.font()
        font.setFamily('Corbel')
        font.setPointSize(10)
        painter.setFont(font)

        y = 0
        for i in range(x0, x0 + w0 + major, minor):
            if i % major:
                painter.setPen(thinTicks)
                if i % intermediate:
                    painter.drawLine(i, y, i, y + _ShortSegment)
                else:
                    painter.drawLine(i, y, i, y + _IntermediateSegment)
            else:
                painter.setPen(thickTicks)
                painter.drawLine(i, y, i, y + _LongSegment)

                loc = QPoint(i + _ThickSegment + 1, y + _LongSegment + _TextPadding)
                txt = hmsTimestamp(self.pix2time(i), shorten=True)
                painter.setPen(textColor)
                painter.drawText(loc, txt)

        # Markers
        yellow = QColor(255, 255, 0, int(255 * _MarkerOpacity))
        green = QColor(0, 255, 0, int(255 * _MarkerOpacity))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(yellow))
        painter.drawPolygon(self.createMarker(self.start, h, _MarkerWidth, _MarkerCorner, False))
        painter.setBrush(QBrush(green))
        painter.drawPolygon(self.createMarker(self.end, h, _MarkerWidth, _MarkerCorner, True))

        painter.end()

    def mouseMoveEvent(self, e):
        self.setToolTip(f"{int(e.position().x())}")

    def mousePressEvent(self, e):
        if e.modifiers() & Qt.ShiftModifier:
            if e.button() == Qt.LeftButton:
                self.setStartMarker(e.position().x())
            elif e.button() == Qt.RightButton:
                self.setEndMarker(e.position().x())

        self.update()

    def keyPressEvent(self, e):
        keyCode = e.key()
        modifiers = e.modifiers()

        step = _StepRegular
        if modifiers & Qt.ShiftModifier:
            step = _StepLarge
        elif modifiers & Qt.ControlModifier:
            step = _StepSmall

        if modifiers & Qt.AltModifier:
            # Adjust end with Alt + Left/Right Arrow keys
            if keyCode == Qt.Key_Left:
                self.setEndMarker(self.end - step)
            elif keyCode == Qt.Key_Right:
                self.setEndMarker(self.end + step)
        else:
            # Adjust start with Left/Right Arrow keys
            if keyCode == Qt.Key_Left:
                self.setStartMarker(self.start - step)
            elif keyCode == Qt.Key_Right:
                self.setStartMarker(self.start + step)
            elif keyCode == Qt.Key_Minus:
                # Zoom out to bigger time interval
                self.interval = self.interval.next()
            elif keyCode == Qt.Key_Plus:
                # Zoom in to smaller time interval
                self.interval = self.interval.prev()

        self.update()


# ******************************************************************************
class AudioSpectrumScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super(AudioSpectrumScrollArea, self).__init__(parent)

        self.setWidgetResizable(True)
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.audioSpectrum = AudioSpectrumWidget(self, direction=Qt.RightToLeft)
        self.setWidget(self.audioSpectrum)

        self.audioSpectrum.markerChanged.connect(self.updateMarker)

    def updateMarker(self, x: int):
        self.ensureVisible(x, 0, _MarkerMargin)

    def setInterval(self, interval: TimeInterval):
        self.audioSpectrum.interval = interval


# ******************************************************************************
if __name__ == '__main__':

    import sys
    from PySide6.QtWidgets import QApplication, QVBoxLayout, QMainWindow

    app = QApplication(sys.argv)
    win = QMainWindow()

    win.setWindowTitle("Image Segment Viewer")

    # Create the central widget
    centralWidget = QWidget()
    win.setCentralWidget(centralWidget)

    layout = QVBoxLayout(centralWidget)

    audioWidget = AudioSpectrumScrollArea()
    layout.addWidget(audioWidget)

    groupBox = QGroupBox('Time Interval')
    radio1 = QRadioButton('Milliseconds')
    radio1.toggled.connect(lambda checked: audioWidget.setInterval(TimeInterval.Millisecond) if checked else None)
    radio15 = QRadioButton('50 Milliseconds')
    radio15.toggled.connect(lambda checked: audioWidget.setInterval(TimeInterval.Millisecond50) if checked else None)
    radio2 = QRadioButton('Centiseconds')
    radio2.toggled.connect(lambda checked: audioWidget.setInterval(TimeInterval.Centisecond) if checked else None)
    radio25 = QRadioButton('50 Centiseconds')
    radio25.toggled.connect(lambda checked: audioWidget.setInterval(TimeInterval.Centisecond50) if checked else None)
    radio3 = QRadioButton('Deciseconds')
    radio3.toggled.connect(lambda checked: audioWidget.setInterval(TimeInterval.Decisecond) if checked else None)
    radio35 = QRadioButton('50 Deciseconds')
    radio35.toggled.connect(lambda checked: audioWidget.setInterval(TimeInterval.Decisecond50) if checked else None)
    radio4 = QRadioButton('Seconds')
    radio4.toggled.connect(lambda checked: audioWidget.setInterval(TimeInterval.Second) if checked else None)
    radio45 = QRadioButton('30 Seconds')
    radio45.toggled.connect(lambda checked: audioWidget.setInterval(TimeInterval.Second30) if checked else None)
    radio5 = QRadioButton('Minutes')
    radio5.toggled.connect(lambda checked: audioWidget.setInterval(TimeInterval.Minute) if checked else None)
    radio55 = QRadioButton('30 Minutes')
    radio55.toggled.connect(lambda checked: audioWidget.setInterval(TimeInterval.Minute30) if checked else None)
    radio6 = QRadioButton('Hours')
    radio6.toggled.connect(lambda checked: audioWidget.setInterval(TimeInterval.Hour) if checked else None)

    radio4.setChecked(True)

    vbox = QVBoxLayout()
    vbox.addWidget(radio1)
    vbox.addWidget(radio15)
    vbox.addWidget(radio2)
    vbox.addWidget(radio25)
    vbox.addWidget(radio3)
    vbox.addWidget(radio35)
    vbox.addWidget(radio4)
    vbox.addWidget(radio45)
    vbox.addWidget(radio5)
    vbox.addWidget(radio55)
    vbox.addWidget(radio6)
    groupBox.setLayout(vbox)
    layout.addWidget(groupBox)

    win.resize(800, 600) # Set initial size
    win.show()

    audioWidget.setFocus()

    sys.exit(app.exec())


# ******************************************************************************
