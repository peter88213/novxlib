"""Provide a class for ODT invisibly tagged stage descriptions import.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.novx_globals import STAGES_SUFFIX
from novxlib.novx_globals import _
from novxlib.odt.odt_r_sectiondesc import OdtRSectionDesc


class OdtRStages(OdtRSectionDesc):
    """ODT stage summaries file reader.

    Import a story structure with invisibly tagged section descriptions.
    """
    DESCRIPTION = _('Story structure')
    SUFFIX = STAGES_SUFFIX

