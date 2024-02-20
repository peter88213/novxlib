"""Provide a class for ODT invisibly tagged part descriptions import.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.novx_globals import PARTS_SUFFIX
from novxlib.novx_globals import _
from novxlib.odt.odt_r_chapterdesc import OdtRChapterDesc


class OdtRPartDesc(OdtRChapterDesc):
    """ODT part summaries file reader.

    Parts are chapters marked in novelibre as beginning of a new section.
    Import a synopsis with invisibly tagged part descriptions.
    """
    DESCRIPTION = _('Part descriptions')
    SUFFIX = PARTS_SUFFIX
