#!/usr/bin/env python3
"""
decoupled_dots_results_pdf.py
------------------------------
Renders Agents/Literature/decoupled_dots_results.md as a clean multi-page PDF.
Output: Agents/WriteUps/decoupled_dots_results.pdf
"""

import os, re
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable, PageBreak,
                                 Preformatted)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

_HERE  = os.path.dirname(os.path.abspath(__file__))
BASE   = os.path.normpath(os.path.join(_HERE, '../../Agents'))

import argparse as _ap
_p = _ap.ArgumentParser(add_help=False)
_p.add_argument('--in-md',  default=None)
_p.add_argument('--out-pdf', default=None)
_args, _ = _p.parse_known_args()

IN_MD   = _args.in_md  or os.path.join(BASE, 'Literature', 'decoupled_dots_results.md')
OUT_PDF = _args.out_pdf or os.path.join(BASE, 'WriteUps',  'decoupled_dots_results.pdf')
os.makedirs(os.path.dirname(OUT_PDF), exist_ok=True)

# ── Styles ─────────────────────────────────────────────────────────────────────
ss = getSampleStyleSheet()

styles = {
    'title': ParagraphStyle('title', parent=ss['Title'],
                            fontSize=14, spaceAfter=6, textColor=colors.HexColor('#1a1a1a')),
    'date':  ParagraphStyle('date', parent=ss['Normal'],
                            fontSize=8, textColor=colors.grey, spaceAfter=12),
    'h2':    ParagraphStyle('h2', parent=ss['Heading2'],
                            fontSize=12, spaceBefore=14, spaceAfter=4,
                            textColor=colors.HexColor('#1a3a8b'),
                            borderPad=2),
    'h3':    ParagraphStyle('h3', parent=ss['Heading3'],
                            fontSize=10, spaceBefore=10, spaceAfter=3,
                            textColor=colors.HexColor('#333333')),
    'h4':    ParagraphStyle('h4', parent=ss['Heading4'],
                            fontSize=9, spaceBefore=7, spaceAfter=2,
                            textColor=colors.HexColor('#555555'), fontName='Helvetica-BoldOblique'),
    'body':  ParagraphStyle('body', parent=ss['Normal'],
                            fontSize=8.5, leading=13, spaceAfter=4),
    'bold_body': ParagraphStyle('bold_body', parent=ss['Normal'],
                            fontSize=8.5, leading=13, spaceAfter=4, fontName='Helvetica-Bold'),
    'code':  ParagraphStyle('code', parent=ss['Code'],
                            fontSize=7.5, leading=11, leftIndent=12,
                            backColor=colors.HexColor('#f5f5f5'),
                            borderColor=colors.HexColor('#cccccc'),
                            borderWidth=0.5, borderPad=4,
                            fontName='Courier', spaceAfter=6),
    'bullet': ParagraphStyle('bullet', parent=ss['Normal'],
                             fontSize=8.5, leading=13, leftIndent=16,
                             firstLineIndent=-10, spaceAfter=3),
    'sub_bullet': ParagraphStyle('sub_bullet', parent=ss['Normal'],
                             fontSize=8.5, leading=13, leftIndent=28,
                             firstLineIndent=-10, spaceAfter=2),
    'italic': ParagraphStyle('italic', parent=ss['Normal'],
                             fontSize=8, leading=12, textColor=colors.HexColor('#555555'),
                             fontName='Helvetica-Oblique', spaceAfter=4),
    'hr': None,
}

TABLE_HEADER_BG = colors.HexColor('#dce6f7')
TABLE_ALT_BG    = colors.HexColor('#f7f9fd')
TABLE_GRID      = colors.HexColor('#aaaaaa')

def make_table(headers, rows):
    """Build a formatted reportlab Table from header list and row lists."""
    col_count = len(headers)
    data = [headers] + rows

    # Auto-size columns equally, with a minimum
    col_w = (6.5 * inch) / col_count

    tbl = Table(data, colWidths=[col_w] * col_count, repeatRows=1)
    style_cmds = [
        ('BACKGROUND',  (0, 0), (-1, 0), TABLE_HEADER_BG),
        ('TEXTCOLOR',   (0, 0), (-1, 0), colors.HexColor('#1a1a6b')),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, -1), 7.5),
        ('LEADING',     (0, 0), (-1, -1), 10),
        ('GRID',        (0, 0), (-1, -1), 0.4, TABLE_GRID),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, TABLE_ALT_BG]),
        ('LEFTPADDING',  (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING',   (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 3),
        ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
    ]
    tbl.setStyle(TableStyle(style_cmds))
    return tbl

def ascii_safe(text):
    """Replace Unicode characters that Courier/Helvetica can't render."""
    # Superscript digits/signs
    sup_map = {'⁰':'0','¹':'1','²':'2','³':'3','⁴':'4','⁵':'5',
               '⁶':'6','⁷':'7','⁸':'8','⁹':'9','⁻':'-','⁺':'+'}
    for ch, asc in sup_map.items():
        text = text.replace(ch, asc)
    # Subscript digits
    sub_map = {'₀':'0','₁':'1','₂':'2','₃':'3','₄':'4',
               '₅':'5','₆':'6','₇':'7','₈':'8','₉':'9'}
    for ch, asc in sub_map.items():
        text = text.replace(ch, asc)
    # Greek letters
    greek = {'α':'alpha','β':'beta','γ':'gamma','δ':'delta','μ':'mu',
             'σ':'sigma','λ':'lambda','χ':'chi','ε':'epsilon','η':'eta'}
    for ch, name in greek.items():
        text = text.replace(ch, name)
    # Common symbols
    text = text.replace('×','x').replace('→','->').replace('←','<-')
    text = text.replace('≈','~=').replace('≠','!=').replace('±','+-')
    text = text.replace('—','-').replace('°','deg')
    return text

def inline_fmt(text):
    """Convert markdown inline markup to reportlab XML."""
    # Escape ampersands first
    text = text.replace('&', '&amp;')
    # Bold-italic ***text***
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
    # Bold **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Italic *text*
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    # Code `text`
    text = re.sub(r'`(.+?)`', r'<font name="Courier" size="7.5">\1</font>', text)
    # Em-dash
    text = text.replace('—', '&#8212;')
    # Arrows
    text = text.replace('→', '&#8594;').replace('←', '&#8592;').replace('↔', '&#8596;')
    # Degree
    text = text.replace('°', '&#176;')
    # Times/multiply
    text = text.replace('×', '&#215;')
    # Plus-minus
    text = text.replace('±', '&#177;')
    # Check and cross marks
    text = text.replace('✓', '&#10003;').replace('✗', '&#10007;')
    # Superscript digits and signs (Unicode superscripts → <super>)
    sup_map = {'⁰':'0','¹':'1','²':'2','³':'3','⁴':'4','⁵':'5',
               '⁶':'6','⁷':'7','⁸':'8','⁹':'9','⁻':'-','⁺':'+'}
    # Replace runs of superscript chars as one <super> span
    def _sup_repl(m):
        s = ''.join(sup_map.get(c, c) for c in m.group(0))
        return f'<super>{s}</super>'
    text = re.sub('[⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺]+', _sup_repl, text)
    # Subscript digits (Unicode subscripts → plain small text via <sub>)
    sub_map = {'₀':'0','₁':'1','₂':'2','₃':'3','₄':'4',
               '₅':'5','₆':'6','₇':'7','₈':'8','₉':'9'}
    def _sub_repl(m):
        s = ''.join(sub_map.get(c, c) for c in m.group(0))
        return s   # plain digit — <sub> not supported by reportlab
    text = re.sub('[₀₁₂₃₄₅₆₇₈₉]+', _sub_repl, text)
    # Greek letters (Helvetica lacks them — spell out or use closest ASCII)
    greek = {'α':'alpha','β':'beta','γ':'gamma','δ':'delta','μ':'mu',
             'σ':'sigma','λ':'lambda','χ':'chi','ε':'epsilon','η':'eta'}
    for ch, name in greek.items():
        text = text.replace(ch, f'<i>{name}</i>')
    # Not-equal
    text = text.replace('≠', '&#8800;').replace('≈', '&#8776;')
    # Dagger
    text = text.replace('†', '&#8224;')
    return text

def parse_table(lines):
    """Parse a markdown pipe-table into (headers, rows) lists of Paragraph."""
    rows_raw = []
    for line in lines:
        line = line.strip().strip('|')
        if re.match(r'^[\s\-|:]+$', line):
            continue
        cells = [c.strip() for c in line.split('|')]
        rows_raw.append(cells)
    if not rows_raw:
        return None, None
    headers = [Paragraph(inline_fmt(h), styles['bold_body']) for h in rows_raw[0]]
    rows = [[Paragraph(inline_fmt(c), styles['body']) for c in r]
            for r in rows_raw[1:]]
    return headers, rows

def md_to_story(md_text):
    story = []
    lines = md_text.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip YAML front-matter (if any)
        if stripped == '---' and i == 0:
            i += 1
            while i < len(lines) and lines[i].strip() != '---':
                i += 1
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^---+$', stripped):
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width='100%', thickness=0.5,
                                    color=colors.HexColor('#cccccc')))
            story.append(Spacer(1, 4))
            i += 1
            continue

        # Headings
        m = re.match(r'^(#{1,4})\s+(.*)', stripped)
        if m:
            level = len(m.group(1))
            text  = inline_fmt(m.group(2))
            if level == 1:
                story.append(Paragraph(text, styles['title']))
            elif level == 2:
                story.append(Paragraph(text, styles['h2']))
            elif level == 3:
                story.append(Paragraph(text, styles['h3']))
            else:
                story.append(Paragraph(text, styles['h4']))
            i += 1
            continue

        # Italic date line (e.g. *Written 2026-04-06*)
        m = re.match(r'^\*(.+)\*$', stripped)
        if m:
            story.append(Paragraph(m.group(1), styles['italic']))
            i += 1
            continue

        # Code block
        if stripped.startswith('```'):
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            code_text = '\n'.join(code_lines)
            code_text = ascii_safe(code_text)
            story.append(Preformatted(code_text, styles['code']))
            continue

        # Pipe table
        if '|' in stripped and stripped.startswith('|'):
            tbl_lines = []
            while i < len(lines) and '|' in lines[i] and lines[i].strip().startswith('|'):
                tbl_lines.append(lines[i])
                i += 1
            headers, rows = parse_table(tbl_lines)
            if headers:
                story.append(make_table(headers, rows))
                story.append(Spacer(1, 6))
            continue

        # Bullet: sub-level (4 spaces or tab)
        if re.match(r'^(    |\t)\s*[-*]\s+', line):
            text = re.sub(r'^(    |\t)\s*[-*]\s+', '', line)
            story.append(Paragraph('&#8226; ' + inline_fmt(text), styles['sub_bullet']))
            i += 1
            continue

        # Bullet: top-level
        if re.match(r'^[-*]\s+', stripped):
            text = re.sub(r'^[-*]\s+', '', stripped)
            story.append(Paragraph('&#8226; ' + inline_fmt(text), styles['bullet']))
            i += 1
            continue

        # Numbered list
        m = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if m:
            text = m.group(1) + '. ' + inline_fmt(m.group(2))
            story.append(Paragraph(text, styles['bullet']))
            i += 1
            continue

        # Blank line
        if not stripped:
            story.append(Spacer(1, 4))
            i += 1
            continue

        # Normal paragraph
        story.append(Paragraph(inline_fmt(stripped), styles['body']))
        i += 1

    return story

# ── Build PDF ──────────────────────────────────────────────────────────────────
with open(IN_MD, encoding='utf-8') as f:
    md_text = f.read()

story = md_to_story(md_text)

doc = SimpleDocTemplate(
    OUT_PDF,
    pagesize=letter,
    leftMargin=0.85*inch, rightMargin=0.75*inch,
    topMargin=0.85*inch,  bottomMargin=0.85*inch,
    title='DecoupledDots Results',
    author='VRDots Analysis',
)
doc.build(story)
print(f'Saved: {OUT_PDF}')
