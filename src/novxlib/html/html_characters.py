"""Provide a class for HTML charcters report file representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.html.html_report import HtmlReport
from novxlib.novx_globals import CHARACTER_REPORT_SUFFIX
from novxlib.novx_globals import _


class HtmlCharacters(HtmlReport):
    """Class for HTML characters report file representation."""
    DESCRIPTION = 'HTML charcters report'
    EXTENSION = '.html'
    SUFFIX = CHARACTER_REPORT_SUFFIX

    _fileHeader = f'''{HtmlReport._fileHeader}
<title>{_('Characters')} ($Title)</title>
</head>

<body>
<p class=title>$Title {_('by')} $AuthorName - {_('Characters')}</p>
<table>
<tr class="heading">
<td class="chtitle">{_('Name')}</td>
<td>{_('Full name')}</td>
<td>{_('AKA')}</td>
<td>{_('Tags')}</td>
<td>{_('Description')}</td>
<td>{_('Bio')}</td>
<td>{_('Goals')}</td>
<td>{_('Notes')}</td>
</tr>
'''

    _characterTemplate = '''<tr>
<td class="chtitle">$Title</td>
<td>$FullName</td>
<td>$AKA</td>
<td>$Tags</td>
<td>$Desc</td>
<td>$Bio</td>
<td>$Goals</td>
<td>$Notes</td>
</tr>
'''

