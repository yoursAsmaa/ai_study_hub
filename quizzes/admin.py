from django.contrib import admin
from .models import Quiz, Question, Flashcard, StudySession

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'source_note', 'score', 'completed', 'created_at')
    search_fields = ('title', 'user__username')
    list_filter = ('completed', 'created_at')
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'question_text', 'correct_answer', 'is_correct')
    search_fields = ('question_text', 'correct_answer', 'explanation')

@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ('user', 'front', 'known', 'created_at')
    search_fields = ('front', 'back', 'user__username')
    list_filter = ('known', 'created_at')

@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'category', 'start_time', 'end_time', 'duration_minutes')
    search_fields = ('subject', 'notes', 'user__username')
    list_filter = ('category', 'start_time')
