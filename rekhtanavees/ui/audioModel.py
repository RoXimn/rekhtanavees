# -*- coding: utf-8 -*-
# ******************************************************************************
# Copyright (c) 2022. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
from typing import Any, List, Sequence, Union

from PySide6.QtCore import QAbstractListModel, QMimeData, QModelIndex, QObject, QPersistentModelIndex, Qt

from audio.audioproject import AudioProject


# ******************************************************************************
class RAudioModel(QAbstractListModel):

    def __init__(self, parent: QObject, audioProject: AudioProject):
        super(RAudioModel, self).__init__(parent)
        self.audioProject = audioProject

    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> Any:  # type: ignore
        return None

    def supportedDragActions(self) -> Qt.DropActions:
        return Qt.MoveAction

    def rowCount(self, parent: QModelIndex) -> int:  # type: ignore
        return len(self.audioProject.recordings)

    def data(self, index: QModelIndex, role: int) -> Any:  # type: ignore
        return None

    def flags(self, index: Union[QModelIndex, QPersistentModelIndex]) -> Qt.ItemFlags:
        defaultFlags = super(RAudioModel, self).flags(index)

        if index.isValid():
            return Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | defaultFlags
        else:
            return Qt.ItemIsDropEnabled | defaultFlags

    def mimeTypes(self) -> List[str]:
        return ['application/vnd.audio.recording']

    def mimeData(self, indexes: Sequence[QModelIndex]) -> QMimeData:
        mimeData = QMimeData()
        ii = ','.join(str(index.row()) for index in indexes if index.isValid())
        mimeData.setData('application/vnd.audio.recording', ii.encode('utf-8'))
        return mimeData

    def canDropMimeData(self, data: QMimeData, action: Qt.DropAction,
                        row: int, column: int,
                        parent: Union[QModelIndex, QPersistentModelIndex]) -> bool:
        if not data.hasFormat('application/vnd.audio.recording'):
            return False
        if not column == 0:
            return False
        return True

    def dropMimeData(self, data: QMimeData, action: Qt.DropAction,
                     row: int, column: int,
                     parent: Union[QModelIndex, QPersistentModelIndex]) -> bool:
        if not self.canDropMimeData(data, action, row, column, parent):
            return False

        if action == Qt.IgnoreAction:
            return True

        if row != -1:
            beginRow = row
        elif parent.isValid():
            beginRow = parent.row()
        else:
            beginRow = self.rowCount(QModelIndex())

        droppedRows: List[int] = [int(ii) for ii in data.data('application/vnd.audio.recording').decode('utf-8').split(',')]  # type: ignore

        self.insertRows(beginRow, len(droppedRows))
        for ii in droppedRows:
            idx = self.index(beginRow, 0, QModelIndex())
            # update the row at new location
            beginRow += 1

        return True


# ******************************************************************************


# ******************************************************************************


# ******************************************************************************
