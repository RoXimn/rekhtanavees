# -*- coding: utf-8 -*-
# ******************************************************************************
# Copyright (c) 2022. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
"""Audio timeline ruler."""
# ******************************************************************************
from PySide6.QtCore import QRect, QSize, Signal, QPoint
from PySide6.QtGui import QPaintEvent, QPainter, QFontMetrics, QResizeEvent, Qt, QBrush, QColor
from PySide6.QtWidgets import QWidget, QAbstractScrollArea


# ******************************************************************************
class RRuler(QWidget):
    sizeChanged = Signal(QSize)

    def __init__(self, parent: QAbstractScrollArea, width: int = 60):
        super(RRuler, self).__init__(parent)
        self.setFixedSize(width, parent.height())
        self.offset = 0
        parent.verticalScrollBar().valueChanged.connect(self.setOffset)
        self.adjustSize()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setPen(Qt.blue)
        painter.setBrush(QBrush(QColor(255, 0, 0, 128)))
        painter.drawRect(self.rect())
        # painter.fillRect(self.rect(), QBrush(QColor(255, 0, 0, 128)))
        # painter.translate(0, -self.offset)
        # heightMM: int = int(self.height() * self.toMM())
        # painter.setFont(self.font())
        # fm = QFontMetrics(self.font())
        # for position in range(heightMM):
        #     positionInPix: int = int(position / self.toMM())
        #     if position % 10 == 0:
        #         if position != 0:
        #             txt: str = str(position)
        #             txtRect: QRect = fm.boundingRect(txt).translated(0, positionInPix)
        #             txtRect.translate(0, txtRect.height()//2)
        #             painter.drawText(txtRect, txt)
        #         painter.drawLine(self.width() - 15, positionInPix, self.width(), positionInPix)
        #     else:
        #         painter.drawLine(self.width() - 10, positionInPix, self.width(), positionInPix)

    # def resizeEvent(self, event: QResizeEvent):
        # maximumMM: int = int(event.size().height() * self.toMM())
        # fm = QFontMetrics(self.font())
        # w: int = fm.horizontalAdvance(str(maximumMM)) + 20
        # if w != event.size().width():
        #     newSize = QSize(w, event.size().height())
        #     self.sizeChanged.emit(newSize)
        #     self.move(self.parent().width()-self.width(), 0)
        #     return self.setFixedSize(newSize)
        # return super(RRuler, self).resizeEvent(event)

    def adjustSize(self):
        print(f'adjusting from: {self.geometry()} ', end='')
        self.setFixedHeight(self.parent().height())
        self.move(self.parent().width() - self.width(), 0)
        print(f'to: {self.geometry()}')
        # super(RRuler, self).adjustSize()

    def setOffset(self, value: int):
        self.offset = value
        self.update()

    @staticmethod
    def toMM() -> float:
        return 25.4 / qApp.screens()[0].logicalDotsPerInchY()


# ******************************************************************************
if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView


    class GraphicsView(QGraphicsView):
        def __init__(self, parent: QWidget = None):
            super(GraphicsView, self).__init__(parent)
            self.ruler: RRuler = RRuler(self)
            self.setViewportMargins(0, 0, self.ruler.width(), 0)
            # self.ruler.sizeChanged.connect(self.adjustMargins)

        def resizeEvent(self, event: QResizeEvent):
            self.ruler.adjustSize()
            return super(GraphicsView, self).resizeEvent(event)

    app = QApplication()
    win = QMainWindow()
    win.setGeometry(100, 100, 800, 600)
    win.setWindowTitle("Scene Test")
    gview = GraphicsView()
    win.setCentralWidget(gview)
    scene = QGraphicsScene()
    gview.setScene(scene)
    win.show()
    app.exec()

# ******************************************************************************
