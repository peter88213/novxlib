"""Provide a class for ODT visibly tagged chapters and sections export.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.novx_globals import PROOF_SUFFIX
from novxlib.novx_globals import SECTION_PREFIX
from novxlib.novx_globals import _
from novxlib.odt.odt_w_formatted import OdtWFormatted


class OdtWProof(OdtWFormatted):
    """ODT proof reading file writer.

    Export a manuscript with visibly tagged chapters and sections.
    """
    DESCRIPTION = _('Tagged manuscript for proofing')
    SUFFIX = PROOF_SUFFIX

    _fileHeader = f'''$ContentHeader<text:p text:style-name="Title">$Title</text:p>
<text:p text:style-name="Subtitle">$AuthorName</text:p>$Filters
'''

    _partTemplate = '''<text:h text:style-name="Heading_20_1" text:outline-level="1">$Title</text:h>
'''

    _chapterTemplate = '''<text:h text:style-name="Heading_20_2" text:outline-level="2">$Title</text:h>
'''

    _sectionTemplate = f'''<text:h text:style-name="Heading_20_3" text:outline-level="3">$Title</text:h>
<text:p text:style-name="section_20_mark">[$ID]</text:p>
$SectionContent
<text:p text:style-name="section_20_mark">[/{SECTION_PREFIX}]</text:p>
'''

    _fileFooter = OdtWFormatted._CONTENT_XML_FOOTER

