"""Import and export XML data files. 

This is a novxlib sample application.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novelibre
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import sys

from novxlib.converter.novx_exporter import NovxExporter
from mvclib.user_interface.ui_tk import UiTk
from nvlib.model.novx.data_writer import DataWriter
from nvlib.novx_globals import DATA_SUFFIX

SUFFIX = DATA_SUFFIX


def run(sourcePath, suffix=''):
    ui = UiTk('novelibre import/export')
    converter = NovxExporter()
    converter.ui = ui
    converter.EXPORT_TARGET_CLASSES.append(DataWriter)
    kwargs = {'suffix': suffix}
    converter.run(sourcePath, **kwargs)
    ui.start()


if __name__ == '__main__':
    run(sys.argv[1], SUFFIX)
