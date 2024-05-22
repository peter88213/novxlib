"""Provide a class with getters and factory methods for novxlib model objects.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.model.basic_element import BasicElement
from novxlib.model.chapter import Chapter
from novxlib.model.character import Character
from novxlib.model.novel import Novel
from novxlib.model.nv_tree import NvTree
from novxlib.model.plot_line import PlotLine
from novxlib.model.plot_point import PlotPoint
from novxlib.model.section import Section
from novxlib.model.world_element import WorldElement
from novxlib.novx.novx_file import NovxFile


class NovxService:
    """Getters and factory methods for novxlib model objects."""

    def get_novx_file_extension(self):
        return NovxFile.EXTENSION

    def make_basic_element(self, **kwargs):
        return BasicElement(**kwargs)

    def make_chapter(self, **kwargs):
        return Chapter(**kwargs)

    def make_character(self, **kwargs):
        return Character(**kwargs)

    def make_novel(self, **kwargs):
        kwargs['tree'] = kwargs.get('tree', NvTree())
        return Novel(**kwargs)

    def make_nv_tree(self, **kwargs):
        return NvTree(**kwargs)

    def make_plot_line(self, **kwargs):
        return PlotLine(**kwargs)

    def make_plot_point(self, **kwargs):
        return PlotPoint(**kwargs)

    def make_section(self, **kwargs):
        return Section(**kwargs)

    def make_world_element(self, **kwargs):
        return WorldElement(**kwargs)

    def make_novx_file(self, filePath, **kwargs):
        return NovxFile(filePath, **kwargs)

