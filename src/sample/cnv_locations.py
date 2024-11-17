"""Import and export novelibre location descriptions for editing. 

Convert novelibre location descriptions to odt with invisible location tags.
Convert html with invisible location tags to novelibre format.

This is a novxlib sample application.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novelibre
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import sys

from nvlib.model.converter.novx_converter import NovxConverter
from nvlib.novx_globals import LOCATIONS_SUFFIX
from mvclib.user_interface.ui_tk import UiTk

SUFFIX = LOCATIONS_SUFFIX


def run(sourcePath, suffix=''):
    ui = UiTk('novelibre import/export')
    converter = NovxConverter()
    converter.ui = ui
    kwargs = {'suffix': suffix}
    converter.run(sourcePath, **kwargs)
    ui.start()


if __name__ == '__main__':
    run(sys.argv[1], SUFFIX)
