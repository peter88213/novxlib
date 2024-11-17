"""Export novelibre brief synopsis. 

This is a novxlib sample application.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novelibre
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import sys

from novxlib.converter.novx_exporter import NovxExporter
from mvclib.user_interface.ui_tk import UiTk
from nvlib.novx_globals import BRF_SYNOPSIS_SUFFIX

SUFFIX = BRF_SYNOPSIS_SUFFIX


def run(sourcePath, suffix=''):
    ui = UiTk('novelibre import/export')
    converter = NovxExporter()
    converter.ui = ui
    kwargs = {'suffix': suffix}
    converter.run(sourcePath, **kwargs)
    ui.start()


if __name__ == '__main__':
    run(sys.argv[1], SUFFIX)
