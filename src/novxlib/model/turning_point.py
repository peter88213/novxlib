"""Provide a class for novelibre plot point representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.model.basic_element import BasicElement


class TurningPoint(BasicElement):
    """Plot point representation."""

    def __init__(self,
            sectionAssoc=None,
            notes=None,
            **kwargs):
        """Extends the superclass constructor."""
        super().__init__(**kwargs)

        self._sectionAssoc = sectionAssoc
        # str -- ID of the associated section

        self._notes = notes

    @property
    def sectionAssoc(self):
        return self._sectionAssoc

    @sectionAssoc.setter
    def sectionAssoc(self, newVal):
        if self._sectionAssoc != newVal:
            self._sectionAssoc = newVal
            self.on_element_change()

    @property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, newVal):
        if self._notes != newVal:
            self._notes = newVal
            self.on_element_change()

