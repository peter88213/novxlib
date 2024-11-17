"""Import and export novelibre character list. 

File format: csv (intended for spreadsheet conversion).
Convert novelibre character list to ods.
Convert csv to novelibre format.

This is a novxlib sample application.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novelibre
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import sys

from nvlib.model.converter.novx_converter import NovxConverter
from nvlib.novx_globals import CHARLIST_SUFFIX
from mvclib.user_interface.ui_tk import UiTk

SUFFIX = CHARLIST_SUFFIX


def run(sourcePath, suffix=''):
    ui = UiTk('novelibre import/export')
    converter = NovxConverter()
    converter.ui = ui
    kwargs = {'suffix': suffix}
    converter.run(sourcePath, **kwargs)
    ui.start()


if __name__ == '__main__':
    run(sys.argv[1], SUFFIX)
