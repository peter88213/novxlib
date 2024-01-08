"""Import and export noveltree chapter descriptions for editing. 

Convert noveltree chapter descriptions to odt with invisible chapter and section tags.
Convert html with invisible chapter and section tags to noveltree format.

This is a novxlib sample application.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import sys

from novxlib.converter.novx_converter import NovxConverter
from novxlib.novx_globals import CHAPTERS_SUFFIX
from novxlib.ui.ui_tk import UiTk

SUFFIX = CHAPTERS_SUFFIX


def run(sourcePath, suffix=''):
    ui = UiTk('noveltree import/export')
    converter = NovxConverter()
    converter.ui = ui
    kwargs = {'suffix': suffix}
    converter.run(sourcePath, **kwargs)
    ui.start()


if __name__ == '__main__':
    run(sys.argv[1], SUFFIX)
