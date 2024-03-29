"""Provide a class for ODT invisibly tagged part descriptions export.

Parts are chapters marked `This chapter  begins a new section` in novelibre.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.novx_globals import PARTS_SUFFIX
from novxlib.novx_globals import _
from novxlib.odt.odt_writer import OdtWriter


class OdtWPartDesc(OdtWriter):
    """ODT part summaries file writer.

    Export a synopsis with invisibly tagged part descriptions.
    """
    DESCRIPTION = _('Part descriptions')
    SUFFIX = PARTS_SUFFIX

    _fileHeader = f'''{OdtWriter._CONTENT_XML_HEADER}<text:p text:style-name="Title">$Title</text:p>
<text:p text:style-name="Subtitle">$AuthorName</text:p>$Filters
'''

    _partTemplate = '''<text:section text:style-name="Sect1" text:name="$ID">
<text:h text:style-name="Heading_20_1" text:outline-level="1"><text:a xlink:href="../$ProjectName$ManuscriptSuffix.odt#$Title|outline">$Title</text:a></text:h>
$Desc
</text:section>
'''

    _fileFooter = OdtWriter._CONTENT_XML_FOOTER
