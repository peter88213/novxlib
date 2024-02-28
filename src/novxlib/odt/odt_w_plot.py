"""Provide a class for ODT plot description export, and the filter classes needed.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from string import Template

from novxlib.novx_globals import MANUSCRIPT_SUFFIX
from novxlib.novx_globals import PLOT_SUFFIX
from novxlib.novx_globals import SECTIONS_SUFFIX
from novxlib.novx_globals import _
from novxlib.odt.odt_writer import OdtWriter


class OdtWPlot(OdtWriter):
    """ODT plot description file representation.

    Export a plot description with story structure and arcs.
    """
    DESCRIPTION = _('Plot description')
    SUFFIX = PLOT_SUFFIX

    _fileHeader = f'''{OdtWriter._CONTENT_XML_HEADER}<text:p text:style-name="Title">$Title</text:p>
<text:p text:style-name="Subtitle">$AuthorName</text:p>

<text:h text:style-name="Heading_20_1" text:outline-level="1">{_('Story structure')}</text:h>
'''

    _stage1Template = '''<text:h text:style-name="Heading_20_1" text:outline-level="1"><text:bookmark text:name="$ID"/>$Title</text:h>
$Desc
'''

    _stage2Template = '''<text:h text:style-name="Heading_20_2" text:outline-level="2"><text:bookmark text:name="$ID"/>$Title</text:h>
$Desc
'''

    _arcHeadingTemplate = f'''<text:h text:style-name="Heading_20_1" text:outline-level="1">{_('Arcs')}</text:h>
'''

    _arcTemplate = '''$Heading<text:h text:style-name="Heading_20_2" text:outline-level="2"><text:bookmark text:name="$ID"/>$Title</text:h>
$Desc
$TurningPoints
'''
    _plotPointTemplate = '''<text:h text:style-name="Heading_20_3" text:outline-level="3"><text:bookmark text:name="$ID"/>$Title</text:h>
$Desc
'''
    _assocSectionTemplate = '''<text:p text:style-name="Text_20_body">$Section: <text:span text:style-name="Emphasis">$SectionTitle</text:span></text:p>    
<text:p text:style-name="Text_20_body">→ <text:a xlink:href="../$ProjectName$SectionsSuffix.odt#$scID%7Cregion">$Description</text:a></text:p>
<text:p text:style-name="Text_20_body">→ <text:a xlink:href="../$ProjectName$ManuscriptSuffix.odt#$scID%7Cregion">$Manuscript</text:a></text:p>
'''

    _fileFooter = OdtWriter._CONTENT_XML_FOOTER

    def write(self):
        """Initialize "first arc" flag.

       Extends the superclass constructor.
        """
        self._firstArc = True
        super().write()

    def _get_arcMapping(self, acId):
        """Add associated sections to the arc mapping dictionary.
        
        Extends the superclass method.
        """
        arcMapping = super()._get_arcMapping(acId)
        if self._firstArc:
            arcMapping['Heading'] = self._arcHeadingTemplate
            self._firstArc = False
        else:
            arcMapping['Heading'] = ''
        plotPoints = []
        for tpId in self.novel.tree.get_children(acId):
            plotPointMapping = dict(
                    ID=tpId,
                    Title=self.novel.turningPoints[tpId].title,
                    Desc=self.novel.turningPoints[tpId].desc,
                    )
            template = Template(self._plotPointTemplate)
            plotPoints.append(template.safe_substitute(plotPointMapping))
            scId = self.novel.turningPoints[tpId].sectionAssoc
            if scId:
                sectionAssocMapping = dict(
                    SectionTitle=self.novel.sections[scId].title,
                    ProjectName=self._convert_from_novx(self.projectName, True),
                    Section=_('Section'),
                    Description=_('Description'),
                    Manuscript=_('Manuscript'),
                    scID=scId,
                    ManuscriptSuffix=MANUSCRIPT_SUFFIX,
                    SectionsSuffix=SECTIONS_SUFFIX,
                    )
                template = Template(self._assocSectionTemplate)
                plotPoints.append(template.safe_substitute(sectionAssocMapping))
        arcMapping['TurningPoints'] = '\n'.join(plotPoints)
        return arcMapping

