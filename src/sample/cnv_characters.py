"""Import and export noveltree character descriptions for editing. 

Convert noveltree character descriptions to odt with invisible character tags.
Convert html with invisible character tags to noveltree format.

This is a novxlib sample application.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import sys

from novxlib.converter.novx_converter import NovxConverter
from novxlib.novx_globals import CHARACTERS_SUFFIX
from novxlib.ui.ui_tk import UiTk

SUFFIX = CHARACTERS_SUFFIX


def run(sourcePath, suffix=''):
    ui = UiTk('noveltree import/export')
    converter = NovxConverter()
    converter.ui = ui
    kwargs = {'suffix': suffix}
    converter.run(sourcePath, **kwargs)
    ui.start()


if __name__ == '__main__':
    run(sys.argv[1], SUFFIX)
