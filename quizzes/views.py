from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q, Max, Avg

from .models import Quiz, Question, Flashcard, StudySession
from .forms import QuizForm, QuestionForm, FlashcardForm, StartSessionForm
from dashboard.models import log_activity
from notes.models import Category

# =====================================================================
# QUIZ VIEWS
# =====================================================================

@login_required
def quiz_list(request):
    quizzes = Quiz.objects.filter(user=request.user).order_by('-created_at')

    # Search Query
    search_query = request.GET.get('q', '').strip()
    if search_query:
        quizzes = quizzes.filter(title__icontains=search_query)

    paginator = Paginator(quizzes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'quizzes/quiz_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'total_count': quizzes.count(),
    })


@login_required
def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, user=request.user)
    questions = quiz.questions.all()
    return render(request, 'quizzes/quiz_detail.html', {
        'quiz': quiz,
        'questions': questions,
    })


@login_required
def quiz_create(request):
    if request.method == 'POST':
        form = QuizForm(request.POST, user=request.user)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.user = request.user
            quiz.save()
            log_activity(request.user, 'QUIZ_CREATED', f"Created quiz '{quiz.title}'")
            messages.success(request, f"Quiz '{quiz.title}' created! Now add some questions.")
            return redirect('quizzes:quiz_detail', pk=quiz.pk)
    else:
        form = QuizForm(user=request.user)

    return render(request, 'quizzes/quiz_form.html', {'form': form, 'title': 'Create New Quiz'})


@login_required
def quiz_edit(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, user=request.user)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz, user=request.user)
        if form.is_valid():
            quiz = form.save()
            log_activity(request.user, 'QUIZ_UPDATED', f"Updated quiz '{quiz.title}'")
            messages.success(request, f"Quiz '{quiz.title}' updated successfully!")
            return redirect('quizzes:quiz_detail', pk=quiz.pk)
    else:
        form = QuizForm(instance=quiz, user=request.user)

    return render(request, 'quizzes/quiz_form.html', {'form': form, 'quiz': quiz, 'title': 'Edit Quiz'})


@login_required
def quiz_delete(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, user=request.user)
    if request.method == 'POST':
        title = quiz.title
        quiz.delete()
        log_activity(request.user, 'QUIZ_DELETED', f"Deleted quiz '{title}'")
        messages.success(request, f"Quiz '{title}' deleted successfully!")
        return redirect('quizzes:quiz_list')

    return render(request, 'quizzes/quiz_confirm_delete.html', {'quiz': quiz})


@login_required
def question_create(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id, user=request.user)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            options_list = [
                form.cleaned_data['option_a'].strip(),
                form.cleaned_data['option_b'].strip(),
                form.cleaned_data['option_c'].strip(),
                form.cleaned_data['option_d'].strip(),
            ]
            correct_val = form.cleaned_data[f"option_{form.cleaned_data['correct_option'].lower()}"].strip()

            Question.objects.create(
                quiz=quiz,
                question_text=form.cleaned_data['question_text'].strip(),
                options=options_list,
                correct_answer=correct_val,
                explanation=form.cleaned_data['explanation'].strip()
            )
            
            # Recalculate quiz counters
            quiz.total_questions = quiz.questions.count()
            quiz.save()

            messages.success(request, "Question added successfully!")
            return redirect('quizzes:quiz_detail', pk=quiz.id)
    else:
        form = QuestionForm()

    return render(request, 'quizzes/question_form.html', {'form': form, 'quiz': quiz})


@login_required
def question_delete(request, quiz_id, pk):
    quiz = get_object_or_404(Quiz, pk=quiz_id, user=request.user)
    question = get_object_or_404(Question, pk=pk, quiz=quiz)
    if request.method == 'POST':
        question.delete()
        quiz.total_questions = quiz.questions.count()
        quiz.save()
        messages.success(request, "Question removed.")
    return redirect('quizzes:quiz_detail', pk=quiz.id)


@login_required
def quiz_take(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, user=request.user)
    questions = quiz.questions.all()
    if not questions.exists():
        messages.warning(request, "This quiz has no questions yet.")
        return redirect('quizzes:quiz_detail', pk=quiz.id)

    return render(request, 'quizzes/quiz_take.html', {
        'quiz': quiz,
        'questions': questions,
    })


@login_required
def quiz_submit(request, pk):
    if request.method != 'POST':
        return redirect('quizzes:quiz_list')

    quiz = get_object_or_404(Quiz, pk=pk, user=request.user)
    questions = quiz.questions.all()

    correct_count = 0
    total = questions.count()

    for q in questions:
        ans_key = f"question_{q.id}"
        user_ans = request.POST.get(ans_key, '').strip()
        q.user_answer = user_ans
        
        is_correct = (user_ans == q.correct_answer)
        q.is_correct = is_correct
        q.save()

        if is_correct:
            correct_count += 1

    percentage = (correct_count / total * 100) if total > 0 else 0.0

    quiz.score = percentage
    quiz.correct_answers = correct_count
    quiz.total_questions = total
    quiz.completed = True
    quiz.save()

    log_activity(request.user, 'QUIZ_SUBMITTED', f"Submitted quiz '{quiz.title}' with score {percentage:.1f}%")
    messages.success(request, "Quiz submitted successfully!")
    return redirect('quizzes:quiz_result', pk=quiz.id)


@login_required
def quiz_result(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, user=request.user)
    if not quiz.completed:
        return redirect('quizzes:quiz_take', pk=quiz.id)

    questions = quiz.questions.all()
    incorrect_answers = quiz.total_questions - quiz.correct_answers

    return render(request, 'quizzes/quiz_result.html', {
        'quiz': quiz,
        'questions': questions,
        'incorrect_answers': incorrect_answers,
    })


# =====================================================================
# FLASHCARD VIEWS
# =====================================================================

@login_required
def flashcard_list(request):
    flashcards = Flashcard.objects.filter(user=request.user)

    known_filter = request.GET.get('known', '').strip()
    if known_filter == '1':
        flashcards = flashcards.filter(known=True)
    elif known_filter == '0':
        flashcards = flashcards.filter(known=False)

    paginator = Paginator(flashcards, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'quizzes/flashcard_list.html', {
        'page_obj': page_obj,
        'known_filter': known_filter,
        'total_count': flashcards.count(),
    })


@login_required
def flashcard_review(request):
    deck = Flashcard.objects.filter(user=request.user, known=False).order_by('?')
    return render(request, 'quizzes/flashcard_review.html', {'deck': deck})


@login_required
def flashcard_create(request):
    if request.method == 'POST':
        form = FlashcardForm(request.POST, user=request.user)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = request.user
            card.save()
            log_activity(request.user, 'FLASHCARD_CREATED', f"Created flashcard '{card.front[:30]}'")
            messages.success(request, "Flashcard added successfully!")
            return redirect('quizzes:flashcard_list')
    else:
        form = FlashcardForm(user=request.user)

    return render(request, 'quizzes/flashcard_form.html', {'form': form, 'title': 'Create Flashcard'})


@login_required
def flashcard_edit(request, pk):
    card = get_object_or_404(Flashcard, pk=pk, user=request.user)
    if request.method == 'POST':
        form = FlashcardForm(request.POST, instance=card, user=request.user)
        if form.is_valid():
            card = form.save()
            messages.success(request, "Flashcard updated successfully!")
            return redirect('quizzes:flashcard_list')
    else:
        form = FlashcardForm(instance=card, user=request.user)

    return render(request, 'quizzes/flashcard_form.html', {'form': form, 'card': card, 'title': 'Edit Flashcard'})


@login_required
def flashcard_delete(request, pk):
    card = get_object_or_404(Flashcard, pk=pk, user=request.user)
    if request.method == 'POST':
        card.delete()
        messages.success(request, "Flashcard deleted successfully.")
        return redirect('quizzes:flashcard_list')

    return render(request, 'quizzes/flashcard_confirm_delete.html', {'card': card})


@login_required
def flashcard_toggle_known(request, pk):
    if request.method != 'POST':
        return redirect('quizzes:flashcard_list')

    card = get_object_or_404(Flashcard, pk=pk, user=request.user)
    card.known = not card.known
    card.save()
    
    state = "known" if card.known else "needs review"
    messages.success(request, f"Flashcard marked as {state}.")

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('quizzes:flashcard_list')


# =====================================================================
# STUDY SESSION VIEWS
# =====================================================================

@login_required
def session_dashboard(request):
    # Check for active study session
    active_session = StudySession.objects.filter(user=request.user, end_time__isnull=True).first()
    
    # Study History
    history = StudySession.objects.filter(user=request.user, end_time__isnull=False).order_by('-start_time')
    
    # Filter subject/category
    subject_filter = request.GET.get('subject', '').strip()
    if subject_filter:
        history = history.filter(subject__icontains=subject_filter)

    category_filter = request.GET.get('category', '').strip()
    if category_filter.isdigit():
        history = history.filter(category_id=category_filter)

    paginator = Paginator(history, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(user=request.user)
    form = StartSessionForm(user=request.user)

    return render(request, 'planner/study_session.html', {
        'active_session': active_session,
        'page_obj': page_obj,
        'categories': categories,
        'category_filter': category_filter,
        'subject_filter': subject_filter,
        'form': form,
    })


@login_required
def session_start(request):
    if request.method != 'POST':
        return redirect('quizzes:session_list')

    # Check active session protection
    active = StudySession.objects.filter(user=request.user, end_time__isnull=True).exists()
    if active:
        messages.warning(request, "You already have an active study session running.")
        return redirect('quizzes:session_list')

    form = StartSessionForm(request.POST, user=request.user)
    if form.is_valid():
        session = form.save(commit=False)
        session.user = request.user
        session.start_time = timezone.now()
        session.save()
        log_activity(request.user, 'SESSION_STARTED', f"Started study session for '{session.subject or 'General'}'")
        messages.success(request, "Study session started! Happy studying!")
    
    return redirect('quizzes:session_list')


@login_required
def session_end(request):
    if request.method != 'POST':
        return redirect('quizzes:session_list')

    active_session = StudySession.objects.filter(user=request.user, end_time__isnull=True).first()
    if not active_session:
        messages.warning(request, "No active study session found to end.")
        return redirect('quizzes:session_list')

    active_session.end_time = timezone.now()
    # Calculate duration server side
    delta = active_session.end_time - active_session.start_time
    duration_min = round(delta.total_seconds() / 60.0)
    active_session.duration_minutes = max(1, int(duration_min)) # minimum 1 minute
    active_session.save()

    log_activity(request.user, 'SESSION_ENDED', f"Ended study session ({active_session.duration_minutes} mins)")
    messages.success(request, f"Well done! Study session logged: {active_session.duration_minutes} minutes.")

    return redirect('quizzes:session_list')


@login_required
def session_history(request):
    history = StudySession.objects.filter(user=request.user, end_time__isnull=False).order_by('-start_time')
    
    paginator = Paginator(history, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'planner/study_session_history.html', {'page_obj': page_obj})
