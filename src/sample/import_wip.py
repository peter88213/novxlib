"""Import a work in progress. 

Convert html with chapter headings and section dividers to novelibre format.

This is a novxlib sample application.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import sys
from novxlib.ui.ui_tk import UiTk
from novxlib.converter.novx_converter import NovxConverter
SUFFIX = ''


def run(sourcePath, suffix=''):
    ui = UiTk('novelibre import/export')
    converter = NovxConverter()
    converter.ui = ui
    kwargs = {'suffix': suffix}
    converter.run(sourcePath, **kwargs)
    ui.start()


if __name__ == '__main__':
    run(sys.argv[1], SUFFIX)
