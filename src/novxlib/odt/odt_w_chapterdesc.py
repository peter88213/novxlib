"""Provide a class for ODT invisibly tagged chapter descriptions export.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.novx_globals import CHAPTERS_SUFFIX
from novxlib.novx_globals import _
from novxlib.odt.odt_writer import OdtWriter


class OdtWChapterDesc(OdtWriter):
    """ODT chapter summaries file writer.

    Export a synopsis with invisibly tagged chapter descriptions.
    """
    DESCRIPTION = _('Chapter descriptions')
    SUFFIX = CHAPTERS_SUFFIX

    _fileHeader = f'''{OdtWriter._CONTENT_XML_HEADER}<text:p text:style-name="Title">$Title</text:p>
<text:p text:style-name="Subtitle">$AuthorName</text:p>
'''

    _partTemplate = '''<text:h text:style-name="Heading_20_1" text:outline-level="1">$Title</text:h>
'''

    _chapterTemplate = '''<text:section text:style-name="Sect1" text:name="$ID">
<text:h text:style-name="Heading_20_2" text:outline-level="2"><text:a xlink:href="../$ProjectName$ManuscriptSuffix.odt#$Title|outline">$Title</text:a></text:h>
$Desc
</text:section>
'''

    _fileFooter = OdtWriter._CONTENT_XML_FOOTER
