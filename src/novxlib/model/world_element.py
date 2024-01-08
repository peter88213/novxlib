"""Provide a generic class for noveltree story world element representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import os
from novxlib.model.basic_element import BasicElement


class WorldElement(BasicElement):
    """Story world element representation (may be location or item)."""

    def __init__(self,
            aka=None,
            tags=None,
            links=None,
            **kwargs):
        """Extends the superclass constructor"""
        super().__init__(**kwargs)
        self._aka = aka
        self._tags = tags
        # semicolon-separated tags
        self._links = links
        # dictionary (Key = path:str, value = title:str) -- paths to linked files

    @property
    def aka(self):
        return self._aka

    @aka.setter
    def aka(self, newVal):
        if self._aka != newVal:
            self._aka = newVal
            self.on_element_change()

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, newVal):
        if self._tags != newVal:
            self._tags = newVal
            self.on_element_change()

    @property
    def links(self):
        try:
            return self._links.copy()
        except AttributeError:
            return None

    @links.setter
    def links(self, newVal):
        if self._links != newVal:
            self._links = newVal
            for linkPath in newVal:
                self._links[linkPath] = os.path.split(linkPath)[1]
                # setting the plain file name as link title
            self.on_element_change()

