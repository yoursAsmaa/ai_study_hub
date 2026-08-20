"""
AI Assistant Views — AI Study Hub
===================================
All views are login-required.
AI logic is delegated entirely to ai_assistant.services.ai_service.
API keys are never read from request data or exposed to templates.

Flow for every AI action:
  Browser → Django View → ai_service function → AI Provider
                       ↑ ownership check here
"""

import json
import logging

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from notes.models import Note
from quizzes.models import Flashcard, Question, Quiz
from dashboard.models import log_activity

from .models import ChatMessage
from .services.ai_service import (
    AIServiceError,
    build_study_data_for_user,
    chat_with_ai,
    explain_note,
    generate_flashcards,
    generate_quiz,
    get_study_recommendation,
    summarize_note,
    MAX_CHAT_CHARS,
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Helper — safe JSON response
# ─────────────────────────────────────────────────────────────────────────────

def _json_ok(data: dict) -> JsonResponse:
    return JsonResponse({"status": "ok", **data})


def _json_err(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"status": "error", "message": message}, status=status)


# ─────────────────────────────────────────────────────────────────────────────
# 1. AI Study Coach landing page
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def index(request):
    """
    Main AI Study Coach page.
    Shows:
      - Chat interface with history
      - Quick-action links (Summarize, Quiz, Flashcards, Explain, Recommend)
    """
    # Load the last 40 messages for this user only
    chat_history = ChatMessage.objects.filter(user=request.user).order_by('created_at')[:40]

    # User's notes for the quick-action selectors
    user_notes = Note.objects.filter(user=request.user).order_by('-updated_at')[:50]

    return render(request, 'ai_assistant/index.html', {
        'chat_history': chat_history,
        'user_notes': user_notes,
        'max_chat_chars': MAX_CHAT_CHARS,
    })


# ─────────────────────────────────────────────────────────────────────────────
# 2. AI Chat  (AJAX POST)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def chat(request):
    """
    Receive a user message, call the AI, persist both messages,
    and return the AI response as JSON.

    Request body (JSON): {"message": "..."}
    Response (JSON):     {"status": "ok", "answer": "...", "message_id": N}
    """
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return _json_err("Invalid request format.", 400)

    question = body.get("message", "").strip()

    if not question:
        return _json_err("Please enter a question.")

    if len(question) > MAX_CHAT_CHARS:
        return _json_err(
            f"Message too long. Keep it under {MAX_CHAT_CHARS} characters."
        )

    # Save the user's message
    user_msg = ChatMessage.objects.create(
        user=request.user,
        role=ChatMessage.ROLE_USER,
        content=question,
    )

    try:
        answer = chat_with_ai(question)
    except AIServiceError as exc:
        # Remove the user message so conversation stays clean on failure
        user_msg.delete()
        return _json_err(str(exc))

    # Save the AI response
    ai_msg = ChatMessage.objects.create(
        user=request.user,
        role=ChatMessage.ROLE_AI,
        content=answer,
    )

    log_activity(request.user, 'AI_CHAT', f"Asked AI: {question[:60]}")

    return _json_ok({"answer": answer, "message_id": ai_msg.pk})


# ─────────────────────────────────────────────────────────────────────────────
# 3. Clear chat history
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def clear_chat(request):
    """Delete all chat messages for the current user."""
    ChatMessage.objects.filter(user=request.user).delete()
    messages.success(request, "Chat history cleared.")
    return redirect('ai_assistant:index')


# ─────────────────────────────────────────────────────────────────────────────
# 4. Summarize Note  (AJAX POST or regular POST)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def summarize(request):
    """
    Summarize the selected note with AI.
    Ownership is verified: users can only summarize their own notes.

    POST params: note_id (int)
    Returns JSON: {status, summary, key_points, important_terms}
    """
    note_id = request.POST.get("note_id", "").strip()
    if not note_id or not note_id.isdigit():
        return _json_err("Invalid note selected.")

    # Ownership check — get_object_or_404 with user= filter
    note = get_object_or_404(Note, pk=int(note_id), user=request.user)

    try:
        result = summarize_note(note.title, note.content)
    except AIServiceError as exc:
        return _json_err(str(exc))

    # Optionally persist the summary back to the Note.summary field
    if result.get("summary"):
        note.summary = result["summary"]
        note.save(update_fields=["summary"])

    log_activity(request.user, 'AI_SUMMARIZE', f"Summarized note '{note.title}'")

    return _json_ok({
        "note_title": note.title,
        "summary": result["summary"],
        "key_points": result["key_points"],
        "important_terms": result["important_terms"],
    })


# ─────────────────────────────────────────────────────────────────────────────
# 5. Explain Note  (AJAX POST)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def explain(request):
    """
    Explain the selected note in the requested style.

    POST params: note_id (int), style (beginner|detailed|example-based)
    Returns JSON: {status, explanation}
    """
    note_id = request.POST.get("note_id", "").strip()
    style   = request.POST.get("style", "beginner").strip()

    if not note_id or not note_id.isdigit():
        return _json_err("Invalid note selected.")

    note = get_object_or_404(Note, pk=int(note_id), user=request.user)

    try:
        explanation = explain_note(note.title, note.content, style)
    except AIServiceError as exc:
        return _json_err(str(exc))

    log_activity(request.user, 'AI_EXPLAIN', f"Explained note '{note.title}' ({style})")

    return _json_ok({"note_title": note.title, "explanation": explanation})


# ─────────────────────────────────────────────────────────────────────────────
# 6. Generate Quiz from Note
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def ai_generate_quiz(request):
    """
    Generate a quiz from a note using AI, validate the output,
    and save it using the existing Quiz + Question models.

    POST params: note_id (int), count (5|10|15)
    On success: redirects to the new quiz detail page.
    On failure (AJAX request): returns JSON error.
    """
    note_id = request.POST.get("note_id", "").strip()
    raw_count = request.POST.get("count", "5").strip()

    if not note_id or not note_id.isdigit():
        return _json_err("Invalid note selected.")

    try:
        count = int(raw_count)
    except ValueError:
        count = 5

    note = get_object_or_404(Note, pk=int(note_id), user=request.user)

    try:
        quiz_data = generate_quiz(note.title, note.content, count)
    except AIServiceError as exc:
        # If it was an AJAX call return JSON; otherwise redirect with message
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return _json_err(str(exc))
        messages.error(request, str(exc))
        return redirect('notes:note_detail', pk=note.pk)

    # Save the quiz using existing Quiz + Question models
    quiz = Quiz.objects.create(
        user=request.user,
        source_note=note,
        title=quiz_data["title"],
        total_questions=len(quiz_data["questions"]),
    )

    for q in quiz_data["questions"]:
        Question.objects.create(
            quiz=quiz,
            question_text=q["question"],
            options=q["options"],          # JSONField — list of 4 strings
            correct_answer=q["correct_answer"],
            explanation=q["explanation"],
        )

    log_activity(
        request.user,
        'AI_QUIZ_GENERATED',
        f"Generated quiz '{quiz.title}' ({len(quiz_data['questions'])} questions) from note '{note.title}'"
    )

    messages.success(
        request,
        f"Quiz '{quiz.title}' generated with {len(quiz_data['questions'])} questions! You can take it now."
    )

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return _json_ok({
            "quiz_id": quiz.pk,
            "quiz_title": quiz.title,
            "question_count": len(quiz_data["questions"]),
            "quiz_url": f"/quizzes/{quiz.pk}/",
        })

    return redirect('quizzes:quiz_detail', pk=quiz.pk)


# ─────────────────────────────────────────────────────────────────────────────
# 7. Generate Flashcards from Note
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def ai_generate_flashcards(request):
    """
    Generate flashcards from a note using AI, validate, and save
    using the existing Flashcard model.

    POST params: note_id (int), count (5|10|15)
    On success: redirects to flashcard list.
    """
    note_id   = request.POST.get("note_id", "").strip()
    raw_count = request.POST.get("count", "5").strip()

    if not note_id or not note_id.isdigit():
        return _json_err("Invalid note selected.")

    try:
        count = int(raw_count)
    except ValueError:
        count = 5

    note = get_object_or_404(Note, pk=int(note_id), user=request.user)

    try:
        cards_data = generate_flashcards(note.title, note.content, count)
    except AIServiceError as exc:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return _json_err(str(exc))
        messages.error(request, str(exc))
        return redirect('notes:note_detail', pk=note.pk)

    # Save using existing Flashcard model (no duplicate model)
    created_count = 0
    for card in cards_data:
        Flashcard.objects.create(
            user=request.user,
            source_note=note,
            front=card["front"],
            back=card["back"],
        )
        created_count += 1

    log_activity(
        request.user,
        'AI_FLASHCARDS_GENERATED',
        f"Generated {created_count} flashcards from note '{note.title}'"
    )

    messages.success(
        request,
        f"{created_count} flashcards generated from '{note.title}'! You can review them now."
    )

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return _json_ok({
            "count": created_count,
            "flashcard_url": "/quizzes/flashcards/",
        })

    return redirect('quizzes:flashcard_list')


# ─────────────────────────────────────────────────────────────────────────────
# 8. Personalised Study Recommendation  (AJAX POST)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def recommend(request):
    """
    Build anonymised study data for the current user and ask the AI
    for personalised study recommendations.

    Returns JSON: {status, recommendations: [...], overall_tip}

    Security: only aggregated counts and topic names are collected.
    No passwords, emails, or credentials are ever sent to the AI provider.
    """
    study_data = build_study_data_for_user(request.user)

    result = get_study_recommendation(study_data)

    log_activity(request.user, 'AI_RECOMMENDATION', "Requested personalised study recommendation")

    return _json_ok({
        "recommendations": result["recommendations"],
        "overall_tip": result["overall_tip"],
    })


# ─────────────────────────────────────────────────────────────────────────────
# 9. Dashboard AI Recommendation Widget  (AJAX GET)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def dashboard_recommendation(request):
    """
    Lightweight endpoint consumed by the dashboard widget via fetch().
    Returns a single quick recommendation or tip as JSON.
    Gracefully returns a fallback if AI is unavailable.
    """
    study_data = build_study_data_for_user(request.user)
    result     = get_study_recommendation(study_data)

    recs = result.get("recommendations", [])
    tip  = result.get("overall_tip", "")

    # Build a single human-readable sentence for the dashboard widget
    if recs:
        top = recs[0]
        widget_text = (
            f"Recommended: spend <strong>{top['duration_minutes']} minutes</strong> "
            f"on <strong>{top['subject']}</strong> — {top['activity']}. "
            f"<em>{top['reason']}</em>"
        )
    elif tip:
        widget_text = tip
    else:
        widget_text = (
            "Keep up your study routine! Add tasks and take quizzes "
            "to unlock personalised recommendations."
        )

    return JsonResponse({"widget_text": widget_text, "recommendations": recs, "overall_tip": tip})
