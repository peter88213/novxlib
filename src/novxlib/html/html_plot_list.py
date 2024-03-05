"""Provide a class for html plot list representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.html.html_report import HtmlReport
from novxlib.novx_globals import AC_ROOT
from novxlib.novx_globals import CH_ROOT
from novxlib.novx_globals import PLOTLIST_SUFFIX
from novxlib.novx_globals import _
from novxlib.novx_globals import list_to_string


class HtmlPlotList(HtmlReport):
    """html plot list representation."""
    DESCRIPTION = _('HTML Plot list')
    SUFFIX = PLOTLIST_SUFFIX

    def write(self):
        """Create a HTML table.
        
        Raise the "Error" exception in case of error. 
        Extends the superclass method.
        """

        def create_cell(text, attr=''):
            """Return the markup for a table cell with text and attributes."""
            return f'<td {attr}>{self._convert_from_novx(text)}</td>'

        STYLE_CH_TITLE = 'font-weight: bold; color: red'
        htmlText = [self._fileHeader]
        htmlText.append(f'''<title>{self.novel.title}</title>
</head>
<body>
<p class=title>{self.novel.title} - {_("Plot")}</p>
<table>''')
        arcColors = (
            'LightSteelBlue',
            'Gold',
            'Coral',
            'YellowGreen',
            'MediumTurquoise',
            'Plum',
            )

        # Get plot lines.
        if self.novel.tree.get_children(AC_ROOT) is not None:
            arcs = self.novel.tree.get_children(AC_ROOT)
        else:
            arcs = []

        # Title row.
        htmlText.append('<tr class="heading">')
        htmlText.append(create_cell(''))
        for i, acId in enumerate(arcs):
            colorIndex = i % len(arcColors)
            htmlText.append(create_cell(self.novel.arcs[acId].title, attr=f'style="background: {arcColors[colorIndex]}"'))
        htmlText.append('</tr>')

        # Section rows.
        for chId in self.novel.tree.get_children(CH_ROOT):
            for scId in self.novel.tree.get_children(chId):
                # Section row
                if self.novel.sections[scId].scType == 0:
                    htmlText.append(f'<tr>')
                    htmlText.append(create_cell(self.novel.sections[scId].title))
                    for i, acId in enumerate(arcs):
                        colorIndex = i % len(arcColors)
                        if scId in self.novel.arcs[acId].sections:
                            points = []
                            for ptId in self.novel.tree.get_children(acId):
                                if scId == self.novel.turningPoints[ptId].sectionAssoc:
                                    points.append(self.novel.turningPoints[ptId].title)
                            htmlText.append(create_cell(list_to_string(points), attr=f'style="background: {arcColors[colorIndex]}"'))
                        else:
                            htmlText.append(create_cell(''))
                    htmlText.append(f'</tr>')

        htmlText.append(self._fileFooter)
        with open(self.filePath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(htmlText))
