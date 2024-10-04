"""Provide a class for ODT story structure export.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.novx_globals import STAGES_SUFFIX
from novxlib.novx_globals import _
from novxlib.odt.odt_writer import OdtWriter


class OdtWStages(OdtWriter):
    """ODT story structure file representation.

    Export a story structure description with the stages.
    """
    DESCRIPTION = _('Story structure')
    SUFFIX = STAGES_SUFFIX

    _fileHeader = f'''{OdtWriter._CONTENT_XML_HEADER}<text:p text:style-name="Title">$Title</text:p>
<text:p text:style-name="Subtitle">$AuthorName</text:p>

<text:h text:style-name="Heading_20_1" text:outline-level="1">{_('Story structure')}</text:h>
'''

    _stage1Template = '''<text:h text:style-name="Heading_20_1" text:outline-level="1"><text:bookmark text:name="$ID"/>$Title</text:h>
<text:section text:style-name="Sect1" text:name="$ID">
$Desc
</text:section>
'''

    _stage2Template = '''<text:h text:style-name="Heading_20_2" text:outline-level="2"><text:bookmark text:name="$ID"/>$Title</text:h>
<text:section text:style-name="Sect1" text:name="$ID">
$Desc
</text:section>
'''

    _fileFooter = OdtWriter._CONTENT_XML_FOOTER

