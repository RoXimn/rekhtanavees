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

from PySide6.QtCore import QPointF, Qt, Signal, Slot
from PySide6.QtGui import (QColorSpace, QImage, QKeySequence,
                           QMouseEvent, QPalette, QPixmap, QShortcut,
                           QWheelEvent)
from PySide6.QtWidgets import (QAbstractSlider, QApplication, QLabel,
                               QScrollArea, QSizePolicy)


# ******************************************************************************
class ImageViewer(QScrollArea):
    SCALE_FACTOR: float = 0.25
    zoomEvent = Signal(int)

    # **************************************************************************
    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        self.dragStartPosition: Union[QPointF, None] = None
        self.startHorizValue: int = 0
        self.startVertValue: int = 0

        self.imageLabel: QLabel = QLabel(self)
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.image: QImage = QImage()
        self.scaleFactor: float = 1.0

        self.setBackgroundRole(QPalette.Dark)
        self.setWidget(self.imageLabel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.zoomEvent.connect(self.onImageZoom)

        self.keyF2 = QShortcut(self)
        self.keyF2.setKey(QKeySequence(Qt.Key_F2))
        self.keyF2.activated.connect(self.onKeyF2Down)

        self.keyF3 = QShortcut(self)
        self.keyF3.setKey(QKeySequence(Qt.Key_F3))
        self.keyF3.activated.connect(self.onKeyF3Down)

        self.keyF4 = QShortcut(self)
        self.keyF4.setKey(QKeySequence(Qt.Key_F4))
        self.keyF4.activated.connect(self.onKeyF4Down)

    # **************************************************************************
    def setImage(self, newImage):
        self.image = newImage
        if self.image.colorSpace().isValid():
            self.image.convertToColorSpace(QColorSpace.SRgb)
        self.imageLabel.setPixmap(QPixmap.fromImage(self.image))
        self.scaleFactor = 1.0
        self.imageLabel.adjustSize()
        self.updateToolTip()

    # **************************************************************************
    def wheelEvent(self, e: QWheelEvent) -> None:
        steps: int = (e.angleDelta() / 8 / 15).y()  # type: ignore
        mod = e.modifiers()
        if mod == Qt.ControlModifier:
            self.zoomEvent.emit(steps)
            e.accept()
            return
        elif mod == Qt.ShiftModifier:
            hbar = self.horizontalScrollBar()
            hbarAction = QAbstractSlider.SliderSingleStepSub if steps > 0 else QAbstractSlider.SliderSingleStepAdd
            for x in range(abs(steps)):
                hbar.triggerAction(hbarAction)
        else:
            super(ImageViewer, self).wheelEvent(e)

    # **************************************************************************
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragStartPosition = event.position()
            self.startHorizValue = self.horizontalScrollBar().value()
            self.startVertValue = self.verticalScrollBar().value()

    # **************************************************************************
    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() != Qt.LeftButton:
            return
        if (event.position() - self.dragStartPosition).manhattanLength() >= QApplication.startDragDistance():  # type: ignore
            delta = event.position() - self.dragStartPosition  # type: ignore
            self.horizontalScrollBar().setValue(int(self.startHorizValue - delta.x()))
            self.verticalScrollBar().setValue(int(self.startVertValue - delta.y()))

    # **************************************************************************
    def scaleImage(self, factor: float):
        self.scaleFactor *= factor
        newSize = self.scaleFactor * self.imageLabel.pixmap().size()  # type: ignore
        self.imageLabel.resize(newSize)  # type: ignore

        self.adjustScrollbars(self.horizontalScrollBar(), factor)
        self.adjustScrollbars(self.verticalScrollBar(), factor)
        self.updateToolTip()

    # **************************************************************************
    def adjustScrollbars(self, scrollBar, factor):
        pos = int(factor * scrollBar.value() + ((factor - 1) * scrollBar.pageStep() / 2))
        scrollBar.setValue(pos)

    # **************************************************************************
    def onKeyF2Down(self):
        self.resetImageSize()

    # **************************************************************************
    def onKeyF3Down(self):
        self.fitWidthToWindow()

    # **************************************************************************
    def onKeyF4Down(self):
        self.fitHeightToWindow()

    # **************************************************************************
    @Slot()
    def fitWidthToWindow(self):
        self.scaleImage(self.viewport().width() / self.imageLabel.width())

    # **************************************************************************
    @Slot()
    def fitHeightToWindow(self):
        self.scaleImage(self.viewport().height() / self.imageLabel.height())

    # **************************************************************************
    @Slot()
    def resetImageSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    # **************************************************************************
    def onImageZoom(self, steps: int):
        xoom = self.zoomIn if steps > 0 else self.zoomOut
        for i in range(abs(steps)):
            xoom()

    # **************************************************************************
    @Slot()
    def zoomIn(self):
        self.scaleImage(1.0 + self.SCALE_FACTOR)

    # **************************************************************************
    @Slot()
    def zoomOut(self):
        self.scaleImage(1.0 - self.SCALE_FACTOR)

    # **************************************************************************
    def updateToolTip(self) -> None:
        self.setToolTip(f'{self.image.width()}x{self.image.height()} [x{self.scaleFactor:.02f}]')


# ******************************************************************************
