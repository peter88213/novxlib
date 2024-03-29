"""Provide a class for novelibre character representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.model.world_element import WorldElement


class Character(WorldElement):
    """novelibre character representation."""
    MAJOR_MARKER = 'Major'
    MINOR_MARKER = 'Minor'

    def __init__(self,
            bio=None,
            goals=None,
            fullName=None,
            isMajor=None,
            birthDate=None,
            deathDate=None,
            **kwargs):
        """Extends the superclass constructor."""
        super().__init__(**kwargs)
        self._bio = bio
        self._goals = goals
        self._fullName = fullName
        self._isMajor = isMajor
        self._birthDate = birthDate
        self._deathDate = deathDate

    @property
    def bio(self):
        return self._bio

    @bio.setter
    def bio(self, newVal):
        if self._bio != newVal:
            self._bio = newVal
            self.on_element_change()

    @property
    def goals(self):
        return self._goals

    @goals.setter
    def goals(self, newVal):
        if self._goals != newVal:
            self._goals = newVal
            self.on_element_change()

    @property
    def fullName(self):
        return self._fullName

    @fullName.setter
    def fullName(self, newVal):
        if self._fullName != newVal:
            self._fullName = newVal
            self.on_element_change()

    @property
    def isMajor(self):
        return self._isMajor

    @isMajor.setter
    def isMajor(self, newVal):
        if self._isMajor != newVal:
            self._isMajor = newVal
            self.on_element_change()

    @property
    def birthDate(self):
        return self._birthDate

    @birthDate.setter
    def birthDate(self, newVal):
        if self._birthDate != newVal:
            self._birthDate = newVal
            self.on_element_change()

    @property
    def deathDate(self):
        return self._deathDate

    @deathDate.setter
    def deathDate(self, newVal):
        if self._deathDate != newVal:
            self._deathDate = newVal
            self.on_element_change()

