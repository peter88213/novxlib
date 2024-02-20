"""Import an outline. 

Convert html with chapter and section headings/descriptions to novelibre format.

This is a novxlib sample application.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import sys
from novxlib.ui.ui_tk import UiTk
from novxlib.converter.converter_ff import ConverterFf
from novxlib.converter.new_project_factory import NewProjectFactory
SUFFIX = ''


def run(sourcePath, suffix=''):
    ui = UiTk('novelibre import/export')
    converter = ConverterFf()
    converter.newProjectFactory = NewProjectFactory([])
    converter.ui = ui
    kwargs = {'suffix': suffix}
    converter.run(sourcePath, **kwargs)
    ui.start()


if __name__ == '__main__':
    run(sys.argv[1], SUFFIX)
