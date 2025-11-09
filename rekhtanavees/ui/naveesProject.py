# ******************************************************************************
# Copyright (c) 2025. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit # http://creativecommons.org/licenses/by/4.0/.
#
# Author:      RoXimn <roximn@rixir.org>
# ******************************************************************************
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from rekhtanavees.audio.audioproject import AudioProject


# ******************************************************************************
class NaveesProject(QObject):
    """Project class based on QObject to interact with the UI."""

    # --------------------------------------------------------------------------
    projectModified = Signal(bool)
    """Indicates change in project modification status."""

    # --------------------------------------------------------------------------
    def __init__(self, parent: QObject):
        super(NaveesProject, self).__init__(parent)

        self.data: AudioProject | None = None

    # --------------------------------------------------------------------------
    def modificationStatusChanged(self):
        assert self.data is None

    # --------------------------------------------------------------------------
    def new(self, folder: Path, name: str, author: str, email: str, description: str):
        assert self.data is None
        # Create project directory
        folder.mkdir(parents=True, exist_ok=True)
        qApp.logger.debug(f'Project directory "{folder}" successfully created')

        self.data = AudioProject(path=folder, name=name)

        self.data.title = name
        self.data.authorName = author
        self.data.authorEmail = email
        self.data.description = description

        def projectChanged(status: bool) -> None:
            self.projectModified.emit(status)
        self.data.notifyObserver = projectChanged

        self.data.saveProject()
        qApp.logger.info(f'New project file "{self.data.filename}" created in {self.data.folder}')

    # --------------------------------------------------------------------------
    def open(self, projectFilePath: Path):
        assert self.data is None
        self.data = AudioProject(path=projectFilePath)
        self.data.loadProject()

    # --------------------------------------------------------------------------
    def save(self):
        assert self.data

        self.data.saveProject()

    # --------------------------------------------------------------------------
    def saveAs(self, filePath: Path):
        assert self.data

        self.data.setFilePath(filePath)
        self.data.saveProject()

    # --------------------------------------------------------------------------
    def close(self, save: bool = True):
        if self.data is None:
            return

        if save and self.data.isModified:
            self.data.saveProject()

        self.data = None

    # --------------------------------------------------------------------------

# ******************************************************************************
