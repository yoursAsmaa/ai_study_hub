from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q, Max, Avg, Sum

from planner.models import Task
from notes.models import Note
from resources.models import Resource
from quizzes.models import Quiz, StudySession
from .models import Activity


@login_required
def index(request):
    user_tasks = Task.objects.filter(user=request.user)

    total_tasks     = user_tasks.count()
    completed_tasks = user_tasks.filter(
        Q(status=Task.STATUS_COMPLETED) | Q(is_completed=True)
    ).count()
    pending_tasks   = user_tasks.filter(
        Q(status=Task.STATUS_PENDING) | Q(status=Task.STATUS_IN_PROGRESS),
        is_completed=False,
    ).count()
    overdue_tasks   = user_tasks.filter(
        due_date__lt=timezone.now(), is_completed=False
    ).exclude(status=Task.STATUS_COMPLETED).count()

    total_notes     = Note.objects.filter(user=request.user).count()
    total_resources = Resource.objects.filter(user=request.user).count()
    completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0

    upcoming_tasks      = user_tasks.filter(
        is_completed=False
    ).exclude(status=Task.STATUS_COMPLETED).order_by('due_date')[:5]

    recent_activities   = Activity.objects.filter(user=request.user)[:8]

    # ── Quiz analytics ────────────────────────────────────────────────────
    user_quizzes        = Quiz.objects.filter(user=request.user)
    total_quizzes       = user_quizzes.count()
    completed_quizzes   = user_quizzes.filter(completed=True)
    avg_score           = completed_quizzes.aggregate(avg=Avg('score'))['avg']
    average_quiz_score  = round(avg_score, 1) if avg_score is not None else 0.0
    best_score          = completed_quizzes.aggregate(best=Max('score'))['best']
    best_quiz_score     = round(best_score, 1) if best_score is not None else 0.0

    # ── Study sessions analytics ──────────────────────────────────────────
    user_sessions       = StudySession.objects.filter(user=request.user, end_time__isnull=False)
    total_study_sessions= user_sessions.count()
    total_study_time    = user_sessions.aggregate(total=Sum('duration_minutes'))['total'] or 0

    # ── Static fallback AI tip (shown before the widget loads via fetch) ──
    # This is a lightweight rule-based tip — the live AI recommendation is
    # fetched asynchronously by the dashboard JS after page load.
    if overdue_tasks > 0:
        static_ai_tip = (
            f"You have <strong>{overdue_tasks} overdue task{'s' if overdue_tasks > 1 else ''}</strong>. "
            "Tackle those first before starting new study sessions."
        )
    elif average_quiz_score > 0 and average_quiz_score < 60:
        static_ai_tip = (
            f"Your average quiz score is <strong>{average_quiz_score}%</strong>. "
            "Consider reviewing your notes and retaking the quizzes to strengthen retention."
        )
    elif pending_tasks > 0:
        static_ai_tip = (
            f"You have <strong>{pending_tasks} pending task{'s' if pending_tasks > 1 else ''}</strong>. "
            "Focus on high-priority items to stay ahead of your deadlines."
        )
    elif total_notes == 0:
        static_ai_tip = (
            "Start by creating notes for your subjects — you can then generate "
            "AI-powered quizzes and flashcards from them instantly."
        )
    else:
        static_ai_tip = (
            "Great work keeping up with your studies! "
            "Click <strong>Get AI Recommendation</strong> for a personalised study plan."
        )

    context = {
        'total_tasks':          total_tasks,
        'completed_tasks':      completed_tasks,
        'pending_tasks':        pending_tasks,
        'overdue_tasks':        overdue_tasks,
        'total_notes':          total_notes,
        'total_resources':      total_resources,
        'completion_rate':      completion_rate,
        'upcoming_tasks':       upcoming_tasks,
        'recent_activities':    recent_activities,
        'total_quizzes':        total_quizzes,
        'average_quiz_score':   average_quiz_score,
        'best_quiz_score':      best_quiz_score,
        'total_study_sessions': total_study_sessions,
        'total_study_time':     total_study_time,
        # AI widget
        'static_ai_tip':        static_ai_tip,
    }

    return render(request, 'dashboard/index.html', context)
