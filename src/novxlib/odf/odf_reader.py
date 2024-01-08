"""Provide an abstract ODF file reader class.

Other ODF file readers inherit from this class.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import os
from abc import ABC, abstractmethod
from novxlib.file.file import File
from novxlib.odf.check_odf import odf_is_locked


class OdfReader(File, ABC):
    """Abstract OpenDocument file reader."""

    def is_locked(self):
        """Return True if the file is locked by its application."""
        return odf_is_locked(self.filePath)
