from django.urls import path
from . import views
from .pdf_views import quiz_result_pdf, study_sessions_pdf

app_name = 'quizzes'

urlpatterns = [
    # Quizzes
    path('', views.quiz_list, name='quiz_list'),
    path('create/', views.quiz_create, name='quiz_create'),
    path('<int:pk>/', views.quiz_detail, name='quiz_detail'),
    path('<int:pk>/edit/', views.quiz_edit, name='quiz_edit'),
    path('<int:pk>/delete/', views.quiz_delete, name='quiz_delete'),

    # Questions CRUD
    path('<int:quiz_id>/questions/create/', views.question_create, name='question_create'),
    path('<int:quiz_id>/questions/<int:pk>/delete/', views.question_delete, name='question_delete'),

    # Quiz Play Flow
    path('<int:pk>/take/', views.quiz_take, name='quiz_take'),
    path('<int:pk>/submit/', views.quiz_submit, name='quiz_submit'),
    path('<int:pk>/result/', views.quiz_result, name='quiz_result'),

    # Flashcards
    path('flashcards/', views.flashcard_list, name='flashcard_list'),
    path('flashcards/create/', views.flashcard_create, name='flashcard_create'),
    path('flashcards/<int:pk>/edit/', views.flashcard_edit, name='flashcard_edit'),
    path('flashcards/<int:pk>/delete/', views.flashcard_delete, name='flashcard_delete'),
    path('flashcards/<int:pk>/toggle/', views.flashcard_toggle_known, name='flashcard_toggle_known'),
    path('flashcards/review/', views.flashcard_review, name='flashcard_review'),

    # Study Sessions
    path('sessions/', views.session_dashboard, name='session_list'),
    path('sessions/start/', views.session_start, name='session_start'),
    path('sessions/end/', views.session_end, name='session_end'),
    path('sessions/history/', views.session_history, name='session_history'),

    # PDF exports
    path('<int:pk>/result/pdf/', quiz_result_pdf, name='quiz_result_pdf'),
    path('sessions/export/pdf/', study_sessions_pdf, name='sessions_pdf'),
]
