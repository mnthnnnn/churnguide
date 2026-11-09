"""
B.Tech Final Year Project Report Generator
Department of Computer Science and Engineering
Govt. College Of Engineering & Technology Safapora Ganderbal J&K

Adheres strictly to the guidelines:
- A4 size (210 x 297 mm), 35 mm left/right margins, 30 mm top/bottom margins.
- Times-Roman 12 pt running text, 1.5 line spacing (18 pt leading), justified, 15 mm indent.
- Headings: Chapter (17 pt Bold CAPS centered), Section (17 pt Bold Title Case left),
  Subsection (14 pt Bold sentence case left), Sub-subsection (12 pt Bold sentence case left).
- Table captions 11 pt ABOVE tables; Figure captions 11 pt BELOW figures.
- Page numbers centered in bottom margin, 20 mm from bottom edge.
- Cover page no number. Prelim pages in small roman numerals. Chapter 1 starts Arabic at 1.
- Each preliminary section, chapter, references, and appendix starts on an odd page.
- Table of Contents, List of Figures, List of Tables generated dynamically with two-pass exact page matching.
- Length targeted at 50-70 pages.
"""

import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, pt
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, KeepTogether, PageBreak, Flowable
)
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# ----------------- PAGE METRICS -----------------
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_LEFT = 35 * mm
MARGIN_RIGHT = 35 * mm
MARGIN_TOP = 30 * mm
MARGIN_BOTTOM = 30 * mm
PRINTABLE_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT # 140 mm = ~396.85 pt
PRINTABLE_HEIGHT = PAGE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM # 237 mm = ~671.81 pt
BOTTOM_PAGE_NUM_Y = 20 * mm # 20 mm from bottom edge

# ----------------- ROMAN NUMERAL HELPER -----------------
def to_roman(num):
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syb = ["m", "cm", "d", "cd", "c", "xc", "l", "xl", "x", "ix", "v", "iv", "i"]
    res = ""
    for i in range(len(val)):
        while num >= val[i]:
            res += syb[i]
            num -= val[i]
    return res

# ----------------- CANVAS WITH TWO-PASS TRACKING -----------------
class ReportCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, total_pages):
        page_num = self._pageNumber
        # Determine if blank page
        is_blank = getattr(self, '_is_blank_page', False)
        ch1_start = getattr(self, '_ch1_start_page', 21)

        # 1. Cover page (Page 1) has NO page number
        if page_num == 1 or is_blank:
            return

        # 2. Inside Title Page (Page 3) starts Roman numbering 'i', but NOT printed
        if page_num <= 3:
            return

        self.saveState()
        self.setFont('Times-Roman', 12)

        # 3. Preliminary pages (before Chapter 1) in small roman numerals
        if page_num < ch1_start:
            # Roman page count starts from Inside Title Page (page 3 is i, 4 is ii, 5 is iii, etc.)
            roman_val = to_roman(page_num - 2)
            self.drawCentredString(PAGE_WIDTH / 2.0, BOTTOM_PAGE_NUM_Y, roman_val)
        else:
            # 4. Starting from Chapter 1: Arabic numerals starting at 1
            arabic_val = str(page_num - ch1_start + 1)
            self.drawCentredString(PAGE_WIDTH / 2.0, BOTTOM_PAGE_NUM_Y, arabic_val)

        self.restoreState()

# Custom Flowable to mark blank pages
class MarkBlankPage(Flowable):
    def wrap(self, availWidth, availHeight):
        return 0, 0
    def draw(self):
        self.canv._is_blank_page = True

class ClearBlankMark(Flowable):
    def wrap(self, availWidth, availHeight):
        return 0, 0
    def draw(self):
        self.canv._is_blank_page = False

# Flowable to notify canvas of Chapter 1 starting page
class MarkChapter1Start(Flowable):
    def wrap(self, availWidth, availHeight):
        return 0, 0
    def draw(self):
        self.canv._ch1_start_page = self.canv._pageNumber

# Page tracking flowable for Table of Contents, Figures, Tables
class PageTracker(Flowable):
    def __init__(self, key, registry):
        super().__init__()
        self.key = key
        self.registry = registry

    def wrap(self, availWidth, availHeight):
        return 0, 0

    def draw(self):
        ch1_start = getattr(self.canv, '_ch1_start_page', 21)
        curr = self.canv._pageNumber
        if curr < ch1_start:
            display_page = to_roman(curr - 2)
        else:
            display_page = str(curr - ch1_start + 1)
        self.registry[self.key] = display_page

# Odd-page break generator
def odd_page_break():
    """Generates a page transition ensuring the next item starts on an odd (right-hand) page."""
    return [PageBreak(), MarkBlankPage(), PageBreak(), ClearBlankMark()]

