"""
PDF Export Views — Notes
========================
Server-side PDF generation using ReportLab.
Ownership is checked on every request.
Users can only export their own content.
"""

import io
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph, Spacer, SimpleDocTemplate, HRFlowable, Table, TableStyle
)

from .models import Note


def _brand_color():
    return colors.HexColor('#4f46e5')


def _build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='NoteTitle',
        fontSize=20,
        fontName='Helvetica-Bold',
        textColor=_brand_color(),
        spaceAfter=6,
        leading=24,
    ))
    styles.add(ParagraphStyle(
        name='MetaLabel',
        fontSize=8,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#94a3b8'),
        spaceBefore=2,
        spaceAfter=1,
    ))
    styles.add(ParagraphStyle(
        name='MetaValue',
        fontSize=9,
        fontName='Helvetica',
        textColor=colors.HexColor('#475569'),
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name='NoteContent',
        fontSize=10,
        fontName='Helvetica',
        textColor=colors.HexColor('#0f172a'),
        leading=16,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name='Footer',
        fontSize=7,
        fontName='Helvetica',
        textColor=colors.HexColor('#94a3b8'),
        alignment=1,  # centre
    ))
    return styles


@login_required
def note_pdf(request, pk):
    """Export a single note as a PDF. Only the note owner can export."""
    note = get_object_or_404(Note, pk=pk, user=request.user)
    styles = _build_styles()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=note.title,
        author=request.user.get_full_name() or request.user.username,
    )

    story = []

    # ── Header ────────────────────────────────────────────────
    story.append(Paragraph("AI Study Hub", styles['MetaLabel']))
    story.append(Paragraph(note.title, styles['NoteTitle']))
    story.append(HRFlowable(
        width="100%", thickness=1.5,
        color=_brand_color(), spaceAfter=10,
    ))

    # ── Metadata table ────────────────────────────────────────
    meta_data = [
        ["Category", note.category.name if note.category else "General"],
        ["Created",  note.created_at.strftime("%B %d, %Y %H:%M")],
        ["Updated",  note.updated_at.strftime("%B %d, %Y %H:%M")],
    ]
    if note.tags.exists():
        meta_data.append(["Tags", "  ".join(f"#{t.name}" for t in note.tags.all())])

    meta_table = Table(meta_data, colWidths=[3 * cm, None])
    meta_table.setStyle(TableStyle([
        ('FONTNAME',    (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, -1), 8),
        ('TEXTCOLOR',   (0, 0), (0, -1), colors.HexColor('#94a3b8')),
        ('TEXTCOLOR',   (1, 0), (1, -1), colors.HexColor('#475569')),
        ('TOPPADDING',  (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('VALIGN',      (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # ── Content ───────────────────────────────────────────────
    story.append(Paragraph("Note Content", ParagraphStyle(
        'SectionHead', fontSize=11, fontName='Helvetica-Bold',
        textColor=_brand_color(), spaceAfter=6,
    )))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e2e8f0'), spaceAfter=8))

    # Split content on newlines and render each line as a Paragraph
    for line in note.content.split('\n'):
        text = line.strip()
        if text:
            story.append(Paragraph(text, styles['NoteContent']))
        else:
            story.append(Spacer(1, 6))

    # ── Footer ────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e2e8f0'), spaceAfter=6))
    story.append(Paragraph(
        f"Exported from AI Study Hub · {timezone.now().strftime('%B %d, %Y')} · {request.user.username}",
        styles['Footer']
    ))

    doc.build(story)
    buffer.seek(0)

    safe_title = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in note.title)[:60]
    filename = f"note_{safe_title}.pdf"

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
