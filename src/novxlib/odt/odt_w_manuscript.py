"""Provide a class for ODT invisibly tagged chapters and sections export.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.novx_globals import MANUSCRIPT_SUFFIX
from novxlib.novx_globals import _
from novxlib.odt.odt_w_formatted import OdtWFormatted


class OdtWManuscript(OdtWFormatted):
    """ODT manuscript file writer.

    Export a manuscript with invisibly tagged chapters and sections.
    """
    DESCRIPTION = _('Editable manuscript')
    SUFFIX = MANUSCRIPT_SUFFIX

    _fileHeader = f'''$ContentHeader<text:p text:style-name="Title">$Title</text:p>
<text:p text:style-name="Subtitle">$AuthorName</text:p>
'''

    _partTemplate = '''<text:h text:style-name="Heading_20_1" text:outline-level="1">$Title</text:h>
'''

    _chapterTemplate = '''<text:h text:style-name="Heading_20_2" text:outline-level="2">$Title</text:h>
'''

    _sectionTemplate = '''<text:h text:style-name="Invisible_20_Heading_20_3" text:outline-level="3">$Title</text:h>
<text:section text:style-name="Sect1" text:name="$ID">
$SectionContent
</text:section>
'''

    _sectionDivider = '<text:p text:style-name="Heading_20_4">* * *</text:p>\n'

    _fileFooter = OdtWFormatted._CONTENT_XML_FOOTER

