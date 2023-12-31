"""Provide a class for ods plot list representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/yw-table
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.novx_globals import AC_ROOT
from novxlib.novx_globals import CH_ROOT
from novxlib.novx_globals import MANUSCRIPT_SUFFIX
from novxlib.novx_globals import PLOTLIST_SUFFIX
from novxlib.novx_globals import _
from novxlib.novx_globals import list_to_string
from novxlib.ods.ods_writer import OdsWriter


class OdsWPlotList(OdsWriter):
    """html plot list representation.

    Public instance variables:
        filePath: str -- path to the file (property with getter and setter). 

    """
    DESCRIPTION = _('ODS Plot list')
    SUFFIX = PLOTLIST_SUFFIX

    _ADDITIONAL_STYLES = '''
  <style:style style:name="ce0" style:family="table-cell" style:parent-style-name="Default">
   <style:table-cell-properties style:text-align-source="value-type" style:repeat-content="false"/>
   <style:paragraph-properties fo:margin-left="0cm"/>
   <style:text-properties fo:color="#ff0000" fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold"/>
  </style:style>
  <style:style style:name="ce1" style:family="table-cell" style:parent-style-name="Default">
   <style:table-cell-properties fo:background-color="#b0c4de"/>
  </style:style>
  <style:style style:name="ce2" style:family="table-cell" style:parent-style-name="Default">
   <style:table-cell-properties fo:background-color="#ffd700"/>
  </style:style>
  <style:style style:name="ce3" style:family="table-cell" style:parent-style-name="Default">
   <style:table-cell-properties fo:background-color="#ff7f50"/>
  </style:style>
  <style:style style:name="ce4" style:family="table-cell" style:parent-style-name="Default">
   <style:table-cell-properties fo:background-color="#9acd32"/>
  </style:style>
  <style:style style:name="ce5" style:family="table-cell" style:parent-style-name="Default">
   <style:table-cell-properties fo:background-color="#48d1cc"/>
  </style:style>
  <style:style style:name="ce6" style:family="table-cell" style:parent-style-name="Default">
   <style:table-cell-properties fo:background-color="#dda0dd"/>
  </style:style>
 </office:automatic-styles>'''

    _fileHeader = OdsWriter._CONTENT_XML_HEADER.replace(' </office:automatic-styles>', _ADDITIONAL_STYLES)
    _fileHeader = f'{_fileHeader}{DESCRIPTION}" table:style-name="ta1" table:print="false">'

    def write_content_xml(self):
        """Create the ODS table.
        
        Raise the "Error" exception in case of error. 
        Extends the superclass method.
        """

        def create_cell(text, attr='', link=''):
            """Return the markup for a table cell with text and attributes."""
            if link:
                attr = f'{attr} table:formula="of:=HYPERLINK(&quot;file:///{self.projectPath}/{self._convert_from_novx(self.projectName)}{link}&quot;;&quot;{self._convert_from_novx(text)}&quot;)"'
                text = ''
            else:
                text = f'\n      <text:p>{self._convert_from_novx(text)}</text:p>'
            return f'     <table:table-cell {attr} office:value-type="string">{text}\n     </table:table-cell>'

        odsText = [
            self._fileHeader,
            '<table:table-column table:style-name="co4" table:default-cell-style-name="Default"/>',
            ]

        arcColorsTotal = 6
        # total number of the background colors used in the "ce" table cell styles

        arcs = self.novel.tree.get_children(AC_ROOT)

        # Arc columns.
        for acId in arcs:
            odsText.append('<table:table-column table:style-name="co3" table:default-cell-style-name="Default"/>')

        # Title row.
        odsText.append('   <table:table-row table:style-name="ro2">')
        odsText.append(create_cell(''))
        for i, acId in enumerate(arcs):
            j = (i % arcColorsTotal) + 1
            odsText.append(create_cell(self.novel.arcs[acId].title, attr=f'table:style-name="ce{j}"', link=f'_plot.odt#{acId}'))
        odsText.append('    </table:table-row>')

        # Arc/section rows.
        for chId in self.novel.tree.get_children(CH_ROOT):
            if self.novel.chapters[chId].chType == 2:
                # Arc row
                odsText.append('   <table:table-row table:style-name="ro2">')
                odsText.append(create_cell(self.novel.chapters[chId].title, attr='table:style-name="ce0"', link=f'_plot.odt#{chId}'))
                for acId in arcs:
                    odsText.append(create_cell(''))
                odsText.append(f'    </table:table-row>')
            for scId in self.novel.tree.get_children(chId):
                # Section row
                if self.novel.sections[scId].scType == 0:
                    odsText.append('   <table:table-row table:style-name="ro2">')
                    odsText.append(create_cell(self.novel.sections[scId].title, link=f'{MANUSCRIPT_SUFFIX}.odt#{scId}%7Cregion'))
                    for i, acId in enumerate(arcs):
                        colorIndex = (i % arcColorsTotal) + 1
                        if scId in self.novel.arcs[acId].sections:
                            points = []
                            for ptId in self.novel.turningPoints:
                                if scId == self.novel.turningPoints[ptId].sectionAssoc:
                                    points.append(self.novel.turningPoints[ptId].title)
                            odsText.append(create_cell(list_to_string(points), attr=f'table:style-name="ce{colorIndex}" '))
                        else:
                            odsText.append(create_cell(''))
                    odsText.append(f'    </table:table-row>')

        odsText.append(self._CONTENT_XML_FOOTER)
        with open(self.filePath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(odsText))
