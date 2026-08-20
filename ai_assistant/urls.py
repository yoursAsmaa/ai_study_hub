from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    # Main AI Study Coach page
    path('', views.index, name='index'),

    # Chat (AJAX POST)
    path('chat/', views.chat, name='chat'),
    path('chat/clear/', views.clear_chat, name='clear_chat'),

    # Note AI actions (AJAX POST — called from note_detail page)
    path('summarize/', views.summarize, name='summarize'),
    path('explain/', views.explain, name='explain'),

    # Quiz + Flashcard generation (POST → redirect on success)
    path('generate-quiz/', views.ai_generate_quiz, name='generate_quiz'),
    path('generate-flashcards/', views.ai_generate_flashcards, name='generate_flashcards'),

    # Recommendations
    path('recommend/', views.recommend, name='recommend'),
    path('dashboard-recommendation/', views.dashboard_recommendation, name='dashboard_recommendation'),
]
