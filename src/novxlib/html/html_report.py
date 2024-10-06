"""Provide a base class for HTML report file representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from html import escape
from novxlib.file.file_export import FileExport


class HtmlReport(FileExport):
    """Class for HTML report file representation."""
    DESCRIPTION = 'HTML report'
    EXTENSION = '.html'
    SUFFIX = '_report'

    _fileHeader = '''<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>

<style type="text/css">
body {font-family: sans-serif}
p.title {font-size: larger; font-weight: bold}
td {padding: 10}
tr.heading {font-size:smaller; font-weight: bold; background-color:rgb(240,240,240)}
table {border-spacing: 0}
table, td {border: rgb(240,240,240) solid 1px; vertical-align: top}
td.chtitle {font-weight: bold}
</style>

'''

    _fileFooter = '''</table>
</body>
</html>
'''

    def _convert_from_novx(self, text, **kwargs):
        """Return text, converted from *mdnovel* markup to target format.
        
        Positional arguments:
            text -- string to convert.
        
        Overrides the superclass method.
        """
        if not text:
            return ''

        text = escape(text.rstrip())
        newlines = []
        for line in text.split('\n'):
            newlines.append(f'<p>{line}</p>')
        return '\n'.join(newlines)

