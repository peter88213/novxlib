"""Provide a class for novelibre plot line representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.model.basic_element import BasicElement


class PlotLine(BasicElement):
    """Plot line representation."""

    def __init__(self,
            shortName=None,
            sections=None,
            **kwargs):
        """Extends the superclass constructor."""
        super().__init__(**kwargs)

        self._shortName = shortName
        self._sections = sections

    @property
    def shortName(self):
        # str -- name of the plot line
        return self._shortName

    @shortName.setter
    def shortName(self, newVal):
        if self._shortName != newVal:
            self._shortName = newVal
            self.on_element_change()

    @property
    def sections(self):
        # List of str -- IDs of the sections associated with the plot line.
        try:
            return self._sections[:]
        except TypeError:
            return None

    @sections.setter
    def sections(self, newVal):
        if self._sections != newVal:
            self._sections = newVal
            self.on_element_change()

