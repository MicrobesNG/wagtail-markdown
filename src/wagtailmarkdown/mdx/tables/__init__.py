"""
Tables Extension for Python-Markdown
====================================

Added parsing of tables to Python-Markdown.

A simple example:

    First Header  | Second Header
    ------------- | -------------
    Content Cell  | Content Cell
    Content Cell  | Content Cell

Copyright 2009 - [Waylan Limberg](http://achinghead.com)
"""


import markdown

from packaging.version import Version


if Version(markdown.__version__) >= Version("3.2"):
    # Using markdown version 3.2+
    import xml.etree.ElementTree as etree
else:
    # Using markdown below 3.2
    from markdown.util import etree

from markdown import Extension
from markdown.blockprocessors import BlockProcessor


class TableProcessor(BlockProcessor):
    """Process Tables."""

    def test(self, parent, block):
        rows = block.split("\n")
        return (
            len(rows) > 2
            and "|" in rows[0]
            and "|" in rows[1]
            and "-" in rows[1]
            and rows[1].strip()[0] in ["|", ":", "-"]
        )

    def run(self, parent, blocks):
        """Parse a table block and build table."""
        block = blocks.pop(0).split("\n")
        header = block[0].strip()
        seperator = block[1].strip()
        rows = block[2:]
        # Get format type (bordered by pipes or not)
        border = False
        if header.startswith("|"):
            border = True
        # Get alignment of columns
        align = []
        for c in self._split_row(seperator, border):
            if c.startswith(":") and c.endswith(":"):
                align.append("center")
            elif c.startswith(":"):
                align.append("left")
            elif c.endswith(":"):
                align.append("right")
            else:
                align.append(None)
        # Build table
        table = etree.SubElement(parent, "table")
        table.set("class", "wftable")
        thead = etree.SubElement(table, "thead")
        self._build_row(header, thead, align, border)
        tbody = etree.SubElement(table, "tbody")
        for row in rows:
            self._build_row(row.strip(), tbody, align, border)

    def _build_row(self, row, parent, align, border):
        """Given a row of text, build table cells."""
        tr = etree.SubElement(parent, "tr")
        tag = "td"
        if parent.tag == "thead":
            tag = "th"
        cells = self._split_row(row, border)
        # We use align here rather than cells to ensure every row
        # contains the same number of columns.
        for i, a in enumerate(align):
            c = etree.SubElement(tr, tag)
            try:
                c.text = cells[i].strip()
            except IndexError:
                c.text = ""
            if a:
                c.set("align", a)

    def _split_row(self, row, border):
        """split a row of text into list of cells."""
        if border:
            if row.startswith("|"):
                row = row[1:]
            if row.endswith("|"):
                row = row[:-1]
        return row.split("|")


class TableExtension(Extension):
    """Add tables to Markdown."""

    def extendMarkdown(self, md):
        """Add an instance of TableProcessor to BlockParser."""
        md.parser.blockprocessors.register(TableProcessor(md.parser), "table", 69)
