"""
Production B.Tech Project Report Generator
Compiles report/project_report.pdf with two-pass exact page number resolution.
Department of Computer Science and Engineering
Govt. College Of Engineering & Technology Safapora Ganderbal J&K
"""

import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import fitz  # PyMuPDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
pt = 1
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, KeepTogether, PageBreak, Flowable
)
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from report.report_content import (
    PROJECT_TITLE, DEGREE_TEXT, DEPARTMENT_TEXT, SUBMISSION_MONTH_YEAR,
    SUPERVISOR_FIELD, SUPERVISOR_DESIG_FIELD, HOD_FIELD, HOD_DESIG_FIELD,
    GROUP_FIELD, DATE_FIELD, CANDIDATES, ABSTRACT_TEXT, ABBREVIATIONS,
    NOTATIONS, REFERENCES_LIST
)

from report.chapters_data import (
    CH1_SECTIONS, CH2_SECTIONS, CH3_SECTIONS, CH4_SECTIONS,
    CH5_SECTIONS, CH6_SECTIONS, CH7_SECTIONS,
    APPENDIX_A_CONTENT, APPENDIX_B_CONTENT, APPENDIX_C_CONTENT
)

# Dimensions & Margins
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_LEFT = 35 * mm
MARGIN_RIGHT = 35 * mm
MARGIN_TOP = 30 * mm
MARGIN_BOTTOM = 30 * mm
PRINTABLE_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT # 140 mm = ~396.85 pt
PRINTABLE_HEIGHT = PAGE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM # 237 mm = ~671.81 pt
BOTTOM_PAGE_NUM_Y = 20 * mm

def to_roman(num):
    if num <= 0:
        return "i"
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syb = ["m", "cm", "d", "cd", "c", "xc", "l", "xl", "x", "ix", "v", "iv", "i"]
    res = ""
    for i in range(len(val)):
        while num >= val[i]:
            res += syb[i]
            num -= val[i]
    return res

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
            roman_val = to_roman(page_num - 2)
            self.drawCentredString(PAGE_WIDTH / 2.0, BOTTOM_PAGE_NUM_Y, roman_val)
        else:
            # 4. Starting from Chapter 1: Arabic numerals starting at 1
            arabic_val = str(page_num - ch1_start + 1)
            self.drawCentredString(PAGE_WIDTH / 2.0, BOTTOM_PAGE_NUM_Y, arabic_val)

        self.restoreState()

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

class MarkChapter1Start(Flowable):
    def wrap(self, availWidth, availHeight):
        return 0, 0
    def draw(self):
        self.canv._ch1_start_page = self.canv._pageNumber

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

class SectionEndTracker(Flowable):
    def __init__(self, key, registry):
        super().__init__()
        self.key = key
        self.registry = registry

    def wrap(self, availWidth, availHeight):
        return 0, 0

    def draw(self):
        self.registry[self.key] = self.canv._pageNumber

def odd_section_break():
    """Unconditionally inserts a pagebreak, blank page, and pagebreak for 1-page preliminary items."""
    return [PageBreak(), MarkBlankPage(), PageBreak(), ClearBlankMark()]

def even_section_break():
    """For 2-page items that end on an even page, a single pagebreak moves to the next odd page."""
    return [PageBreak()]

def odd_transition(key, end_registry):
    """
    Ensures that the next section starts on an odd page.
    If the section ended on an odd page, the next page is even, so we insert a blank page.
    If the section ended on an even page, the next page is odd, so a single PageBreak is sufficient.
    """
    end_page = end_registry.get(key)
    if end_page is not None:
        if end_page % 2 == 1:
            return [PageBreak(), MarkBlankPage(), PageBreak(), ClearBlankMark()]
        else:
            return [PageBreak()]
    # Fallback during Pass 1:
    if key in ('COVER', 'INSIDE_TITLE', 'CERTIFICATE_END', 'DECLARATION_END', 'ACK_END', 'ABS_END', 'LOF_END', 'LOT_END'):
        return [PageBreak(), MarkBlankPage(), PageBreak(), ClearBlankMark()]
    elif key in ('TOC_END', 'ABB_END'):
        return [PageBreak()]
    else:
        return [PageBreak()]


def get_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='RunningText',
        fontName='Times-Roman',
        fontSize=12,
        leading=18,
        alignment=TA_JUSTIFY,
        firstLineIndent=15 * mm,
        spaceAfter=3
    ))

    styles.add(ParagraphStyle(
        name='RunningTextNoIndent',
        fontName='Times-Roman',
        fontSize=12,
        leading=18,
        alignment=TA_JUSTIFY,
        firstLineIndent=0,
        spaceAfter=3
    ))

    styles.add(ParagraphStyle(
        name='SingleSpacedText',
        fontName='Times-Roman',
        fontSize=12,
        leading=15,
        alignment=TA_JUSTIFY,
        firstLineIndent=15 * mm,
        spaceAfter=3
    ))

    styles.add(ParagraphStyle(
        name='ChapterNumberHeading',
        fontName='Times-Bold',
        fontSize=17,
        leading=22,
        alignment=TA_CENTER,
        spaceAfter=6,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name='ChapterTitleHeading',
        fontName='Times-Bold',
        fontSize=17,
        leading=22,
        alignment=TA_CENTER,
        spaceAfter=20,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name='ReportSectionHeading',
        fontName='Times-Bold',
        fontSize=16,
        leading=20,
        alignment=TA_LEFT,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name='ReportSubsectionHeading',
        fontName='Times-Bold',
        fontSize=13,
        leading=17,
        alignment=TA_LEFT,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name='ReportSubsubsectionHeading',
        fontName='Times-Bold',
        fontSize=12,
        leading=16,
        alignment=TA_LEFT,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name='ReportTableCaption',
        fontName='Times-Bold',
        fontSize=11,
        leading=14,
        alignment=TA_LEFT,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name='ReportFigureCaption',
        fontName='Times-Bold',
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=10
    ))

    styles.add(ParagraphStyle(
        name='TOCItemTitle',
        fontName='Times-Roman',
        fontSize=10,
        leading=13,
        alignment=TA_LEFT
    ))

    styles.add(ParagraphStyle(
        name='TOCItemTitleBold',
        fontName='Times-Bold',
        fontSize=10,
        leading=13,
        alignment=TA_LEFT
    ))

    styles.add(ParagraphStyle(
        name='TOCItemPage',
        fontName='Times-Roman',
        fontSize=10,
        leading=13,
        alignment=TA_RIGHT
    ))

    styles.add(ParagraphStyle(
        name='TOCItemPageBold',
        fontName='Times-Bold',
        fontSize=10,
        leading=13,
        alignment=TA_RIGHT
    ))

    styles.add(ParagraphStyle(
        name='ReferenceItem',
        fontName='Times-Roman',
        fontSize=10,
        leading=13,
        alignment=TA_JUSTIFY,
        leftIndent=10 * mm,
        firstLineIndent=-10 * mm,
        spaceAfter=3
    ))

    styles.add(ParagraphStyle(
        name='CodeSnippet',
        fontName='Courier',
        fontSize=8.0,
        leading=10.5,
        alignment=TA_LEFT,
        spaceAfter=2
    ))

    return styles

def build_cover_page(styles):
    """Sample Sheet 1: Cover Page Layout."""
    elements = []
    # Title: TNR 16 Bold Centered
    title_style = ParagraphStyle(
        'CoverTitle',
        fontName='Times-Bold',
        fontSize=16,
        leading=22,
        alignment=TA_CENTER
    )
    elements.append(Spacer(1, 15 * mm))
    elements.append(Paragraph(PROJECT_TITLE, title_style))
    elements.append(Spacer(1, 12 * mm))

    sub1_style = ParagraphStyle(
        'CoverSub1',
        fontName='Times-BoldItalic',
        fontSize=12,
        leading=16,
        alignment=TA_CENTER
    )
    elements.append(Paragraph("Project Report submitted<br/>in partial fulfillment of the requirements for the degree", sub1_style))
    elements.append(Spacer(1, 4 * mm))
    elements.append(Paragraph("of", sub1_style))
    elements.append(Spacer(1, 4 * mm))

    sub2_style = ParagraphStyle(
        'CoverSub2',
        fontName='Times-Bold',
        fontSize=14,
        leading=18,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(DEGREE_TEXT, sub2_style))
    elements.append(Spacer(1, 4 * mm))
    elements.append(Paragraph("by", sub1_style))
    elements.append(Spacer(1, 4 * mm))

    # Candidates list
    cand_lines = "<br/>".join([f"{c['name']} ({c['enrolment']})" for c in CANDIDATES])
    elements.append(Paragraph(cand_lines, sub2_style))
    elements.append(Spacer(1, 2 * mm))
    elements.append(Paragraph(GROUP_FIELD, sub2_style))
    elements.append(Spacer(1, 6 * mm))

    elements.append(Paragraph("Under the guidance of", sub1_style))
    elements.append(Spacer(1, 4 * mm))
    elements.append(Paragraph(f"{SUPERVISOR_FIELD}<br/>{SUPERVISOR_DESIG_FIELD}", sub2_style))
    elements.append(Spacer(1, 10 * mm))

    elements.append(Paragraph(DEPARTMENT_TEXT, sub2_style))
    elements.append(Spacer(1, 3 * mm))
    elements.append(Paragraph(SUBMISSION_MONTH_YEAR, sub2_style))

    return elements

def build_certificate_page(styles, registry):
    """Sample Sheet 2: Certificate Layout."""
    elements = []
    elements.append(PageTracker('CERTIFICATE', registry))
    cert_heading = ParagraphStyle('CertHeading', fontName='Times-Bold', fontSize=17, leading=22, alignment=TA_CENTER, spaceAfter=24)
    elements.append(Paragraph("CERTIFICATE", cert_heading))
    elements.append(Spacer(1, 10 * mm))

    body_style = ParagraphStyle('CertBody', fontName='Times-Roman', fontSize=12, leading=22, alignment=TA_JUSTIFY, firstLineIndent=15 * mm)
    names_str = ", ".join([f"{c['name']} ({c['enrolment']})" for c in CANDIDATES])
    cert_text = (
        f"This is to certify that the project report entitled <b>\"{PROJECT_TITLE}\"</b> "
        f"submitted by {names_str} to the Department of Computer Science and Engineering, "
        f"Govt. College Of Engineering & Technology Safapora Ganderbal J&K, in partial fulfillment for the award "
        f"of the degree of B. Tech in Computer Science and Engineering is a bona fide record of project work "
        f"carried out by them under my/our supervision."
    )
    elements.append(Paragraph(cert_text, body_style))
    elements.append(Spacer(1, 35 * mm))

    # Signature table at bottom
    sig_data = [
        [
            Paragraph(f"<b>{SUPERVISOR_FIELD}</b><br/>{SUPERVISOR_DESIG_FIELD}<br/>Department of CSE,<br/>GCET Safapora", styles['RunningTextNoIndent']),
            Paragraph(f"<b>{HOD_FIELD}</b><br/>{HOD_DESIG_FIELD}<br/>Department of CSE,<br/>GCET Safapora", styles['RunningTextNoIndent'])
        ]
    ]
    sig_table = Table(sig_data, colWidths=[70 * mm, 70 * mm])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(sig_table)
    return elements

def build_declaration_page(styles, registry):
    """Sample Sheet 3: Student Declaration Layout."""
    elements = []
    elements.append(PageTracker('DECLARATION', registry))
    dec_heading = ParagraphStyle('DecHeading', fontName='Times-Bold', fontSize=17, leading=22, alignment=TA_CENTER, spaceAfter=24)
    elements.append(Paragraph("STUDENT DECLARATION", dec_heading))
    elements.append(Spacer(1, 10 * mm))

    body_style = ParagraphStyle('DecBody', fontName='Times-Roman', fontSize=12, leading=22, alignment=TA_JUSTIFY, firstLineIndent=15 * mm)
    dec_text = (
        f"I declare that this project report titled <b>\"{PROJECT_TITLE}\"</b> submitted in partial "
        f"fulfillment of the degree of B. Tech in Computer Science and Engineering is a record of original work "
        f"carried out by me under the supervision of {SUPERVISOR_FIELD}. The matter embodied in this project, in full "
        f"or in parts, has not been submitted to any other Institution or University for the award of any degree or diploma. "
        f"I also declare that the work submitted by me is entirely original, free from plagiarism, and has been "
        f"diligently checked through Turnitin software to ensure its authenticity."
    )
    elements.append(Paragraph(dec_text, body_style))
    elements.append(Spacer(1, 25 * mm))

    cand_lines = "<br/>".join([f"{c['name']}<br/>{c['enrolment']}" for c in CANDIDATES])
    dec_bottom = (
        f"&lt;Signature Lines Blank&gt;<br/><br/>"
        f"{cand_lines}<br/>"
        f"Safapora, 193504<br/>"
        f"{DATE_FIELD}"
    )
    elements.append(Paragraph(dec_bottom, styles['RunningTextNoIndent']))
    return elements

def build_acknowledgments_page(styles, registry):
    """Sample Sheet 4: Acknowledgments."""
    elements = []
    elements.append(PageTracker('ACKNOWLEDGEMENTS', registry))
    ack_heading = ParagraphStyle('AckHeading', fontName='Times-Bold', fontSize=17, leading=22, alignment=TA_CENTER, spaceAfter=24)
    elements.append(Paragraph("ACKNOWLEDGMENTS", ack_heading))
    elements.append(Spacer(1, 6 * mm))

    p1 = (
        "I take this opportunity to express our profound gratitude to our project supervisor, "
        f"{SUPERVISOR_FIELD}, {SUPERVISOR_DESIG_FIELD}, Department of Computer Science and Engineering, "
        "Govt. College Of Engineering & Technology Safapora Ganderbal J&K, for their invaluable guidance, constant encouragement, "
        "and intellectual support throughout the progression of this project."
    )
    p2 = (
        "I express our sincere gratitude to the Head of the Department, Department of Computer Science and Engineering, "
        "for providing excellent laboratory facilities, administrative assistance, and an intellectually stimulating academic atmosphere."
    )
    p3 = (
        "I extend our sincere thanks to one and all of the Govt. College Of Engineering & Technology Safapora family, "
        "including technical staff, faculty members, and fellow students, for their direct and indirect contributions toward "
        "completing this document in accordance with the official project report guidelines."
    )
    elements.append(Paragraph(p1, styles['RunningText']))
    elements.append(Paragraph(p2, styles['RunningText']))
    elements.append(Paragraph(p3, styles['RunningText']))
    elements.append(Spacer(1, 15 * mm))

    names_block = "<br/>".join([c['name'] for c in CANDIDATES])
    elements.append(Paragraph(names_block, styles['RunningTextNoIndent']))
    return elements

def build_abstract_page(styles, registry):
    """Sample Sheet 5: Abstract (Single spaced, max 300 words)."""
    elements = []
    elements.append(PageTracker('ABSTRACT', registry))
    abs_heading = ParagraphStyle('AbsHeading', fontName='Times-Bold', fontSize=17, leading=22, alignment=TA_CENTER, spaceAfter=24)
    elements.append(Paragraph("ABSTRACT", abs_heading))
    elements.append(Spacer(1, 6 * mm))
    elements.append(Paragraph(ABSTRACT_TEXT, styles['SingleSpacedText']))
    return elements

def build_toc_page(styles, read_reg, write_reg):
    """Sample Sheet 6: Table of Contents."""
    elements = []
    elements.append(PageTracker('TABLE OF CONTENTS', write_reg))
    registry = read_reg
    toc_heading = ParagraphStyle('TOCHeading', fontName='Times-Bold', fontSize=17, leading=22, alignment=TA_CENTER, spaceAfter=20)
    elements.append(Paragraph("TABLE OF CONTENTS", toc_heading))
    elements.append(Spacer(1, 4 * mm))

    # Header Row: DESCRIPTION | PAGE NUMBER
    toc_table_data = [
        [Paragraph("<b>DESCRIPTION</b>", styles['TOCItemTitleBold']), Paragraph("<b>PAGE NUMBER</b>", styles['TOCItemPageBold'])]
    ]

    prelim_items = [
        ("CERTIFICATE", registry.get('CERTIFICATE', 'iii')),
        ("DECLARATION", registry.get('DECLARATION', 'v')),
        ("ACKNOWLEDGEMENTS", registry.get('ACKNOWLEDGEMENTS', 'vii')),
        ("ABSTRACT", registry.get('ABSTRACT', 'ix')),
        ("LIST OF FIGURES", registry.get('LIST OF FIGURES', 'xv')),
        ("LIST OF TABLES", registry.get('LIST OF TABLES', 'xvii')),
        ("ABBREVIATIONS/ NOTATIONS/ NOMENCLATURE", registry.get('ABBREVIATIONS', 'xix'))
    ]

    for title, pg in prelim_items:
        toc_table_data.append([Paragraph(title, styles['TOCItemTitleBold']), Paragraph(pg, styles['TOCItemPage'])])

    # Chapters and sections
    chapter_map = [
        ("1.", "INTRODUCTION", registry.get('CH1', '1'), [
            ("1.1", "Background and Problem Statement", registry.get('CH1_1', '1')),
            ("1.2", "Business Significance and Economic Impact", registry.get('CH1_2', '3')),
            ("1.3", "Objectives of the Project", registry.get('CH1_3', '5')),
            ("1.4", "Scope and Constraints", registry.get('CH1_4', '7')),
            ("1.5", "Research Questions", registry.get('CH1_5', '8')),
            ("1.6", "Organization of the Report", registry.get('CH1_6', '9')),
        ]),
        ("2.", "LITERATURE REVIEW", registry.get('CH2', '11'), [
            ("2.1", "The Evolution of Churn Analytics in Telecommunications", registry.get('CH2_1', '11')),
            ("2.2", "Classical Statistical and Econometric Approaches", registry.get('CH2_2', '13')),
            ("2.3", "Non-Linear Machine Learning Ensembles", registry.get('CH2_3', '15')),
            ("2.4", "The Class Imbalance Challenge in Telecom Churn", registry.get('CH2_4', '17')),
            ("2.5", "Explainability and Interpretability Frameworks (XAI)", registry.get('CH2_5', '19')),
            ("2.6", "Customer Segmentation and Behavioral Clustering", registry.get('CH2_6', '21')),
            ("2.7", "Literature Summary and Identified Research Gaps", registry.get('CH2_7', '23')),
        ]),
        ("3.", "SYSTEM ANALYSIS AND DESIGN", registry.get('CH3', '25'), [
            ("3.1", "Requirements Analysis", registry.get('CH3_1', '25')),
            ("3.2", "Overall Architectural Framework", registry.get('CH3_2', '27')),
            ("3.3", "Data Processing and Pipeline Architecture", registry.get('CH3_3', '29')),
            ("3.4", "User Interface Architecture and Stepper Design", registry.get('CH3_4', '31')),
            ("3.5", "Privacy, Security, and Offline Operation Principles", registry.get('CH3_5', '33')),
            ("3.6", "Hardware and Software Environment Specifications", registry.get('CH3_6', '34')),
        ]),
        ("4.", "METHODOLOGY", registry.get('CH4', '35'), [
            ("4.1", "Dataset Characteristics and Provisional Public Source", registry.get('CH4_1', '35')),
            ("4.2", "Data Cleansing and Imputation Protocol", registry.get('CH4_2', '37')),
            ("4.3", "Feature Preprocessing and Pipeline Encapsulation", registry.get('CH4_3', '39')),
            ("4.4", "Stratified Train-Test Splitting and Leakage Prevention", registry.get('CH4_4', '41')),
            ("4.5", "Candidate Classification Algorithms", registry.get('CH4_5', '43')),
            ("4.6", "Stratified 5-Fold Cross-Validation Protocol", registry.get('CH4_6', '45')),
            ("4.7", "Model Selection and Refitting Strategy", registry.get('CH4_7', '47')),
            ("4.8", "Final Held-Out Test Set Evaluation Protocol", registry.get('CH4_8', '48')),
            ("4.9", "Mathematical Explainability: Tree-Path Attribution", registry.get('CH4_9', '49')),
            ("4.10", "Customer Segmentation Methodology", registry.get('CH4_10', '51')),
        ]),
        ("5.", "IMPLEMENTATION", registry.get('CH5', '53'), [
            ("5.1", "Project Architecture and Directory Structure", registry.get('CH5_1', '53')),
            ("5.2", "Data Cleansing and Pipeline Implementation", registry.get('CH5_2', '55')),
            ("5.3", "Automated Training and Model Serialization", registry.get('CH5_3', '57')),
            ("5.4", "Implementation of the Tree-Path Attribution Engine", registry.get('CH5_4', '59')),
            ("5.5", "Flask Web Application Framework and Endpoints", registry.get('CH5_5', '61')),
            ("5.6", "Frontend User Interface and CSS Styling", registry.get('CH5_6', '63')),
            ("5.7", "Automated Windows Launcher (START_HERE.bat)", registry.get('CH5_7', '65')),
        ]),
        ("6.", "RESULTS AND DISCUSSION", registry.get('CH6', '67'), [
            ("6.1", "Stratified 5-Fold Cross-Validation Comparison", registry.get('CH6_1', '67')),
            ("6.2", "Model Selection Rationale", registry.get('CH6_2', '69')),
            ("6.3", "Held-Out Test Partition Performance", registry.get('CH6_3', '70')),
            ("6.4", "Confusion Matrix and Error Breakdown", registry.get('CH6_4', '71')),
            ("6.5", "Transparent Discussion of Churner Recall Weakness", registry.get('CH6_5', '73')),
            ("6.6", "Receiver Operating Characteristic (ROC) Analysis", registry.get('CH6_6', '74')),
            ("6.7", "Permutation Feature Importance (Associations vs Causes)", registry.get('CH6_7', '75')),
            ("6.8", "Explainability: Row-Level Tree-Path Case Studies", registry.get('CH6_8', '77')),
            ("6.9", "Customer Segmentation Profiles and Retention Heuristics", registry.get('CH6_9', '79')),
            ("6.10", "Verification of User Interface Usability and Visual Audit", registry.get('CH6_10', '81')),
        ]),
        ("7.", "CONCLUSION AND FUTURE WORK", registry.get('CH7', '83'), [
            ("7.1", "Summary of Contributions", registry.get('CH7_1', '83')),
            ("7.2", "Key Findings and Practical Implications", registry.get('CH7_2', '85')),
            ("7.3", "System Limitations and Environmental Boundaries", registry.get('CH7_3', '86')),
            ("7.4", "Directions for Future Research", registry.get('CH7_4', '87')),
        ]),
        ("", "REFERENCES", registry.get('REFERENCES', '89'), []),
        ("Appendix A", "Data Schema and Feature Dictionary", registry.get('APP_A', '93'), []),
        ("Appendix B", "System Installation, Testing, and Verification Guide", registry.get('APP_B', '95'), []),
        ("Appendix C", "Core Pipeline and Model Selection Source Code", registry.get('APP_C', '97'), [])
    ]

    for num_prefix, title, pg, subsections in chapter_map:
        full_title = f"{num_prefix} {title}".strip()
        toc_table_data.append([Paragraph(f"<b>{full_title}</b>", styles['TOCItemTitleBold']), Paragraph(f"<b>{pg}</b>", styles['TOCItemPageBold'])])
        for s_num, s_title, s_pg in subsections:
            toc_table_data.append([Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;{s_num} {s_title}", styles['TOCItemTitle']), Paragraph(s_pg, styles['TOCItemPage'])])

    t = Table(toc_table_data, colWidths=[118 * mm, 22 * mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.0),
        ('TOPPADDING', (0, 0), (-1, -1), 1.0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(t)
    return elements

def build_list_of_figures(styles, read_reg, write_reg):
    """Sample Sheet 7: List of Figures."""
    elements = []
    elements.append(PageTracker('LIST OF FIGURES', write_reg))
    registry = read_reg
    lof_heading = ParagraphStyle('LOFHeading', fontName='Times-Bold', fontSize=17, leading=22, alignment=TA_CENTER, spaceAfter=20)
    elements.append(Paragraph("LIST OF FIGURES", lof_heading))
    elements.append(Spacer(1, 4 * mm))

    table_data = [
        [Paragraph("<b>FIGURE</b>", styles['TOCItemTitleBold']), Paragraph("<b>TITLE</b>", styles['TOCItemTitleBold']), Paragraph("<b>PAGE NUMBER</b>", styles['TOCItemPageBold'])]
    ]

    figures = [
        ("Figure 1.1", "Subscription Churn Lifecycle in Telecommunications", registry.get('FIG1_1', '2')),
        ("Figure 3.1", "Architectural Block Diagram of ChurnGuide System", registry.get('FIG3_1', '28')),
        ("Figure 3.2", "Scikit-Learn Pipeline Flow and Data Preprocessing Pipeline", registry.get('FIG3_2', '30')),
        ("Figure 3.3", "Step 1 UI - Add Customer Data and Source Selection", registry.get('FIG3_3', '32')),
        ("Figure 3.4", "Step 2 UI - Column Inspection and Target Verification", registry.get('FIG3_4', '33')),
        ("Figure 3.5", "Step 3 UI - Results Dashboard with KPI Tiles and Risk Factors", registry.get('FIG3_5', '34')),
        ("Figure 5.1", "Individual Customer Risk Evaluation with Tree-Path Attribution", registry.get('FIG5_1', '60')),
        ("Figure 5.2", "Bulk Portfolio Scoring Dashboard", registry.get('FIG5_2', '62')),
        ("Figure 6.1", "Test Confusion Matrix for Gradient Boosting Classifier", registry.get('FIG6_1', '72')),
        ("Figure 6.2", "Test Receiver Operating Characteristic (ROC) Curve", registry.get('FIG6_2', '74')),
        ("Figure 6.3", "Top General Churn Risk Factors (Permutation Importance)", registry.get('FIG6_3', '76')),
        ("Figure 6.4", "Unsupervised Customer Segments (K-Means Behavioral Clusters)", registry.get('FIG6_4', '80'))
    ]

    for num, title, pg in figures:
        table_data.append([Paragraph(num, styles['TOCItemTitleBold']), Paragraph(title, styles['TOCItemTitle']), Paragraph(pg, styles['TOCItemPage'])])

    t = Table(table_data, colWidths=[28 * mm, 90 * mm, 22 * mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(t)
    return elements

def build_list_of_tables(styles, read_reg, write_reg):
    """Sample Sheet 8: List of Tables."""
    elements = []
    elements.append(PageTracker('LIST OF TABLES', write_reg))
    registry = read_reg
    lot_heading = ParagraphStyle('LOTHeading', fontName='Times-Bold', fontSize=17, leading=22, alignment=TA_CENTER, spaceAfter=20)
    elements.append(Paragraph("LIST OF TABLES", lot_heading))
    elements.append(Spacer(1, 4 * mm))

    table_data = [
        [Paragraph("<b>TABLE</b>", styles['TOCItemTitleBold']), Paragraph("<b>TITLE</b>", styles['TOCItemTitleBold']), Paragraph("<b>PAGE NUMBER</b>", styles['TOCItemPageBold'])]
    ]

    tables_list = [
        ("Table 2.1", "Comparative Summary of Telecom Churn Prediction Literature", registry.get('TAB2_1', '24')),
        ("Table 3.1", "Hardware and Software Environment Specifications", registry.get('TAB3_1', '34')),
        ("Table 4.1", "Feature Dictionary of Provisional Telecom Churn Dataset", registry.get('TAB4_1', '36')),
        ("Table 4.2", "Missing Value Audit and Imputation Protocol (11 Blank TotalCharges)", registry.get('TAB4_2', '38')),
        ("Table 4.3", "Stratified 5-Fold Cross-Validation Hyperparameter Grid", registry.get('TAB4_3', '46')),
        ("Table 5.1", "Software Libraries and Pinned Version Specifications", registry.get('TAB5_1', '54')),
        ("Table 6.1", "Stratified 5-Fold Cross-Validation Performance Comparison", registry.get('TAB6_1', '68')),
        ("Table 6.2", "Held-Out Test Set Performance Metrics (Frozen Gradient Boosting)", registry.get('TAB6_2', '70')),
        ("Table 6.3", "Confusion Matrix Breakdown on 1,409 Held-Out Customers", registry.get('TAB6_3', '72')),
        ("Table 6.4", "Top 10 Permutation Feature Associations on Held-Out Test Set", registry.get('TAB6_4', '76')),
        ("Table 6.5", "K-Means Customer Cohort Profiles and Retention Recommendations", registry.get('TAB6_5', '79')),
        ("Table A.1", "Complete 21-Column Data Schema Specification", registry.get('TABA_1', '94'))
    ]

    for num, title, pg in tables_list:
        table_data.append([Paragraph(num, styles['TOCItemTitleBold']), Paragraph(title, styles['TOCItemTitle']), Paragraph(pg, styles['TOCItemPage'])])

    t = Table(table_data, colWidths=[28 * mm, 90 * mm, 22 * mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(t)
    return elements

def build_abbreviations_page(styles, registry):
    """Sample Sheet 9: Abbreviations/ Notations/ Nomenclature."""
    elements = []
    elements.append(PageTracker('ABBREVIATIONS', registry))
    abb_heading = ParagraphStyle('AbbHeading', fontName='Times-Bold', fontSize=17, leading=22, alignment=TA_CENTER, spaceAfter=20)
    elements.append(Paragraph("ABBREVIATIONS/ NOTATIONS/ NOMENCLATURE", abb_heading))
    elements.append(Spacer(1, 4 * mm))

    elements.append(Paragraph("<b>Technical Abbreviations</b>", styles['ReportSubsectionHeading']))
    elements.append(Spacer(1, 2 * mm))

    abb_data = []
    for abbr, full in ABBREVIATIONS:
        abb_data.append([Paragraph(f"<b>{abbr}</b>", styles['TOCItemTitleBold']), Paragraph(full, styles['TOCItemTitle'])])

    t_abb = Table(abb_data, colWidths=[30 * mm, 110 * mm])
    t_abb.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(t_abb)
    elements.append(Spacer(1, 6 * mm))

    elements.append(Paragraph("<b>Mathematical Symbols and Notations</b>", styles['ReportSubsectionHeading']))
    elements.append(Spacer(1, 2 * mm))

    not_data = []
    for sym, desc in NOTATIONS:
        not_data.append([Paragraph(f"<b>{sym}</b>", styles['TOCItemTitleBold']), Paragraph(desc, styles['TOCItemTitle'])])

    t_not = Table(not_data, colWidths=[30 * mm, 110 * mm])
    t_not.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(t_not)
    return elements

print("Preliminary pages configured successfully.")

def build_chapter_1(styles, registry):
    elements = []
    elements.append(MarkChapter1Start())
    elements.append(PageTracker('CH1', registry))
    elements.append(Paragraph("CHAPTER 1", styles['ChapterNumberHeading']))
    elements.append(Paragraph("INTRODUCTION", styles['ChapterTitleHeading']))

    for sec_title, paragraphs in CH1_SECTIONS:
        key = "CH1_" + sec_title.split()[0].replace('.', '_')
        elements.append(PageTracker(key, registry))
        elements.append(Paragraph(sec_title, styles['ReportSectionHeading']))
        for i, p in enumerate(paragraphs):
            style = styles['RunningTextNoIndent'] if i == 0 else styles['RunningText']
            elements.append(Paragraph(p, style))

        if "1.1" in sec_title:
            elements.append(Spacer(1, 2.5 * mm))
            fig_path = os.path.join('report', 'fig1_churn_lifecycle.png')
            if os.path.exists(fig_path):
                elements.append(Image(fig_path, width=130 * mm, height=45 * mm))
                elements.append(PageTracker('FIG1_1', registry))
                elements.append(Paragraph("Figure 1.1: Subscription Churn Lifecycle in Telecommunications", styles['ReportFigureCaption']))
                elements.append(Spacer(1, 2.5 * mm))

    return elements

def build_chapter_2(styles, registry):
    elements = []
    elements.append(PageTracker('CH2', registry))
    elements.append(Paragraph("CHAPTER 2", styles['ChapterNumberHeading']))
    elements.append(Paragraph("LITERATURE REVIEW", styles['ChapterTitleHeading']))

    for sec_title, paragraphs in CH2_SECTIONS:
        key = "CH2_" + sec_title.split()[0].replace('.', '_')
        elements.append(PageTracker(key, registry))
        elements.append(Paragraph(sec_title, styles['ReportSectionHeading']))
        for i, p in enumerate(paragraphs):
            style = styles['RunningTextNoIndent'] if i == 0 else styles['RunningText']
            elements.append(Paragraph(p, style))

    # Table 2.1: Literature Comparison
    elements.append(Spacer(1, 4 * mm))
    elements.append(PageTracker('TAB2_1', registry))
    elements.append(Paragraph("Table 2.1: Comparative Summary of Telecom Churn Prediction Literature", styles['ReportTableCaption']))
    lit_data = [
        [Paragraph("<b>Author(s) & Year</b>", styles['TOCItemTitleBold']),
         Paragraph("<b>Algorithms Evaluated</b>", styles['TOCItemTitleBold']),
         Paragraph("<b>Primary Metric</b>", styles['TOCItemTitleBold']),
         Paragraph("<b>Key Findings & Limitations</b>", styles['TOCItemTitleBold'])],
        [Paragraph("Vafeiadis et al. (2015) [14]", styles['TOCItemTitle']),
         Paragraph("SVM, ANN, Decision Tree, Naive Bayes, Logistic Regression", styles['TOCItemTitle']),
         Paragraph("Accuracy, F-Measure", styles['TOCItemTitle']),
         Paragraph("SVM achieved superior accuracy (86.1%); lacked modern boosting ensembles.", styles['TOCItemTitle'])],
        [Paragraph("Ahmad et al. (2019) [1]", styles['TOCItemTitle']),
         Paragraph("XGBoost, Random Forest, Decision Tree", styles['TOCItemTitle']),
         Paragraph("ROC-AUC, Precision, Recall", styles['TOCItemTitle']),
         Paragraph("Tree ensembles outperformed linear models; lacked row-level explainability.", styles['TOCItemTitle'])],
        [Paragraph("Burez & Van den Poel (2009) [4]", styles['TOCItemTitle']),
         Paragraph("Random Forest, Gradient Boosting, Logistic Regression", styles['TOCItemTitle']),
         Paragraph("ROC-AUC, Lift", styles['TOCItemTitle']),
         Paragraph("SMOTE distorted posterior probabilities; recommended ROC-AUC under class imbalance.", styles['TOCItemTitle'])],
        [Paragraph("De Caigny et al. (2018) [6]", styles['TOCItemTitle']),
         Paragraph("Hybrid Decision Tree & Logistic Regression (Logit Leaf)", styles['TOCItemTitle']),
         Paragraph("ROC-AUC, Expected Maximum Profit (EMP)", styles['TOCItemTitle']),
         Paragraph("Segment-specific linear models enhanced interpretability.", styles['TOCItemTitle'])],
        [Paragraph("Lalwani et al. (2022) [9]", styles['TOCItemTitle']),
         Paragraph("AdaBoost, Random Forest, Extra Trees, XGBoost", styles['TOCItemTitle']),
         Paragraph("Accuracy, Recall", styles['TOCItemTitle']),
         Paragraph("Ensemble methods yielded highest accuracy; opaque deployment.", styles['TOCItemTitle'])]
    ]
    t_lit = Table(lit_data, colWidths=[32 * mm, 38 * mm, 24 * mm, 46 * mm])
    t_lit.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(t_lit)
    elements.append(Spacer(1, 4 * mm))

    return elements

def build_chapter_3(styles, registry):
    elements = []
    elements.append(PageTracker('CH3', registry))
    elements.append(Paragraph("CHAPTER 3", styles['ChapterNumberHeading']))
    elements.append(Paragraph("SYSTEM ANALYSIS AND DESIGN", styles['ChapterTitleHeading']))

    for sec_title, paragraphs in CH3_SECTIONS:
        key = "CH3_" + sec_title.split()[0].replace('.', '_')
        elements.append(PageTracker(key, registry))
        elements.append(Paragraph(sec_title, styles['ReportSectionHeading']))
        for i, p in enumerate(paragraphs):
            style = styles['RunningTextNoIndent'] if i == 0 else styles['RunningText']
            elements.append(Paragraph(p, style))

        if "3.2" in sec_title:
            fig_path = os.path.join('report', 'fig3_system_architecture.png')
            if os.path.exists(fig_path):
                elements.append(Spacer(1, 2 * mm))
                elements.append(Image(fig_path, width=125 * mm, height=40 * mm))
                elements.append(PageTracker('FIG3_1', registry))
                elements.append(Paragraph("Figure 3.1: Architectural Block Diagram of ChurnGuide System", styles['ReportFigureCaption']))
                elements.append(Spacer(1, 2 * mm))

        if "3.3" in sec_title:
            fig_path = os.path.join('report', 'fig3_pipeline_architecture.png')
            if os.path.exists(fig_path):
                elements.append(Spacer(1, 2 * mm))
                elements.append(Image(fig_path, width=125 * mm, height=38 * mm))
                elements.append(PageTracker('FIG3_2', registry))
                elements.append(Paragraph("Figure 3.2: Scikit-Learn Pipeline Flow and Data Preprocessing Pipeline", styles['ReportFigureCaption']))
                elements.append(Spacer(1, 2 * mm))

        if "3.4" in sec_title:
            # Screenshots for 3.3, 3.4, 3.5
            s1 = os.path.join('static', 'screenshots', 'step1_add_data.png')
            s2 = os.path.join('static', 'screenshots', 'step2_check_columns.png')
            s3 = os.path.join('static', 'screenshots', 'step3_see_results.png')
            if os.path.exists(s1):
                elements.append(Spacer(1, 1.5 * mm))
                elements.append(Image(s1, width=105 * mm, height=36 * mm))
                elements.append(PageTracker('FIG3_3', registry))
                elements.append(Paragraph("Figure 3.3: Step 1 UI - Add Customer Data and Source Selection", styles['ReportFigureCaption']))
                elements.append(Spacer(1, 1.5 * mm))
            if os.path.exists(s2):
                elements.append(Spacer(1, 1.5 * mm))
                elements.append(Image(s2, width=105 * mm, height=36 * mm))
                elements.append(PageTracker('FIG3_4', registry))
                elements.append(Paragraph("Figure 3.4: Step 2 UI - Column Inspection and Target Verification", styles['ReportFigureCaption']))
                elements.append(Spacer(1, 1.5 * mm))
            if os.path.exists(s3):
                elements.append(Spacer(1, 1.5 * mm))
                elements.append(Image(s3, width=105 * mm, height=36 * mm))
                elements.append(PageTracker('FIG3_5', registry))
                elements.append(Paragraph("Figure 3.5: Step 3 UI - Results Dashboard with KPI Tiles and Risk Factors", styles['ReportFigureCaption']))
                elements.append(Spacer(1, 1.5 * mm))

        if "3.6" in sec_title:
            elements.append(Spacer(1, 4 * mm))
            elements.append(PageTracker('TAB3_1', registry))
            elements.append(Paragraph("Table 3.1: Hardware and Software Environment Specifications", styles['ReportTableCaption']))
            env_data = [
                [Paragraph("<b>Component</b>", styles['TOCItemTitleBold']), Paragraph("<b>Specification & Version</b>", styles['TOCItemTitleBold'])],
                [Paragraph("Processor (CPU)", styles['TOCItemTitle']), Paragraph("Intel Core i7-13700H / AMD Ryzen 7 (x86_64)", styles['TOCItemTitle'])],
                [Paragraph("System Memory (RAM)", styles['TOCItemTitle']), Paragraph("16.0 GB DDR5 RAM", styles['TOCItemTitle'])],
                [Paragraph("Operating System", styles['TOCItemTitle']), Paragraph("Microsoft Windows 11 Home 64-bit", styles['TOCItemTitle'])],
                [Paragraph("Python Environment", styles['TOCItemTitle']), Paragraph("CPython 3.13.7 (Standard 64-bit)", styles['TOCItemTitle'])],
                [Paragraph("Machine Learning Engine", styles['TOCItemTitle']), Paragraph("scikit-learn 1.8.0 (Pipeline, ColumnTransformer)", styles['TOCItemTitle'])],
                [Paragraph("Web Application Framework", styles['TOCItemTitle']), Paragraph("Flask 3.1.2 (WSGI Loopback Server)", styles['TOCItemTitle'])],
                [Paragraph("Automated Testing Tool", styles['TOCItemTitle']), Paragraph("pytest 9.1.1 (15 Automated Unit Tests)", styles['TOCItemTitle'])],
                [Paragraph("Report Compiler", styles['TOCItemTitle']), Paragraph("ReportLab 4.4.10 & PyMuPDF 1.26.7", styles['TOCItemTitle'])]
            ]
            t_env = Table(env_data, colWidths=[50 * mm, 90 * mm])
            t_env.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 2.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
            ]))
            elements.append(t_env)
            elements.append(Spacer(1, 4 * mm))

    return elements

def build_chapter_4(styles, registry):
    elements = []
    elements.append(PageTracker('CH4', registry))
    elements.append(Paragraph("CHAPTER 4", styles['ChapterNumberHeading']))
    elements.append(Paragraph("METHODOLOGY", styles['ChapterTitleHeading']))

    for sec_title, paragraphs in CH4_SECTIONS:
        key = "CH4_" + sec_title.split()[0].replace('.', '_')
        elements.append(PageTracker(key, registry))
        elements.append(Paragraph(sec_title, styles['ReportSectionHeading']))
        for i, p in enumerate(paragraphs):
            style = styles['RunningTextNoIndent'] if i == 0 else styles['RunningText']
            elements.append(Paragraph(p, style))

        if "4.1" in sec_title:
            elements.append(Spacer(1, 4 * mm))
            elements.append(PageTracker('TAB4_1', registry))
            elements.append(Paragraph("Table 4.1: Feature Dictionary of Provisional Telecom Churn Dataset", styles['ReportTableCaption']))
            feat_data = [
                [Paragraph("<b>Category</b>", styles['TOCItemTitleBold']),
                 Paragraph("<b>Feature Column(s)</b>", styles['TOCItemTitleBold']),
                 Paragraph("<b>Data Type</b>", styles['TOCItemTitleBold']),
                 Paragraph("<b>Domain Values / Description</b>", styles['TOCItemTitleBold'])],
                [Paragraph("Demographic", styles['TOCItemTitle']),
                 Paragraph("gender, SeniorCitizen, Partner, Dependents", styles['TOCItemTitle']),
                 Paragraph("Categorical", styles['TOCItemTitle']),
                 Paragraph("Male/Female, 0/1, Yes/No marital status, Yes/No dependents", styles['TOCItemTitle'])],
                [Paragraph("Services", styles['TOCItemTitle']),
                 Paragraph("PhoneService, MultipleLines, InternetService", styles['TOCItemTitle']),
                 Paragraph("Categorical", styles['TOCItemTitle']),
                 Paragraph("Voice service, line counts, DSL / Fiber optic / None", styles['TOCItemTitle'])],
                [Paragraph("Value-Added", styles['TOCItemTitle']),
                 Paragraph("OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies", styles['TOCItemTitle']),
                 Paragraph("Categorical", styles['TOCItemTitle']),
                 Paragraph("Yes, No, No internet service (6 auxiliary digital services)", styles['TOCItemTitle'])],
                [Paragraph("Account Details", styles['TOCItemTitle']),
                 Paragraph("tenure, Contract, PaperlessBilling, PaymentMethod", styles['TOCItemTitle']),
                 Paragraph("Integer & Categorical", styles['TOCItemTitle']),
                 Paragraph("0-72 months; Month-to-month, 1yr, 2yr; Electronic/Mailed check, Auto Bank/Card", styles['TOCItemTitle'])],
                [Paragraph("Financial", styles['TOCItemTitle']),
                 Paragraph("MonthlyCharges, TotalCharges", styles['TOCItemTitle']),
                 Paragraph("Continuous Float", styles['TOCItemTitle']),
                 Paragraph("Current monthly billing rate ($); Cumulative lifetime spend ($)", styles['TOCItemTitle'])],
                [Paragraph("Target", styles['TOCItemTitle']),
                 Paragraph("Churn", styles['TOCItemTitle']),
                 Paragraph("Binary (Target)", styles['TOCItemTitle']),
                 Paragraph("Yes (Churned, 26.54%), No (Retained, 73.46%)", styles['TOCItemTitle'])]
            ]
            t_feat = Table(feat_data, colWidths=[24 * mm, 38 * mm, 24 * mm, 54 * mm])
            t_feat.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 2.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
            ]))
            elements.append(t_feat)
            elements.append(Spacer(1, 4 * mm))

        if "4.2" in sec_title:
            elements.append(Spacer(1, 4 * mm))
            elements.append(PageTracker('TAB4_2', registry))
            elements.append(Paragraph("Table 4.2: Missing Value Audit and Imputation Protocol (11 Blank TotalCharges)", styles['ReportTableCaption']))
            miss_data = [
                [Paragraph("<b>Attribute</b>", styles['TOCItemTitleBold']), Paragraph("<b>Raw Value</b>", styles['TOCItemTitleBold']), Paragraph("<b>Tenure</b>", styles['TOCItemTitleBold']), Paragraph("<b>Imputed Value</b>", styles['TOCItemTitleBold']), Paragraph("<b>Operational Rationale</b>", styles['TOCItemTitleBold'])],
                [Paragraph("TotalCharges (11 records)", styles['TOCItemTitle']),
                 Paragraph("' ' (whitespace string)", styles['TOCItemTitle']),
                 Paragraph("0 months", styles['TOCItemTitle']),
                 Paragraph("$1,400.85 (Training Median)", styles['TOCItemTitle']),
                 Paragraph("Brand new subscribers who joined during current billing cycle. Median imputation preserves distribution without introducing outliers.", styles['TOCItemTitle'])]
            ]
            t_miss = Table(miss_data, colWidths=[32 * mm, 26 * mm, 18 * mm, 26 * mm, 38 * mm])
            t_miss.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 2.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
            ]))
            elements.append(t_miss)
            elements.append(Spacer(1, 4 * mm))

        if "4.6" in sec_title:
            elements.append(Spacer(1, 4 * mm))
            elements.append(PageTracker('TAB4_3', registry))
            elements.append(Paragraph("Table 4.3: Stratified 5-Fold Cross-Validation Hyperparameter Grid", styles['ReportTableCaption']))
            grid_data = [
                [Paragraph("<b>Candidate Algorithm</b>", styles['TOCItemTitleBold']), Paragraph("<b>Hyperparameter Grid Evaluated</b>", styles['TOCItemTitleBold']), Paragraph("<b>Selection Metric</b>", styles['TOCItemTitleBold'])],
                [Paragraph("Logistic Regression", styles['TOCItemTitle']), Paragraph("C in {0.01, 0.1, 1.0, 10.0}, max_iter = 1000, L2 penalty", styles['TOCItemTitle']), Paragraph("Mean CV ROC-AUC", styles['TOCItemTitle'])],
                [Paragraph("Random Forest Classifier", styles['TOCItemTitle']), Paragraph("n_estimators in {50, 100}, max_depth in {5, 10}", styles['TOCItemTitle']), Paragraph("Mean CV ROC-AUC", styles['TOCItemTitle'])],
                [Paragraph("Gradient Boosting Classifier", styles['TOCItemTitle']), Paragraph("learning_rate in {0.05, 0.1}, max_depth in {3, 4}, n_estimators in {50, 100}", styles['TOCItemTitle']), Paragraph("Mean CV ROC-AUC", styles['TOCItemTitle'])]
            ]
            t_grid = Table(grid_data, colWidths=[42 * mm, 68 * mm, 30 * mm])
            t_grid.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 2.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
            ]))
            elements.append(t_grid)
            elements.append(Spacer(1, 4 * mm))

    return elements

def build_chapter_5(styles, registry):
    elements = []
    elements.append(PageTracker('CH5', registry))
    elements.append(Paragraph("CHAPTER 5", styles['ChapterNumberHeading']))
    elements.append(Paragraph("IMPLEMENTATION", styles['ChapterTitleHeading']))

    for sec_title, paragraphs in CH5_SECTIONS:
        key = "CH5_" + sec_title.split()[0].replace('.', '_')
        elements.append(PageTracker(key, registry))
        elements.append(Paragraph(sec_title, styles['ReportSectionHeading']))
        for i, p in enumerate(paragraphs):
            style = styles['RunningTextNoIndent'] if i == 0 else styles['RunningText']
            elements.append(Paragraph(p, style))

        if "5.1" in sec_title:
            elements.append(Spacer(1, 4 * mm))
            elements.append(PageTracker('TAB5_1', registry))
            elements.append(Paragraph("Table 5.1: Software Libraries and Pinned Version Specifications", styles['ReportTableCaption']))
            pkg_data = [
                [Paragraph("<b>Package Name</b>", styles['TOCItemTitleBold']), Paragraph("<b>Pinned Version</b>", styles['TOCItemTitleBold']), Paragraph("<b>Role in Architecture</b>", styles['TOCItemTitleBold'])],
                [Paragraph("scikit-learn", styles['TOCItemTitle']), Paragraph("1.8.0", styles['TOCItemTitle']), Paragraph("ColumnTransformer, Gradient Boosting, Cross-Validation, Metrics", styles['TOCItemTitle'])],
                [Paragraph("pandas", styles['TOCItemTitle']), Paragraph("2.3.3", styles['TOCItemTitle']), Paragraph("Tabular data manipulation, schema validation, CSV parsing", styles['TOCItemTitle'])],
                [Paragraph("flask", styles['TOCItemTitle']), Paragraph("3.1.2", styles['TOCItemTitle']), Paragraph("Local WSGI web application server, routing, Jinja2 templating", styles['TOCItemTitle'])],
                [Paragraph("joblib", styles['TOCItemTitle']), Paragraph("1.5.3", styles['TOCItemTitle']), Paragraph("Pipeline serialization and artifact persistence", styles['TOCItemTitle'])],
                [Paragraph("matplotlib", styles['TOCItemTitle']), Paragraph("3.10.7", styles['TOCItemTitle']), Paragraph("High-resolution diagnostic plotting (Confusion matrix, ROC, importance)", styles['TOCItemTitle'])],
                [Paragraph("pytest", styles['TOCItemTitle']), Paragraph("9.1.1", styles['TOCItemTitle']), Paragraph("Automated unit testing suite (15 assertions)", styles['TOCItemTitle'])],
                [Paragraph("reportlab", styles['TOCItemTitle']), Paragraph("4.4.10", styles['TOCItemTitle']), Paragraph("PDF report generation engine adhering to GCET guidelines", styles['TOCItemTitle'])]
            ]
            t_pkg = Table(pkg_data, colWidths=[36 * mm, 30 * mm, 74 * mm])
            t_pkg.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 2.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
            ]))
            elements.append(t_pkg)
            elements.append(Spacer(1, 4 * mm))

        if "5.4" in sec_title:
            s_pred = os.path.join('static', 'screenshots', 'predict_single.png')
            if os.path.exists(s_pred):
                elements.append(Spacer(1, 2 * mm))
                elements.append(Image(s_pred, width=115 * mm, height=45 * mm))
                elements.append(PageTracker('FIG5_1', registry))
                elements.append(Paragraph("Figure 5.1: Individual Customer Risk Evaluation with Tree-Path Attribution", styles['ReportFigureCaption']))
                elements.append(Spacer(1, 2 * mm))

        if "5.5" in sec_title:
            s_bulk = os.path.join('static', 'screenshots', 'bulk_scoring_demo.png')
            if os.path.exists(s_bulk):
                elements.append(Spacer(1, 2 * mm))
                elements.append(Image(s_bulk, width=115 * mm, height=45 * mm))
                elements.append(PageTracker('FIG5_2', registry))
                elements.append(Paragraph("Figure 5.2: Bulk Portfolio Scoring Dashboard", styles['ReportFigureCaption']))
                elements.append(Spacer(1, 2 * mm))

    return elements

def build_chapter_6(styles, registry):
    elements = []
    elements.append(PageTracker('CH6', registry))
    elements.append(Paragraph("CHAPTER 6", styles['ChapterNumberHeading']))
    elements.append(Paragraph("RESULTS AND DISCUSSION", styles['ChapterTitleHeading']))

    for sec_title, paragraphs in CH6_SECTIONS:
        key = "CH6_" + sec_title.split()[0].replace('.', '_')
        elements.append(PageTracker(key, registry))
        elements.append(Paragraph(sec_title, styles['ReportSectionHeading']))
        for i, p in enumerate(paragraphs):
            style = styles['RunningTextNoIndent'] if i == 0 else styles['RunningText']
            elements.append(Paragraph(p, style))

        if "6.1" in sec_title:
            elements.append(Spacer(1, 4 * mm))
            elements.append(PageTracker('TAB6_1', registry))
            elements.append(Paragraph("Table 6.1: Stratified 5-Fold Cross-Validation Performance Comparison", styles['ReportTableCaption']))
            cv_table_data = [
                [Paragraph("<b>Classification Algorithm</b>", styles['TOCItemTitleBold']),
                 Paragraph("<b>Optimal Hyperparameters</b>", styles['TOCItemTitleBold']),
                 Paragraph("<b>Mean CV ROC-AUC</b>", styles['TOCItemTitleBold']),
                 Paragraph("<b>Fold Std. Dev.</b>", styles['TOCItemTitleBold']),
                 Paragraph("<b>Status</b>", styles['TOCItemTitleBold'])],
                [Paragraph("Logistic Regression", styles['TOCItemTitle']),
                 Paragraph("C = 10.0, max_iter = 1000", styles['TOCItemTitle']),
                 Paragraph("0.8463", styles['TOCItemTitleBold']),
                 Paragraph("&plusmn; 0.0128", styles['TOCItemTitle']),
                 Paragraph("Evaluated", styles['TOCItemTitle'])],
                [Paragraph("Random Forest", styles['TOCItemTitle']),
                 Paragraph("n_estimators = 50, max_depth = 5", styles['TOCItemTitle']),
                 Paragraph("0.8446", styles['TOCItemTitleBold']),
                 Paragraph("&plusmn; 0.0115", styles['TOCItemTitle']),
                 Paragraph("Evaluated", styles['TOCItemTitle'])],
                [Paragraph("<b>Gradient Boosting</b>", styles['TOCItemTitleBold']),
                 Paragraph("<b>learning_rate = 0.05, max_depth = 3, n_est = 100</b>", styles['TOCItemTitleBold']),
                 Paragraph("<b>0.8493</b>", styles['TOCItemTitleBold']),
                 Paragraph("<b>&plusmn; 0.0129</b>", styles['TOCItemTitleBold']),
                 Paragraph("<b>WINNER (Selected)</b>", styles['TOCItemTitleBold'])]
            ]
            t_cv = Table(cv_table_data, colWidths=[36 * mm, 46 * mm, 22 * mm, 18 * mm, 18 * mm])
            t_cv.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#f0fdf4')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 1.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
            ]))
            elements.append(t_cv)
            elements.append(Spacer(1, 2 * mm))

        if "6.3" in sec_title:
            elements.append(Spacer(1, 2 * mm))
            elements.append(PageTracker('TAB6_2', registry))
            elements.append(Paragraph("Table 6.2: Held-Out Test Set Performance Metrics (Frozen Gradient Boosting)", styles['ReportTableCaption']))
            test_metric_data = [
                [Paragraph("<b>Evaluation Metric</b>", styles['TOCItemTitleBold']), Paragraph("<b>Empirical Value (1,409 Test Rows)</b>", styles['TOCItemTitleBold']), Paragraph("<b>Interpretation</b>", styles['TOCItemTitleBold'])],
                [Paragraph("Test Accuracy", styles['TOCItemTitle']), Paragraph("<b>0.7984 (79.84%)</b>", styles['TOCItemTitleBold']), Paragraph("Fraction of overall correct predictions (TN + TP) / Total", styles['TOCItemTitle'])],
                [Paragraph("Test Precision", styles['TOCItemTitle']), Paragraph("<b>0.6585 (65.85%)</b>", styles['TOCItemTitleBold']), Paragraph("Accuracy of positive churn alarms: TP / (TP + FP)", styles['TOCItemTitle'])],
                [Paragraph("Test Recall (Sensitivity)", styles['TOCItemTitle']), Paragraph("<b>0.5000 (50.00%)</b>", styles['TOCItemTitleBold']), Paragraph("Capture rate of true churners: TP / (TP + FN) [Weaker metric]", styles['TOCItemTitle'])],
                [Paragraph("Test F1-Score", styles['TOCItemTitle']), Paragraph("<b>0.5684</b>", styles['TOCItemTitleBold']), Paragraph("Harmonic mean of precision and recall", styles['TOCItemTitle'])],
                [Paragraph("Test ROC-AUC", styles['TOCItemTitle']), Paragraph("<b>0.8465</b>", styles['TOCItemTitleBold']), Paragraph("Threshold-independent discriminative ability", styles['TOCItemTitle'])]
            ]
            t_m = Table(test_metric_data, colWidths=[42 * mm, 38 * mm, 60 * mm])
            t_m.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 1.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
            ]))
            elements.append(t_m)
            elements.append(Spacer(1, 2 * mm))

        if "6.4" in sec_title:
            elements.append(Spacer(1, 2 * mm))
            elements.append(PageTracker('TAB6_3', registry))
            elements.append(Paragraph("Table 6.3: Confusion Matrix Breakdown on 1,409 Held-Out Customers", styles['ReportTableCaption']))
            cm_data = [
                [Paragraph("<b>Actual Class \\ Predicted</b>", styles['TOCItemTitleBold']), Paragraph("<b>Predicted Retained (No)</b>", styles['TOCItemTitleBold']), Paragraph("<b>Predicted Churned (Yes)</b>", styles['TOCItemTitleBold']), Paragraph("<b>Total Actual</b>", styles['TOCItemTitleBold'])],
                [Paragraph("<b>Actual Retained (No)</b>", styles['TOCItemTitleBold']), Paragraph("938 (True Negative, 66.57%)", styles['TOCItemTitle']), Paragraph("97 (False Positive, 6.88%)", styles['TOCItemTitle']), Paragraph("1,035 (73.46%)", styles['TOCItemTitle'])],
                [Paragraph("<b>Actual Churned (Yes)</b>", styles['TOCItemTitleBold']), Paragraph("187 (False Negative, 13.27%)", styles['TOCItemTitle']), Paragraph("187 (True Positive, 13.27%)", styles['TOCItemTitle']), Paragraph("374 (26.54%)", styles['TOCItemTitle'])],
                [Paragraph("<b>Total Predicted</b>", styles['TOCItemTitleBold']), Paragraph("1,125 (79.84%)", styles['TOCItemTitleBold']), Paragraph("284 (20.16%)", styles['TOCItemTitleBold']), Paragraph("1,409 (100.0%)", styles['TOCItemTitleBold'])]
            ]
            t_cm = Table(cm_data, colWidths=[38 * mm, 38 * mm, 38 * mm, 26 * mm])
            t_cm.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 1.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
            ]))
            elements.append(t_cm)
            elements.append(Spacer(1, 4 * mm))

            cm_img = os.path.join('static', 'img', 'confusion_matrix.png')
            if os.path.exists(cm_img):
                elements.append(Spacer(1, 1.5 * mm))
                elements.append(Image(cm_img, width=80 * mm, height=42 * mm))
                elements.append(PageTracker('FIG6_1', registry))
                elements.append(Paragraph("Figure 6.1: Test Confusion Matrix for Gradient Boosting Classifier", styles['ReportFigureCaption']))
                elements.append(Spacer(1, 1.5 * mm))

        if "6.6" in sec_title:
            roc_img = os.path.join('static', 'img', 'roc_curve.png')
            if os.path.exists(roc_img):
                elements.append(Spacer(1, 1.5 * mm))
                elements.append(Image(roc_img, width=80 * mm, height=42 * mm))
                elements.append(PageTracker('FIG6_2', registry))
                elements.append(Paragraph("Figure 6.2: Test Receiver Operating Characteristic (ROC) Curve", styles['ReportFigureCaption']))
                elements.append(Spacer(1, 1.5 * mm))

        if "6.7" in sec_title:
            elements.append(Spacer(1, 2 * mm))
            elements.append(PageTracker('TAB6_4', registry))
            elements.append(Paragraph("Table 6.4: Top 10 Permutation Feature Associations on Held-Out Test Set", styles['ReportTableCaption']))
            perm_data = [
                [Paragraph("<b>Rank</b>", styles['TOCItemTitleBold']), Paragraph("<b>Feature Column</b>", styles['TOCItemTitleBold']), Paragraph("<b>Mean AUC Decrease</b>", styles['TOCItemTitleBold']), Paragraph("<b>Std. Error</b>", styles['TOCItemTitleBold'])],
                [Paragraph("1", styles['TOCItemTitle']), Paragraph("tenure", styles['TOCItemTitleBold']), Paragraph("0.07385", styles['TOCItemTitleBold']), Paragraph("&plusmn; 0.00338", styles['TOCItemTitle'])],
                [Paragraph("2", styles['TOCItemTitle']), Paragraph("Contract", styles['TOCItemTitleBold']), Paragraph("0.04300", styles['TOCItemTitleBold']), Paragraph("&plusmn; 0.00442", styles['TOCItemTitle'])],
                [Paragraph("3", styles['TOCItemTitle']), Paragraph("InternetService", styles['TOCItemTitleBold']), Paragraph("0.02886", styles['TOCItemTitleBold']), Paragraph("&plusmn; 0.00671", styles['TOCItemTitle'])],
                [Paragraph("4", styles['TOCItemTitle']), Paragraph("PaymentMethod", styles['TOCItemTitle']), Paragraph("0.00483", styles['TOCItemTitle']), Paragraph("&plusmn; 0.00146", styles['TOCItemTitle'])],
                [Paragraph("5", styles['TOCItemTitle']), Paragraph("StreamingMovies", styles['TOCItemTitle']), Paragraph("0.00389", styles['TOCItemTitle']), Paragraph("&plusmn; 0.00118", styles['TOCItemTitle'])],
                [Paragraph("6", styles['TOCItemTitle']), Paragraph("TotalCharges", styles['TOCItemTitle']), Paragraph("0.00279", styles['TOCItemTitle']), Paragraph("&plusmn; 0.00104", styles['TOCItemTitle'])],
                [Paragraph("7", styles['TOCItemTitle']), Paragraph("PaperlessBilling", styles['TOCItemTitle']), Paragraph("0.00224", styles['TOCItemTitle']), Paragraph("&plusmn; 0.00130", styles['TOCItemTitle'])],
                [Paragraph("8", styles['TOCItemTitle']), Paragraph("SeniorCitizen", styles['TOCItemTitle']), Paragraph("0.00209", styles['TOCItemTitle']), Paragraph("&plusmn; 0.00069", styles['TOCItemTitle'])],
                [Paragraph("9", styles['TOCItemTitle']), Paragraph("TechSupport", styles['TOCItemTitle']), Paragraph("0.00203", styles['TOCItemTitle']), Paragraph("&plusmn; 0.00147", styles['TOCItemTitle'])],
                [Paragraph("10", styles['TOCItemTitle']), Paragraph("OnlineSecurity", styles['TOCItemTitle']), Paragraph("0.00201", styles['TOCItemTitle']), Paragraph("&plusmn; 0.00083", styles['TOCItemTitle'])]
            ]
            t_perm = Table(perm_data, colWidths=[15 * mm, 45 * mm, 40 * mm, 40 * mm])
            t_perm.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 1.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
            ]))
            elements.append(t_perm)
            elements.append(Spacer(1, 2 * mm))

            fi_img = os.path.join('static', 'img', 'feature_importance.png')
            if os.path.exists(fi_img):
                elements.append(Spacer(1, 1.5 * mm))
                elements.append(Image(fi_img, width=90 * mm, height=42 * mm))
                elements.append(PageTracker('FIG6_3', registry))
                elements.append(Paragraph("Figure 6.3: Top General Churn Risk Factors (Permutation Importance)", styles['ReportFigureCaption']))
                elements.append(Spacer(1, 1.5 * mm))

        if "6.9" in sec_title:
            elements.append(Spacer(1, 2 * mm))
            elements.append(PageTracker('TAB6_5', registry))
            elements.append(Paragraph("Table 6.5: K-Means Customer Cohort Profiles and Retention Recommendations", styles['ReportTableCaption']))
            seg_data = [
                [Paragraph("<b>Cluster & Persona</b>", styles['TOCItemTitleBold']),
                 Paragraph("<b>Count (%)</b>", styles['TOCItemTitleBold']),
                 Paragraph("<b>Tenure</b>", styles['TOCItemTitleBold']),
                 Paragraph("<b>Monthly</b>", styles['TOCItemTitleBold']),
                 Paragraph("<b>Churn %</b>", styles['TOCItemTitleBold']),
                 Paragraph("<b>Tailored Action Strategy</b>", styles['TOCItemTitleBold'])],
                [Paragraph("<b>Cluster 1</b><br/>Loyal Long-Term Low-Usage", styles['TOCItemTitle']),
                 Paragraph("1,159 (16.5%)", styles['TOCItemTitle']),
                 Paragraph("53.6 mos", styles['TOCItemTitle']),
                 Paragraph("$34.92", styles['TOCItemTitle']),
                 Paragraph("5.0%", styles['TOCItemTitleBold']),
                 Paragraph("Appreciation discounts, stable rate guarantee, simplified billing.", styles['TOCItemTitle'])],
                [Paragraph("<b>Cluster 2</b><br/>High-Value Loyal Power Users", styles['TOCItemTitle']),
                 Paragraph("1,904 (27.0%)", styles['TOCItemTitle']),
                 Paragraph("59.5 mos", styles['TOCItemTitle']),
                 Paragraph("$93.31", styles['TOCItemTitle']),
                 Paragraph("15.4%", styles['TOCItemTitle']),
                 Paragraph("VIP loyalty rewards, priority fiber routing, annual renewal bonus.", styles['TOCItemTitle'])],
                [Paragraph("<b>Cluster 3</b><br/>New Budget & Voice-Only", styles['TOCItemTitle']),
                 Paragraph("1,704 (24.2%)", styles['TOCItemTitle']),
                 Paragraph("10.2 mos", styles['TOCItemTitle']),
                 Paragraph("$31.77", styles['TOCItemTitle']),
                 Paragraph("24.6%", styles['TOCItemTitle']),
                 Paragraph("Affordable family plan bundles, flexible payment reminders, zero-fee billing.", styles['TOCItemTitle'])],
                [Paragraph("<b>Cluster 4</b><br/>Critical Churn Risk - High-Cost", styles['TOCItemTitleBold']),
                 Paragraph("2,276 (32.3%)", styles['TOCItemTitleBold']),
                 Paragraph("15.4 mos", styles['TOCItemTitleBold']),
                 Paragraph("$80.78", styles['TOCItemTitleBold']),
                 Paragraph("<b>48.2%</b>", styles['TOCItemTitleBold']),
                 Paragraph("Immediate 90-day onboarding assistance, tech checkup, 15% contract discount.", styles['TOCItemTitleBold'])]
            ]
            t_seg = Table(seg_data, colWidths=[30 * mm, 18 * mm, 16 * mm, 16 * mm, 14 * mm, 46 * mm])
            t_seg.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#fee2e2')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 1.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
            ]))
            elements.append(t_seg)
            elements.append(Spacer(1, 2 * mm))

            s_seg = os.path.join('static', 'screenshots', 'segments_view.png')
            if os.path.exists(s_seg):
                elements.append(Spacer(1, 1.5 * mm))
                elements.append(Image(s_seg, width=105 * mm, height=38 * mm))
                elements.append(PageTracker('FIG6_4', registry))
                elements.append(Paragraph("Figure 6.4: Unsupervised Customer Segments (K-Means Behavioral Clusters)", styles['ReportFigureCaption']))
                elements.append(Spacer(1, 1.5 * mm))

    return elements

def build_chapter_7(styles, registry):
    elements = []
    elements.append(PageTracker('CH7', registry))
    elements.append(Paragraph("CHAPTER 7", styles['ChapterNumberHeading']))
    elements.append(Paragraph("CONCLUSION AND FUTURE WORK", styles['ChapterTitleHeading']))

    for sec_title, paragraphs in CH7_SECTIONS:
        key = "CH7_" + sec_title.split()[0].replace('.', '_')
        elements.append(PageTracker(key, registry))
        elements.append(Paragraph(sec_title, styles['ReportSectionHeading']))
        for i, p in enumerate(paragraphs):
            style = styles['RunningTextNoIndent'] if i == 0 else styles['RunningText']
            elements.append(Paragraph(p, style))

    return elements

def build_references(styles, registry):
    elements = []
    elements.append(PageTracker('REFERENCES', registry))
    ref_heading = ParagraphStyle('RefHeading', fontName='Times-Bold', fontSize=17, leading=22, alignment=TA_CENTER, spaceAfter=20)
    elements.append(Paragraph("REFERENCES", ref_heading))
    elements.append(Spacer(1, 4 * mm))

    for i, ref in enumerate(REFERENCES_LIST):
        ref_text = f"[{i+1}] {ref}"
        elements.append(Paragraph(ref_text, styles['ReferenceItem']))

    return elements

def build_appendices(styles, read_end, write_reg, write_end):
    elements = []
    # Appendix A
    elements.append(PageTracker('APP_A', write_reg))
    app_heading = ParagraphStyle('AppHeading', fontName='Times-Bold', fontSize=17, leading=22, alignment=TA_CENTER, spaceAfter=14)
    elements.append(Paragraph("APPENDIX A", app_heading))
    elements.append(Paragraph("DATA SCHEMA AND FEATURE DICTIONARY", styles['ChapterTitleHeading']))

    for sec_title, paragraphs in APPENDIX_A_CONTENT:
        elements.append(Paragraph(sec_title, styles['ReportSectionHeading']))
        for p in paragraphs:
            elements.append(Paragraph(p, styles['RunningText']))

    elements.append(Spacer(1, 4 * mm))
    elements.append(PageTracker('TABA_1', write_reg))
    elements.append(Paragraph("Table A.1: Complete 21-Column Data Schema Specification", styles['ReportTableCaption']))
    schema_rows = [
        [Paragraph("<b>#</b>", styles['TOCItemTitleBold']), Paragraph("<b>Column Name</b>", styles['TOCItemTitleBold']), Paragraph("<b>Data Type</b>", styles['TOCItemTitleBold']), Paragraph("<b>Missing</b>", styles['TOCItemTitleBold']), Paragraph("<b>Operational Handling</b>", styles['TOCItemTitleBold'])],
        [Paragraph("1", styles['TOCItemTitle']), Paragraph("customerID", styles['TOCItemTitleBold']), Paragraph("String ID", styles['TOCItemTitle']), Paragraph("--", styles['TOCItemTitle']), Paragraph("Ignored / dropped from features", styles['TOCItemTitle'])],
        [Paragraph("2", styles['TOCItemTitle']), Paragraph("gender", styles['TOCItemTitle']), Paragraph("Categorical", styles['TOCItemTitle']), Paragraph("--", styles['TOCItemTitle']), Paragraph("One-Hot Encoded (drop='first')", styles['TOCItemTitle'])],
        [Paragraph("3", styles['TOCItemTitle']), Paragraph("SeniorCitizen", styles['TOCItemTitle']), Paragraph("Binary (0/1)", styles['TOCItemTitle']), Paragraph("--", styles['TOCItemTitle']), Paragraph("Categorical binary feature", styles['TOCItemTitle'])],
        [Paragraph("4", styles['TOCItemTitle']), Paragraph("Partner", styles['TOCItemTitle']), Paragraph("Categorical", styles['TOCItemTitle']), Paragraph("--", styles['TOCItemTitle']), Paragraph("One-Hot Encoded", styles['TOCItemTitle'])],
        [Paragraph("5", styles['TOCItemTitle']), Paragraph("Dependents", styles['TOCItemTitle']), Paragraph("Categorical", styles['TOCItemTitle']), Paragraph("--", styles['TOCItemTitle']), Paragraph("One-Hot Encoded", styles['TOCItemTitle'])],
        [Paragraph("6", styles['TOCItemTitle']), Paragraph("tenure", styles['TOCItemTitleBold']), Paragraph("Integer", styles['TOCItemTitle']), Paragraph("--", styles['TOCItemTitle']), Paragraph("Continuous scaled (StandardScaler)", styles['TOCItemTitle'])],
        [Paragraph("7", styles['TOCItemTitle']), Paragraph("PhoneService", styles['TOCItemTitle']), Paragraph("Categorical", styles['TOCItemTitle']), Paragraph("--", styles['TOCItemTitle']), Paragraph("One-Hot Encoded", styles['TOCItemTitle'])],
        [Paragraph("8", styles['TOCItemTitle']), Paragraph("MultipleLines", styles['TOCItemTitle']), Paragraph("Categorical", styles['TOCItemTitle']), Paragraph("--", styles['TOCItemTitle']), Paragraph("One-Hot Encoded", styles['TOCItemTitle'])],
        [Paragraph("9", styles['TOCItemTitle']), Paragraph("InternetService", styles['TOCItemTitleBold']), Paragraph("Categorical", styles['TOCItemTitle']), Paragraph("--", styles['TOCItemTitle']), Paragraph("One-Hot Encoded (DSL, Fiber, None)", styles['TOCItemTitle'])],
        [Paragraph("10", styles['TOCItemTitle']), Paragraph("OnlineSecurity", styles['TOCItemTitle']), Paragraph("Categorical", styles['TOCItemTitle']), Paragraph("--", styles['TOCItemTitle']), Paragraph("One-Hot Encoded", styles['TOCItemTitle'])],
        [Paragraph("11", styles['TOCItemTitle']), Paragraph("OnlineBackup", styles['TOCItemTitle']), Paragraph("Categorical", styles['TOCItemTitle']), Paragraph("--", styles['TOCItemTitle']), Paragraph("One-Hot Encoded", styles['TOCItemTitle'])],
        [Paragraph("12", styles['TOCItemTitle']), Paragraph("DeviceProtection", styles['TOCItemTitle']), Paragraph("Categorical", styles['TOCItemTitle']), Paragraph("--", styles['TOCItemTitle']), Paragraph("One-Hot Encoded", styles['TOCItemTitle'])],
        [Paragraph("13", styles['TOCItemTitle']), Paragraph("TechSupport", styles['TOCItemTitle']), Paragraph("Categorical", styles['TOCItemTitle']), Paragraph("--", styles['TOCItemTitle']), Paragraph("One-Hot Encoded", styles['TOCItemTitle'])],
        [Paragraph("14", styles['TOCItemTitle']), Paragraph("StreamingTV", styles['TOCItemTitle']), Paragraph("Categorical", styles['TOCItemTitle']), Paragraph("--", styles['TOCItemTitle']), Paragraph("One-Hot Encoded", styles['TOCItemTitle'])],
        [Paragraph("15", styles['TOCItemTitle']), Paragraph("StreamingMovies", styles['TOCItemTitle']), Paragraph("Categorical", styles['TOCItemTitle']), Paragraph("--", styles['TOCItemTitle']), Paragraph("One-Hot Encoded", styles['TOCItemTitle'])],
        [Paragraph("16", styles['TOCItemTitle']), Paragraph("Contract", styles['TOCItemTitleBold']), Paragraph("Categorical", styles['TOCItemTitle']), Paragraph("--", styles['TOCItemTitle']), Paragraph("One-Hot Encoded (Month, 1yr, 2yr)", styles['TOCItemTitle'])],
        [Paragraph("17", styles['TOCItemTitle']), Paragraph("PaperlessBilling", styles['TOCItemTitle']), Paragraph("Categorical", styles['TOCItemTitle']), Paragraph("--", styles['TOCItemTitle']), Paragraph("One-Hot Encoded", styles['TOCItemTitle'])],
        [Paragraph("18", styles['TOCItemTitle']), Paragraph("PaymentMethod", styles['TOCItemTitle']), Paragraph("Categorical", styles['TOCItemTitle']), Paragraph("--", styles['TOCItemTitle']), Paragraph("One-Hot Encoded (4 payment channels)", styles['TOCItemTitle'])],
        [Paragraph("19", styles['TOCItemTitle']), Paragraph("MonthlyCharges", styles['TOCItemTitleBold']), Paragraph("Float", styles['TOCItemTitle']), Paragraph("--", styles['TOCItemTitle']), Paragraph("Continuous scaled (StandardScaler)", styles['TOCItemTitle'])],
        [Paragraph("20", styles['TOCItemTitle']), Paragraph("TotalCharges", styles['TOCItemTitleBold']), Paragraph("Float", styles['TOCItemTitle']), Paragraph("11 blanks", styles['TOCItemTitle']), Paragraph("Median Imputed & StandardScaler", styles['TOCItemTitle'])],
        [Paragraph("21", styles['TOCItemTitle']), Paragraph("Churn", styles['TOCItemTitleBold']), Paragraph("Binary Target", styles['TOCItemTitle']), Paragraph("--", styles['TOCItemTitle']), Paragraph("Ground truth answer column (Yes/No)", styles['TOCItemTitle'])]
    ]
    t_sch = Table(schema_rows, colWidths=[10 * mm, 36 * mm, 24 * mm, 22 * mm, 48 * mm])
    t_sch.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
    ]))
    elements.append(t_sch)
    elements.append(SectionEndTracker('APPA_END', write_end))
    elements.extend(odd_transition('APPA_END', read_end))

    # Appendix B
    elements.append(PageTracker('APP_B', write_reg))
    elements.append(Paragraph("APPENDIX B", app_heading))
    elements.append(Paragraph("SYSTEM INSTALLATION AND CONFIGURATION GUIDE", styles['ChapterTitleHeading']))

    for sec_title, paragraphs in APPENDIX_B_CONTENT:
        elements.append(Paragraph(sec_title, styles['ReportSectionHeading']))
        for p in paragraphs:
            elements.append(Paragraph(p, styles['RunningText']))
    elements.append(SectionEndTracker('APPB_END', write_end))
    elements.extend(odd_transition('APPB_END', read_end))

    # Appendix C
    elements.append(PageTracker('APP_C', write_reg))
    elements.append(Paragraph("APPENDIX C", app_heading))
    elements.append(Paragraph("CORE PIPELINE SOURCE CODE", styles['ChapterTitleHeading']))

    for sec_title, paragraphs in APPENDIX_C_CONTENT:
        elements.append(Paragraph(sec_title, styles['ReportSectionHeading']))
        for p in paragraphs:
            elements.append(Paragraph(p, styles['RunningText']))

    code_text = (
        "# scikit-learn Pipeline Encapsulation (src/train_experiment.py)\n"
        "num_transformer = Pipeline(steps=[\n"
        "    ('imputer', SimpleImputer(strategy='median')),\n"
        "    ('scaler', StandardScaler())\n"
        "])\n\n"
        "cat_transformer = Pipeline(steps=[\n"
        "    ('imputer', SimpleImputer(strategy='most_frequent')),\n"
        "    ('onehot', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))\n"
        "])\n\n"
        "preprocessor = ColumnTransformer(transformers=[\n"
        "    ('num', num_transformer, ['tenure', 'MonthlyCharges', 'TotalCharges']),\n"
        "    ('cat', cat_transformer, categorical_columns)\n"
        "])\n\n"
        "pipeline = Pipeline(steps=[\n"
        "    ('prep', preprocessor),\n"
        "    ('model', GradientBoostingClassifier(learning_rate=0.05, max_depth=3, n_estimators=100, random_state=42))\n"
        "])\n"
    )
    elements.append(Spacer(1, 2 * mm))
    for line in code_text.split('\n'):
        elements.append(Paragraph(line.replace(' ', '&nbsp;'), styles['CodeSnippet']))
    elements.append(SectionEndTracker('APPC_END', write_end))

    return elements

def build_full_story(styles, read_reg, read_end, write_reg, write_end):
    story = []
    # 1. Cover Page
    story.extend(build_cover_page(styles))
    story.append(SectionEndTracker('COVER', write_end))
    story.extend(odd_transition('COVER', read_end))

    # 2. Inside Title Page
    story.extend(build_cover_page(styles))
    story.append(SectionEndTracker('INSIDE_TITLE', write_end))
    story.extend(odd_transition('INSIDE_TITLE', read_end))

    # 3. Certificate
    story.extend(build_certificate_page(styles, write_reg))
    story.append(SectionEndTracker('CERTIFICATE_END', write_end))
    story.extend(odd_transition('CERTIFICATE_END', read_end))

    # 4. Declaration
    story.extend(build_declaration_page(styles, write_reg))
    story.append(SectionEndTracker('DECLARATION_END', write_end))
    story.extend(odd_transition('DECLARATION_END', read_end))

    # 5. Acknowledgments
    story.extend(build_acknowledgments_page(styles, write_reg))
    story.append(SectionEndTracker('ACK_END', write_end))
    story.extend(odd_transition('ACK_END', read_end))

    # 6. Abstract
    story.extend(build_abstract_page(styles, write_reg))
    story.append(SectionEndTracker('ABS_END', write_end))
    story.extend(odd_transition('ABS_END', read_end))

    # 7. Table of Contents
    story.extend(build_toc_page(styles, read_reg, write_reg))
    story.append(SectionEndTracker('TOC_END', write_end))
    story.extend(odd_transition('TOC_END', read_end))

    # 8. List of Figures
    story.extend(build_list_of_figures(styles, read_reg, write_reg))
    story.append(SectionEndTracker('LOF_END', write_end))
    story.extend(odd_transition('LOF_END', read_end))

    # 9. List of Tables
    story.extend(build_list_of_tables(styles, read_reg, write_reg))
    story.append(SectionEndTracker('LOT_END', write_end))
    story.extend(odd_transition('LOT_END', read_end))

    # 10. Abbreviations
    story.extend(build_abbreviations_page(styles, write_reg))
    story.append(SectionEndTracker('ABB_END', write_end))
    story.extend(odd_transition('ABB_END', read_end))

    # 11. Chapters
    story.extend(build_chapter_1(styles, write_reg))
    story.append(SectionEndTracker('CH1_END', write_end))
    story.extend(odd_transition('CH1_END', read_end))

    story.extend(build_chapter_2(styles, write_reg))
    story.append(SectionEndTracker('CH2_END', write_end))
    story.extend(odd_transition('CH2_END', read_end))

    story.extend(build_chapter_3(styles, write_reg))
    story.append(SectionEndTracker('CH3_END', write_end))
    story.extend(odd_transition('CH3_END', read_end))

    story.extend(build_chapter_4(styles, write_reg))
    story.append(SectionEndTracker('CH4_END', write_end))
    story.extend(odd_transition('CH4_END', read_end))

    story.extend(build_chapter_5(styles, write_reg))
    story.append(SectionEndTracker('CH5_END', write_end))
    story.extend(odd_transition('CH5_END', read_end))

    story.extend(build_chapter_6(styles, write_reg))
    story.append(SectionEndTracker('CH6_END', write_end))
    story.extend(odd_transition('CH6_END', read_end))

    story.extend(build_chapter_7(styles, write_reg))
    story.append(SectionEndTracker('CH7_END', write_end))
    story.extend(odd_transition('CH7_END', read_end))

    # 12. References
    story.extend(build_references(styles, write_reg))
    story.append(SectionEndTracker('REF_END', write_end))
    story.extend(odd_transition('REF_END', read_end))

    # 13. Appendices
    story.extend(build_appendices(styles, read_end, write_reg, write_end))

    return story

def generate_pdf(output_path='report/project_report.pdf', max_passes=4):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    styles = get_styles()

    read_reg = {}
    read_end = {}

    for pass_num in range(1, max_passes + 1):
        print(f"Executing Pass {pass_num} of {max_passes}...")
        write_reg = {}
        write_end = {}
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=MARGIN_LEFT,
            rightMargin=MARGIN_RIGHT,
            topMargin=MARGIN_TOP,
            bottomMargin=MARGIN_BOTTOM
        )
        story = build_full_story(styles, read_reg, read_end, write_reg, write_end)
        doc.build(story, canvasmaker=ReportCanvas)

        is_converged = (read_reg == write_reg and read_end == write_end)
        read_reg = write_reg
        read_end = write_end

        pdf_doc = fitz.open(output_path)
        total_pages = len(pdf_doc)
        print(f"Pass {pass_num} Complete. Total Page Count: {total_pages}. Converged: {is_converged}")
        if is_converged:
            break

    print(f"Final PDF Verified. Total Page Count: {total_pages} pages.")
    return total_pages

if __name__ == '__main__':
    generate_pdf()
