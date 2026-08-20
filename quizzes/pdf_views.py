"""
PDF Export Views — Quizzes & Study Sessions
============================================
Server-side PDF generation using ReportLab.
Ownership is checked on every request.
"""

import io
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph, Spacer, SimpleDocTemplate, HRFlowable,
    Table, TableStyle, KeepTogether,
)

from .models import Quiz, StudySession

# ── shared helpers ────────────────────────────────────────────

def _brand():
    return colors.HexColor('#4f46e5')

def _success():
    return colors.HexColor('#10b981')

def _danger():
    return colors.HexColor('#ef4444')

def _muted():
    return colors.HexColor('#94a3b8')

def _text():
    return colors.HexColor('#0f172a')

def _secondary():
    return colors.HexColor('#475569')

def _build_base_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('AppLabel', fontSize=8, fontName='Helvetica-Bold',
                              textColor=_muted(), spaceAfter=2))
    styles.add(ParagraphStyle('DocTitle', fontSize=20, fontName='Helvetica-Bold',
                              textColor=_brand(), spaceAfter=4, leading=24))
    styles.add(ParagraphStyle('SectionHead', fontSize=11, fontName='Helvetica-Bold',
                              textColor=_brand(), spaceAfter=4, spaceBefore=10))
    styles.add(ParagraphStyle('Body', fontSize=9.5, fontName='Helvetica',
                              textColor=_text(), leading=15, spaceAfter=4))
    styles.add(ParagraphStyle('BodySmall', fontSize=8.5, fontName='Helvetica',
                              textColor=_secondary(), leading=13, spaceAfter=3))
    styles.add(ParagraphStyle('Footer', fontSize=7, fontName='Helvetica',
                              textColor=_muted(), alignment=1))
    styles.add(ParagraphStyle('QuestionText', fontSize=10, fontName='Helvetica-Bold',
                              textColor=_text(), leading=15, spaceAfter=5))
    styles.add(ParagraphStyle('OptionText', fontSize=9, fontName='Helvetica',
                              textColor=_secondary(), leading=13))
    return styles


def _footer_paragraph(styles, username):
    return Paragraph(
        f"Exported from AI Study Hub · {timezone.now().strftime('%B %d, %Y')} · {username}",
        styles['Footer']
    )


# ── Quiz Result PDF ───────────────────────────────────────────

@login_required
def quiz_result_pdf(request, pk):
    """Export a completed quiz result as PDF. Owner-only."""
    quiz = get_object_or_404(Quiz, pk=pk, user=request.user)
    styles = _build_base_styles()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title=f"Quiz Results — {quiz.title}",
        author=request.user.get_full_name() or request.user.username,
    )

    story = []

    # ── Header ────────────────────────────────────────────────
    story.append(Paragraph("AI Study Hub — Quiz Results", styles['AppLabel']))
    story.append(Paragraph(quiz.title, styles['DocTitle']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=_brand(), spaceAfter=10))

    # ── Score summary table ───────────────────────────────────
    incorrect = quiz.total_questions - quiz.correct_answers
    pct_color = _success() if quiz.score >= 60 else _danger()

    summary_data = [
        ["Score",     f"{quiz.score:.1f}%"],
        ["Correct",   str(quiz.correct_answers)],
        ["Incorrect", str(incorrect)],
        ["Total",     str(quiz.total_questions)],
        ["Date",      quiz.updated_at.strftime("%B %d, %Y %H:%M")],
    ]
    if quiz.source_note:
        summary_data.append(["Source Note", quiz.source_note.title])

    summary_table = Table(summary_data, colWidths=[3.5 * cm, None])
    summary_table.setStyle(TableStyle([
        ('FONTNAME',     (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME',     (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE',     (0, 0), (-1, -1), 9),
        ('TEXTCOLOR',    (0, 0), (0, -1), _muted()),
        ('TEXTCOLOR',    (1, 0), (1, 0),  pct_color),   # score row coloured
        ('TEXTCOLOR',    (1, 1), (1, -1), _secondary()),
        ('TOPPADDING',   (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 2),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 14))

    # ── Question review ───────────────────────────────────────
    questions = quiz.questions.all()
    if questions.exists():
        story.append(Paragraph("Question-by-Question Review", styles['SectionHead']))
        story.append(HRFlowable(width="100%", thickness=0.5,
                                color=colors.HexColor('#e2e8f0'), spaceAfter=8))

        for idx, q in enumerate(questions, start=1):
            status_color = _success() if q.is_correct else _danger()
            status_label = "✓ Correct" if q.is_correct else "✗ Incorrect"

            block = []

            # Question header row
            q_header = Table(
                [[Paragraph(f"Q{idx}. {q.question_text}", styles['QuestionText']),
                  Paragraph(status_label, ParagraphStyle(
                      'Status', fontSize=9, fontName='Helvetica-Bold',
                      textColor=status_color, alignment=2))]],
                colWidths=[None, 3 * cm],
            )
            q_header.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            block.append(q_header)
            block.append(Spacer(1, 4))

            # Options
            for opt in q.options:
                if opt == q.correct_answer:
                    opt_style = ParagraphStyle('OptCorrect', fontSize=9,
                                               fontName='Helvetica-Bold',
                                               textColor=_success())
                    prefix = "✓ "
                elif opt == q.user_answer and not q.is_correct:
                    opt_style = ParagraphStyle('OptWrong', fontSize=9,
                                               fontName='Helvetica',
                                               textColor=_danger())
                    prefix = "✗ "
                else:
                    opt_style = styles['OptionText']
                    prefix = "   "
                block.append(Paragraph(f"{prefix}{opt}", opt_style))

            # Explanation
            if q.explanation:
                block.append(Spacer(1, 4))
                block.append(Paragraph(
                    f"Explanation: {q.explanation}",
                    ParagraphStyle('Expl', fontSize=8.5, fontName='Helvetica-Oblique',
                                   textColor=_brand(), leading=13)
                ))

            block.append(Spacer(1, 8))
            block.append(HRFlowable(width="100%", thickness=0.3,
                                    color=colors.HexColor('#e2e8f0'), spaceAfter=6))
            story.append(KeepTogether(block))

    # ── Footer ────────────────────────────────────────────────
    story.append(Spacer(1, 16))
    story.append(_footer_paragraph(styles, request.user.username))

    doc.build(story)
    buffer.seek(0)

    safe = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in quiz.title)[:50]
    filename = f"quiz_result_{safe}.pdf"

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# ── Study Session History PDF ─────────────────────────────────

@login_required
def study_sessions_pdf(request):
    """Export all completed study sessions as a PDF summary. Owner-only."""
    sessions = StudySession.objects.filter(
        user=request.user, end_time__isnull=False
    ).order_by('-start_time').select_related('category')

    styles = _build_base_styles()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title="Study Session History",
        author=request.user.get_full_name() or request.user.username,
    )

    story = []

    # ── Header ────────────────────────────────────────────────
    story.append(Paragraph("AI Study Hub — Study Sessions", styles['AppLabel']))
    story.append(Paragraph("Study Session History", styles['DocTitle']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=_brand(), spaceAfter=10))

    # ── Summary stats ─────────────────────────────────────────
    total_sessions = sessions.count()
    total_minutes  = sessions.aggregate(t=Sum('duration_minutes'))['t'] or 0
    total_hours    = total_minutes // 60
    remaining_min  = total_minutes % 60

    stats_data = [
        ["Total Sessions",    str(total_sessions)],
        ["Total Study Time",  f"{total_hours}h {remaining_min}m  ({total_minutes} minutes)"],
        ["Exported",          timezone.now().strftime("%B %d, %Y %H:%M")],
    ]
    stats_table = Table(stats_data, colWidths=[4 * cm, None])
    stats_table.setStyle(TableStyle([
        ('FONTNAME',     (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE',     (0, 0), (-1, -1), 9),
        ('TEXTCOLOR',    (0, 0), (0, -1), _muted()),
        ('TEXTCOLOR',    (1, 0), (1, -1), _secondary()),
        ('TOPPADDING',   (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 2),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 14))

    if sessions.exists():
        story.append(Paragraph("Session Log", styles['SectionHead']))
        story.append(HRFlowable(width="100%", thickness=0.5,
                                color=colors.HexColor('#e2e8f0'), spaceAfter=8))

        # Table header
        header = [
            Paragraph("Subject",    ParagraphStyle('TH', fontSize=8, fontName='Helvetica-Bold', textColor=_muted())),
            Paragraph("Category",   ParagraphStyle('TH', fontSize=8, fontName='Helvetica-Bold', textColor=_muted())),
            Paragraph("Date",       ParagraphStyle('TH', fontSize=8, fontName='Helvetica-Bold', textColor=_muted())),
            Paragraph("Start",      ParagraphStyle('TH', fontSize=8, fontName='Helvetica-Bold', textColor=_muted())),
            Paragraph("End",        ParagraphStyle('TH', fontSize=8, fontName='Helvetica-Bold', textColor=_muted())),
            Paragraph("Duration",   ParagraphStyle('TH', fontSize=8, fontName='Helvetica-Bold', textColor=_muted())),
        ]

        table_data = [header]
        cell_style = ParagraphStyle('TC', fontSize=8.5, fontName='Helvetica', textColor=_text())
        muted_style = ParagraphStyle('TCm', fontSize=8, fontName='Helvetica', textColor=_secondary())

        for sess in sessions:
            table_data.append([
                Paragraph(sess.subject or "General Study", cell_style),
                Paragraph(sess.category.name if sess.category else "—", muted_style),
                Paragraph(sess.start_time.strftime("%b %d, %Y"), muted_style),
                Paragraph(sess.start_time.strftime("%H:%M"), muted_style),
                Paragraph(sess.end_time.strftime("%H:%M") if sess.end_time else "—", muted_style),
                Paragraph(f"{sess.duration_minutes} min", ParagraphStyle(
                    'Dur', fontSize=8.5, fontName='Helvetica-Bold', textColor=_brand())),
            ])

        col_widths = [4.5*cm, 3*cm, 3*cm, 2*cm, 2*cm, 2.5*cm]
        session_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        session_table.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, 0),  colors.HexColor('#f8fafc')),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('LINEBELOW',    (0, 0), (-1, 0),   0.8, colors.HexColor('#e2e8f0')),
            ('LINEBELOW',    (0, 1), (-1, -1),  0.3, colors.HexColor('#e2e8f0')),
            ('TOPPADDING',   (0, 0), (-1, -1),  4),
            ('BOTTOMPADDING',(0, 0), (-1, -1),  4),
            ('VALIGN',       (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(session_table)
    else:
        story.append(Paragraph("No completed study sessions found.", styles['Body']))

    # ── Footer ────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5,
                            color=colors.HexColor('#e2e8f0'), spaceAfter=6))
    story.append(_footer_paragraph(styles, request.user.username))

    doc.build(story)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="study_sessions.pdf"'
    return response
