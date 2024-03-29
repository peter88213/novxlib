"""Provide a class for a novelibre element with notes and tags.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.model.basic_element_notes import BasicElementNotes


class BasicElementTags(BasicElementNotes):
    """Basic element with notes and tags."""

    def __init__(self,
            tags=None,
            **kwargs):
        """Extends the superclass constructor"""
        super().__init__(**kwargs)
        self._tags = tags

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, newVal):
        # str: semicolon-separated tags
        if self._tags != newVal:
            self._tags = newVal
            self.on_element_change()

