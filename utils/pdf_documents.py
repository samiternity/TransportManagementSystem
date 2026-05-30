"""Compact single-page PDF builders for reports and invoices."""

from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

PRIMARY = colors.HexColor('#0984E3')
DARK = colors.HexColor('#2D3436')
MUTED = colors.HexColor('#636E72')
LINE = colors.HexColor('#DFE6E9')
ROW_ALT = colors.HexColor('#F8F9FB')
WHITE = colors.white

PAGE_W, _ = letter
CONTENT_W = PAGE_W - 1.25 * inch


def _styles():
    base = getSampleStyleSheet()
    return {
        'title': ParagraphStyle(
            'Title', parent=base['Normal'], fontName='Helvetica-Bold',
            fontSize=16, textColor=DARK, spaceAfter=2, leading=20,
        ),
        'subtitle': ParagraphStyle(
            'Subtitle', parent=base['Normal'], fontSize=9,
            textColor=MUTED, spaceAfter=10, leading=12,
        ),
        'body': ParagraphStyle(
            'Body', parent=base['Normal'], fontSize=9,
            textColor=DARK, leading=12,
        ),
        'muted': ParagraphStyle(
            'Muted', parent=base['Normal'], fontSize=8,
            textColor=MUTED, leading=10,
        ),
        'right': ParagraphStyle(
            'Right', parent=base['Normal'], fontSize=9,
            alignment=TA_RIGHT, textColor=DARK, leading=12,
        ),
        'right_bold': ParagraphStyle(
            'RightBold', parent=base['Normal'], fontName='Helvetica-Bold',
            fontSize=9, alignment=TA_RIGHT, textColor=DARK, leading=12,
        ),
        'header_right': ParagraphStyle(
            'HeaderRight', parent=base['Normal'], fontSize=8,
            alignment=TA_RIGHT, textColor=MUTED, leading=11,
        ),
    }


def _doc(path, title):
    return SimpleDocTemplate(
        path,
        pagesize=letter,
        leftMargin=0.65 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.5 * inch,
        title=title,
    )


def _page_header(doc_title: str, ref: str):
    """Compact top bar: brand + document meta."""
    styles = _styles()
    issued = datetime.now().strftime('%d %b %Y, %I:%M %p')
    row = Table(
        [[
            Paragraph(
                '<b>Transport Management System</b><br/>'
                f'<font color="#636E72">{doc_title}</font>',
                styles['body'],
            ),
            Paragraph(f'Ref: {ref}<br/>{issued}', styles['header_right']),
        ]],
        colWidths=[CONTENT_W * 0.58, CONTENT_W * 0.42],
    )
    row.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBELOW', (0, 0), (-1, -1), 1.5, PRIMARY),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    return row


def _cell(text, styles, align='left', bold=False):
    style = styles['right_bold'] if align == 'right' and bold else (
        styles['right'] if align == 'right' else styles['body']
    )
    content = f'<b>{text}</b>' if bold else str(text)
    return Paragraph(content, style)


def _simple_table(headers, rows, col_widths, right_cols=None, bold_last=False):
    """Clean table with header row and light borders."""
    styles = _styles()
    right_cols = right_cols or set()
    data = [[Paragraph(f'<b>{h}</b>', styles['body']) for h in headers]]
    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            align = 'right' if i in right_cols else 'left'
            bold = bold_last and i == len(row) - 1
            cells.append(_cell(cell, styles, align=align, bold=bold))
        data.append(cells)

    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, ROW_ALT]),
        ('BOX', (0, 0), (-1, -1), 0.5, LINE),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, LINE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    return t


def _kv_table(pairs):
    """Inline two-column facts without heavy boxes."""
    styles = _styles()
    data = [
        [Paragraph(f'<b>{k}</b>', styles['muted']), Paragraph(str(v), styles['body'])]
        for k, v in pairs
    ]
    t = Table(data, colWidths=[1.35 * inch, CONTENT_W - 1.35 * inch])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    return t


def _format_date(value) -> str:
    if value is None:
        return 'N/A'
    if hasattr(value, 'strftime'):
        return value.strftime('%d %b %Y')
    return str(value)


def _footer_note(text: str):
    return Paragraph(text, _styles()['muted'])


def build_operational_report_pdf(path: str, scope_label: str, metrics: list) -> None:
    """Single-page operational metrics report."""
    ref = f'RPT-{datetime.now().strftime("%Y%m%d-%H%M")}'
    doc = _doc(path, 'Operational Report')
    styles = _styles()

    story = [
        _page_header('Operational Report', ref),
        Spacer(1, 0.12 * inch),
        Paragraph('Operational Analytics Report', styles['title']),
        Paragraph(f'Scope: {scope_label}', styles['subtitle']),
        _kv_table([
            ('Vehicle filter', scope_label),
            ('Metrics', str(len(metrics))),
        ]),
        Spacer(1, 0.1 * inch),
    ]

    rows = [(str(i), label, f'{val:,.1f}', unit) for i, (label, val, unit) in enumerate(metrics, 1)]
    story.append(_simple_table(
        ['#', 'Metric', 'Value', 'Unit'],
        rows,
        [0.4 * inch, 3.5 * inch, 1.15 * inch, 0.7 * inch],
        right_cols={2, 3},
    ))
    story.extend([
        Spacer(1, 0.14 * inch),
        _footer_note(
            'Generated from live system data. Driver utilization is fleet-wide. '
            'Internal use only — Transport Management System.'
        ),
    ])
    doc.build(story)


def build_invoice_pdf(path: str, invoice: dict) -> None:
    """Single-page passenger invoice."""
    invoice_id = invoice['invoice_id']
    ref = f'INV-{invoice_id:05d}'
    doc = _doc(path, 'Invoice')
    styles = _styles()

    amount = float(invoice['amount'])
    status = invoice.get('status', 'Unpaid')
    status_color = '#00B894' if status == 'Paid' else '#D63031'
    due_str = _format_date(invoice.get('due_date'))
    issued = datetime.now().strftime('%d %b %Y')
    route = invoice.get('route', 'Transport service')
    period = invoice.get('billing_period', '')

    story = [
        _page_header('Invoice', ref),
        Spacer(1, 0.12 * inch),
        Paragraph(f'Invoice #{invoice_id}', styles['title']),
        Paragraph(
            f'Status: <font color="{status_color}"><b>{status}</b></font> &nbsp;|&nbsp; '
            f'Issued: {issued} &nbsp;|&nbsp; Due: {due_str}',
            styles['subtitle'],
        ),
        Spacer(1, 0.06 * inch),
        _kv_table([
            ('Bill to', invoice.get('passenger_name', 'N/A')),
            ('Account', invoice.get('username', 'N/A')),
            ('Phone', invoice.get('phone') or '—'),
            ('Service', route),
        ]),
        Spacer(1, 0.1 * inch),
    ]

    rows = [('1', route, period, due_str, f'${amount:,.2f}')]
    story.append(_simple_table(
        ['#', 'Description', 'Period', 'Due', 'Amount'],
        rows,
        [0.35 * inch, 2.6 * inch, 1.1 * inch, 0.95 * inch, 1.0 * inch],
        right_cols={4},
        bold_last=True,
    ))

    total_label = 'Total due' if status != 'Paid' else 'Total paid'
    total_row = Table(
        [[
            Paragraph('', styles['body']),
            Paragraph(f'<b>{total_label}</b>', styles['right_bold']),
            Paragraph(f'<b>${amount:,.2f}</b>', styles['right_bold']),
        ]],
        colWidths=[CONTENT_W - 2.2 * inch, 1.1 * inch, 1.1 * inch],
    )
    total_row.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 1, PRIMARY),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.extend([
        Spacer(1, 0.06 * inch),
        total_row,
        Spacer(1, 0.12 * inch),
        _footer_note(
            f'Payment due by {due_str}. Reference invoice #{invoice_id} when paying. '
            'Pay via the TMS Billing portal. Electronic invoice — no signature required.'
        ),
    ])
    doc.build(story)
