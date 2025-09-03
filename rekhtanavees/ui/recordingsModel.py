# -*- coding: utf-8 -*-
# ******************************************************************************
# Copyright (c) 2025. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
from PySide6.QtCore import QAbstractTableModel, Qt
from PySide6.QtGui import QFont

from rekhtanavees.audio import Segment
from rekhtanavees.misc.utils import hmsTimestamp, tms


# ******************************************************************************
class RecordingsTableModel(QAbstractTableModel):
    # --------------------------------------------------------------------------
    def __init__(self, segments: list[Segment] | None = None, parent = None):
        super().__init__(parent)
        self._segments = segments

    # --------------------------------------------------------------------------
    def setSegments(self, segments: list[Segment] | None):
        if segments != self._segments:
            self.beginResetModel()
            self._segments = segments
            self.endResetModel()

        self.layoutChanged.emit()

    # --------------------------------------------------------------------------
    def rowCount(self, parent=None):
        if self._segments:
            return len(self._segments)
        else:
            return 0

    # --------------------------------------------------------------------------
    def columnCount(self, parent=None):
            return 3

    # --------------------------------------------------------------------------
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or self._segments is None:
            return None

        r, c = index.row(), index.column()
        if 0 <= r < len(self._segments):
            if role == Qt.DisplayRole:
                if c == 0:
                    return hmsTimestamp(tms(self._segments[r].start))
                elif c == 1:
                    return hmsTimestamp(tms(self._segments[r].end))
                elif c == 2:
                    return self._segments[r].text
            elif role == Qt.FontRole:
                if c == 2:
                    return QFont(['Noto Naskh Arabic', 'Noto Sans'], 14, QFont.Normal)

        return None

    # --------------------------------------------------------------------------
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                # Provide column headers
                if 0 <= section < self.columnCount():
                    return ['Start', 'End', 'Text'][section]
            elif orientation == Qt.Vertical:
                # Provide row headers
                return str(section + 1)
        return None

    # --------------------------------------------------------------------------
    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable


# ******************************************************************************
