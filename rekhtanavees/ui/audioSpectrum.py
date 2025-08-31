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

from PySide6.QtCore import (Qt, QSize, QPoint, QPointF, Signal, QRectF)
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QPolygonF, QResizeEvent, QTransform, QFont
)
from PySide6.QtWidgets import (
    QWidget, QScrollArea, QSizePolicy, QScrollBar, QSpacerItem,
    QScroller, QScrollerProperties
)

from audio import AudioRenderer, Segment, findSegment, loadTranscript
from rekhtanavees.audio import AudioClip
from rekhtanavees.misc.utils import hmsTimestamp


# ******************************************************************************
class TimeInterval(Enum):
    Millisecond     = 1.000
    Millisecond75   = 0.750
    Millisecond50   = 0.500
    Millisecond25   = 0.250
    Centisecond     = 0.100
    Centisecond75   = 0.075
    Centisecond50   = 0.050
    Centisecond25   = 0.025
    Decisecond      = 0.010
    Decisecond50    = 0.005
    Second          = 0.001
    Second30        = 0.0005
    Minute          = 0.001  / 60.0
    Minute30        = 0.0005 / 60.0
    Hour            = 0.001  / 3600.0

    def first(self):
        members = list(self.__class__)
        return members[0]

    def last(self):
        members = list(self.__class__)
        return members[-1]

    def isFirst(self):
        members = list(self.__class__)
        index = members.index(self)
        return index == 0

    def isLast(self):
        members = list(self.__class__)
        index = members.index(self)
        return index == len(members) - 1

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

_MarkerTextPadding: int = 1

_MarkerWidth: int = 2
_MarkerCorner: int = 5
_MarkerOpacity: float = 0.5
"""Percent opacity of the marker; 0.0 (fully transparent) to 1.0 (completely opaque)."""

_StepSmall: int = 5
_StepRegular: int = 50
_StepLarge: int = 200

_MarkerMargin: int = 100
_FocusColor: QColor = QColor(255, 255, 0)

_SwapRTLMarkers: bool = True

_Height: int = 128
_SpectrumCMap: str = "viridis"

_TextSize: int = 18
_MinTextWidth: int = 36
_ElideString: str = "*"
_ElideColor: QColor = QColor(255, 0, 0, 224)
_TextColor: QColor = QColor(0, 0, 0, 128)
_SelectedTextColor: QColor = QColor(0, 0, 0, 255)
_TextFont: QFont = QFont('Noto Naskh Arabic', _TextSize)

_TextBoxBrush: QBrush = QBrush(QColor(255, 255, 0, 128), Qt.Dense7Pattern)
_TextBoxBorder: QColor = QColor(255, 255, 255, 128)

_SelectedBoxBrush: QBrush = QBrush(QColor(255, 255, 0, 64), Qt.Dense1Pattern)
_SelectedBoxBorder : QColor = QColor(255, 0, 0, 224)

# ******************************************************************************
class AudioSpectrumWidget(QWidget):
    markerChanged = Signal(int, int)

    RulerScale: dict[TimeInterval, tuple[int, int, int]] = {
        # minor, intermediate, major
        # * major and intermediate values should be multiple of minor
        TimeInterval.Millisecond: (50, 250, 500),
        TimeInterval.Millisecond75: (75, 188, 375),
        TimeInterval.Millisecond50: (25, 125, 250),
        TimeInterval.Millisecond25: (25, 125, 250),
        TimeInterval.Centisecond: (10, 50, 100),
        TimeInterval.Centisecond75: (25, 75, 150),
        TimeInterval.Centisecond50: (10, 50, 100),
        TimeInterval.Centisecond25: (10, 50, 100),
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

        self._scaleFactor: TimeInterval = TimeInterval.Millisecond25

        self.segments = loadTranscript(Path(r"C:\Users\driyo\Documents\Ertugrul Urdu\S1E1-ErtugrulGhaziUrdu-15min.json"))
        self.ac = AudioClip.createAudioClip(Path(r"C:\Users\driyo\Documents\Ertugrul Urdu\S1E1-ErtugrulGhaziUrdu-15min.flac"))

        # self.segments = None
        # self.ac = AudioClip.createAudioClip(Path(r"F:\sounds\piano-chords.flac"))

        self.currentSegment = -1

        self.renderer = AudioRenderer(self.ac, widthPerSec=self.interval.value * 1000.0, height=_Height, direction=Qt.LeftToRight, cmap=_SpectrumCMap)

        self.totalTime: int = len(self.ac)
        """Length of audio clip in milliseconds"""

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

    def sizeHint(self) -> QSize:
        return QSize(self.time2pix(self.totalTime), _Height)

    def setStartMarker(self, start: int):
        """Set the start marker position in milliseconds."""
        if start == self.start:
            return
        prevStart = self.start

        # Ensure start and end are within the widget bounds
        self.start = max(0, min(self.totalTime, start))

        # Ensure start > end
        if self.start > self.end:
            self.start, self.end = self.end, self.start

        if prevStart != self.start:
            self.markerChanged.emit(self.start, self.RulerScale[self._scaleFactor][2])
            self.update()

    def setEndMarker(self, end: int):
        """Set the end marker position in milliseconds."""
        if end == self.end:
            return
        prevEnd = self.end

        # Ensure end is within the widget bounds
        self.end = max(0, min(self.totalTime, end))

        # Ensure start > end
        if self.start > self.end:
            self.start, self.end = self.end, self.start

        if prevEnd != self.end:
            self.markerChanged.emit(self.end, self.RulerScale[self._scaleFactor][2])
            self.update()

    @property
    def currentSegment(self) -> int:
        return self.currentSegmentIndex

    @currentSegment.setter
    def currentSegment(self, index: int):
        if self.segments and 0 <= index < len(self.segments):
            self.currentSegmentIndex = index
            s: Segment = self.segments[index]
            self.start = int(s.start * 1000.0)
            self.end = int(s.end * 1000.0)
        else:
            self.currentSegmentIndex = -1
            self.start = 0
            self.end = 0

    @staticmethod
    def _createMarkerPolygon(dx, height, width, corner, rtl: bool) -> QPolygonF:
        """Create marker geometry as polygon for rendering"""
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
        if self.direction == Qt.LayoutDirection.RightToLeft:
            transform: QTransform = QTransform()
            # start at right edge
            transform.translate(w, 0)
            # flip x-axis
            transform.scale(-1, 1)
            # Apply the RTL transformation to the painter
            painter.setWorldTransform(transform)

        viewport = self.parent()
        vx0, vw = viewport.parent().horizontalScrollBar().value(), viewport.width()
        minor, intermediate, major = self.RulerScale[self._scaleFactor]

        w0 = min(vw, w)
        x0 = vx0 - (vx0 % major)
        viewBox = QRectF(x0, 0, w0, _Height)  # x, y, width, height

        # Background fill
        # brush = QBrush(Qt.gray)
        # brush.setStyle(Qt.SolidPattern)
        # rect = QRect(x0, 0, x0 + w0 + major, h)
        # painter.fillRect(rect, brush)

        # Spectrum
        st, et = self.pix2time(x0), self.pix2time(x0 + w0 + major)
        img = self.renderer.renderSpectrum(startTime=st, endTime=et)
        painter.drawImage(x0, 0, img)

        # Text segments
        if self.segments:
            for i, segment in enumerate(self.segments):
                # print(segment)
                lt = self.time2pix(int(segment.start * 1000))
                rt = self.time2pix(int(segment.end * 1000))

                top = 0
                btm = img.height() - 1

                segmentBox = QRectF(QPointF(lt, top), QPointF(rt, btm))
                if not viewBox.intersects(segmentBox):
                    continue

                painter.fillRect(segmentBox, _TextBoxBrush if self.currentSegmentIndex != i else _SelectedBoxBrush)
                painter.setPen(_TextBoxBorder if self.currentSegmentIndex != i else _SelectedBoxBorder)
                # painter.drawRect(segmentBox)
                painter.drawLine(segmentBox.topRight(), segmentBox.bottomRight())
                painter.drawLine(segmentBox.topLeft(), segmentBox.bottomLeft())

                # if the segment box is too small, replace with an elide string/character
                if segmentBox.width() >= _MinTextWidth:
                    painter.setPen(_SelectedTextColor if self.currentSegmentIndex == i else _TextColor)
                    painter.setFont(_TextFont)
                    if self.direction == Qt.LeftToRight:
                        painter.drawText(segmentBox, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, segment.text)
                    else:
                        tfm = painter.worldTransform()
                        painter.save()
                        painter.resetTransform()
                        segmentBox = tfm.mapRect(segmentBox)
                        painter.drawText(segmentBox, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, segment.text)
                        painter.restore()
                else:
                    painter.setPen(_ElideColor)
                    painter.setFont(_TextFont)
                    painter.drawText(segmentBox, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, _ElideString)

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

                loc: QPoint = QPoint(i, y + _LongSegment + _MarkerTextPadding)
                txt = hmsTimestamp(self.pix2time(i), shorten=True)
                painter.setPen(textColor)

                if self.direction == Qt.LeftToRight:
                    loc += QPoint(_ThickSegment + 1, 0)
                    painter.drawText(loc, txt)
                else:
                    loc -= QPoint(_ThickSegment + 1, 0)

                    tfm = painter.worldTransform()
                    painter.save()
                    painter.resetTransform()
                    painter.drawText(tfm.map(loc), txt)
                    painter.restore()

        # Markers
        yellow = QColor(255, 255, 0, int(255 * _MarkerOpacity))
        green = QColor(0, 255, 0, int(255 * _MarkerOpacity))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(yellow))
        painter.drawPolygon(self._createMarkerPolygon(self.time2pix(self.start), h, _MarkerWidth, _MarkerCorner, False))
        painter.setBrush(QBrush(green))
        painter.drawPolygon(self._createMarkerPolygon(self.time2pix(self.end), h, _MarkerWidth, _MarkerCorner, True))

        # Focus indicator
        # if self.hasFocus():
        #     # Draw focus rectangle
        #     dottedPen = QPen(_FocusColor, 1, Qt.DotLine)
        #     rect = QRect(vx0, 0, vw, h)
        #     painter.setPen(dottedPen)
        #     painter.setBrush(Qt.NoBrush)
        #     painter.drawRect(rect)

        painter.end()

    def mouseMoveEvent(self, e):
        wx = e.position().x()
        if self.direction == Qt.RightToLeft:
            wx = self.width() - wx
        t = self.pix2time(int(wx))
        self.setToolTip(f"{hmsTimestamp(t)} ({t/1000.0:,.03f}s)")

    def mousePressEvent(self, e):
        if e.modifiers() == Qt.NoModifier:
            if e.button() == Qt.LeftButton:
                wx = e.position().x()
                if self.direction == Qt.RightToLeft:
                    # Convert from screen space to widget space
                    wx = self.width() - wx
                twx = self.pix2time(wx)
                idx = findSegment(self.segments, twx/1000.0)
                self.currentSegment = idx
                e.accept()
                self.update()
                return

        elif e.modifiers() & Qt.ShiftModifier:
            # Shift + Left Click
            if e.button() == Qt.LeftButton:
                fSetMarker = self.setStartMarker
                wx = e.position().x()
                if self.direction == Qt.RightToLeft:
                    # Convert from screen space to widget space
                    wx = self.width() - wx
                    # Swap Markers for RTL Layout
                    if _SwapRTLMarkers:
                        fSetMarker = self.setEndMarker
                fSetMarker(self.pix2time(wx))
                e.accept()
                self.update()
                return

            # Shift + Right Click
            elif e.button() == Qt.RightButton:
                fSetMarker = self.setEndMarker
                wx = e.position().x()
                if self.direction == Qt.RightToLeft:
                    # Convert from screen space to widget space
                    wx = self.width() - wx
                    # Swap Markers for RTL Layout
                    if _SwapRTLMarkers:
                        fSetMarker = self.setStartMarker
                fSetMarker(self.pix2time(wx))
                e.accept()
                self.update()
                return

        super().mousePressEvent(e)

    def keyPressEvent(self, e):
        keyCode = e.key()
        modifiers = e.modifiers()

        step = _StepRegular
        if modifiers & Qt.ShiftModifier:
            step = _StepLarge
        elif modifiers & Qt.ControlModifier:
            step = _StepSmall

        if self.direction == Qt.RightToLeft:
            step *= -1

        if modifiers & Qt.AltModifier:
            # Adjust end with Alt + Left/Right Arrow keys
            if keyCode == Qt.Key_Left:
                self.setEndMarker(self.end - step)
                e.accept()
                return
            elif keyCode == Qt.Key_Right:
                self.setEndMarker(self.end + step)
                e.accept()
                return
        else:
            # Adjust start with Left/Right Arrow keys
            if keyCode == Qt.Key_Left:
                self.setStartMarker(self.start - step)
                e.accept()
                return
            elif keyCode == Qt.Key_Right:
                self.setStartMarker(self.start + step)
                e.accept()
                return

            # Adjust Zoom with Plus/Minus keys
            elif keyCode == Qt.Key_Minus:
                # Zoom out to bigger time interval
                self.interval = self.interval.next()
                e.accept()
                return
            elif keyCode == Qt.Key_Plus:
                # Zoom in to smaller time interval
                self.interval = self.interval.prev()
                e.accept()
                return

        super().keyPressEvent(e)


# ******************************************************************************
class AudioSpectrumScrollArea(QScrollArea):
    def __init__(self, parent=None, direction: Qt.LayoutDirection = Qt.LeftToRight):
        super(AudioSpectrumScrollArea, self).__init__(parent)

        self.setWidgetResizable(True)
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setLayoutDirection(direction)

        self.audioSpectrum = AudioSpectrumWidget(self, direction=direction)
        self.setWidget(self.audioSpectrum)

        self.audioSpectrum.markerChanged.connect(self.updateMarker)

        # Doesn't recognise RTL layout!!!
        QScroller.grabGesture(self.viewport(), QScroller.ScrollerGestureType.LeftMouseButtonGesture)
        props =  QScroller.scroller(self.viewport()).scrollerProperties()
        props.setScrollMetric(QScrollerProperties.ScrollMetric.DragStartDistance, 0.01) # Example: adjust drag start distance
        QScroller.scroller(self.viewport()).setScrollerProperties(props)

    def updateMarker(self, x: int, margin: int):
        px = self.audioSpectrum.time2pix(x)
        self.showTime(x, margin, -1)

    def showTime(self, t: int, margin: int = 100, dx: int = -1):
        """Ensure visibility of the given time (in milliseconds)"""
        hbar: QScrollBar = self.horizontalScrollBar()
        pageStep: int = hbar.pageStep()

        v = hbar.value()
        px = self.audioSpectrum.time2pix(t)
        tdx = self.audioSpectrum.pix2time(dx)
        t0 = t - tdx
        t0px = self.audioSpectrum.time2pix(t0)

        if dx >= 0:
            v = t0px
        else:
            if px < v:
                v = px - margin
            elif px >= v + pageStep:
                v = (px + margin) - pageStep

        hbar.setValue(v)
        self.verticalScrollBar().setValue(0)

    def setInterval(self, interval: TimeInterval):
        self.audioSpectrum.interval = interval

    def wheelEvent(self, event):
        # Get the vertical scroll delta
        delta_y = event.angleDelta().y()
        pos = event.position()
        sx = self.audioSpectrum.mapFromParent(pos).x()
        # Convert from screen space to widget space
        if self.layoutDirection() == Qt.RightToLeft:
            wx = self.audioSpectrum.width() - sx
        else:
            wx = sx
        t = self.audioSpectrum.pix2time(int(wx))
        hbar: QScrollBar = self.horizontalScrollBar()
        v = hbar.value()
        dx: int = wx - v
        tdx: int = self.audioSpectrum.pix2time(dx)

        if delta_y > 0:  # Scroll up
            # Zoom in to smaller time interval
            if not self.audioSpectrum.interval.isFirst():
                oldSize = self.audioSpectrum.size()
                self.audioSpectrum.interval = self.audioSpectrum.interval.prev()
                while self.audioSpectrum.size() == oldSize or hbar.maximum() + hbar.pageStep() == oldSize.width():
                    QApplication.instance().processEvents()
                self.showTime(t, -1, dx)
        elif delta_y < 0:  # Scroll down
            # Zoom out to bigger time interval
            if not self.audioSpectrum.interval.isLast():
                oldSize = self.audioSpectrum.size()
                self.audioSpectrum.interval = self.audioSpectrum.interval.next()
                while self.audioSpectrum.size() == oldSize or hbar.maximum() + hbar.pageStep() == oldSize.width():
                    QApplication.instance().processEvents()
                self.showTime(t, -1, dx)

        # Call the base class implementation to ensure proper event handling
        super().wheelEvent(event)

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

    audioWidgetLTR = AudioSpectrumScrollArea(direction=Qt.LeftToRight)
    layout.addWidget(audioWidgetLTR)

    audioWidgetRTL = AudioSpectrumScrollArea(direction=Qt.RightToLeft)
    layout.addWidget(audioWidgetRTL)

    layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Fixed, QSizePolicy.Expanding))

    # def setAudioInterval(interval: TimeInterval):
    #     audioWidgetLTR.setInterval(interval)
    #     audioWidgetRTL.setInterval(interval)
    #
    #
    # groupBox = QGroupBox('Time Interval')
    # radio1 = QRadioButton('Milliseconds')
    # radio1.toggled.connect(lambda checked: setAudioInterval(TimeInterval.Millisecond) if checked else None)
    # radio15 = QRadioButton('50 Milliseconds')
    # radio15.toggled.connect(lambda checked: setAudioInterval(TimeInterval.Millisecond50) if checked else None)
    # radio2 = QRadioButton('Centiseconds')
    # radio2.toggled.connect(lambda checked: setAudioInterval(TimeInterval.Centisecond) if checked else None)
    # radio25 = QRadioButton('50 Centiseconds')
    # radio25.toggled.connect(lambda checked: setAudioInterval(TimeInterval.Centisecond50) if checked else None)
    # radio3 = QRadioButton('Deciseconds')
    # radio3.toggled.connect(lambda checked: setAudioInterval(TimeInterval.Decisecond) if checked else None)
    # radio35 = QRadioButton('50 Deciseconds')
    # radio35.toggled.connect(lambda checked: setAudioInterval(TimeInterval.Decisecond50) if checked else None)
    # radio4 = QRadioButton('Seconds')
    # radio4.toggled.connect(lambda checked: setAudioInterval(TimeInterval.Second) if checked else None)
    # radio45 = QRadioButton('30 Seconds')
    # radio45.toggled.connect(lambda checked: setAudioInterval(TimeInterval.Second30) if checked else None)
    # radio5 = QRadioButton('Minutes')
    # radio5.toggled.connect(lambda checked: setAudioInterval(TimeInterval.Minute) if checked else None)
    # radio55 = QRadioButton('30 Minutes')
    # radio55.toggled.connect(lambda checked: setAudioInterval(TimeInterval.Minute30) if checked else None)
    # radio6 = QRadioButton('Hours')
    # radio6.toggled.connect(lambda checked: setAudioInterval(TimeInterval.Hour) if checked else None)
    #
    # radio2.setChecked(True)
    #
    # vbox = QVBoxLayout()
    # vbox.addWidget(radio1)
    # vbox.addWidget(radio15)
    # vbox.addWidget(radio2)
    # vbox.addWidget(radio25)
    # vbox.addWidget(radio3)
    # vbox.addWidget(radio35)
    # vbox.addWidget(radio4)
    # vbox.addWidget(radio45)
    # vbox.addWidget(radio5)
    # vbox.addWidget(radio55)
    # vbox.addWidget(radio6)
    # groupBox.setLayout(vbox)
    # layout.addWidget(groupBox)

    win.resize(800, 600) # Set initial size
    win.show()

    audioWidgetLTR.setFocus()

    sys.exit(app.exec())


# ******************************************************************************
