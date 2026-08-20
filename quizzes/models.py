from django.db import models
from django.contrib.auth.models import User
from notes.models import Note, Category

class Quiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    source_note = models.ForeignKey(Note, on_delete=models.SET_NULL, null=True, blank=True, related_name='quizzes')
    title = models.CharField(max_length=255)
    score = models.FloatField(default=0.0)
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} (Score: {self.score:.1f}%)"


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    options = models.JSONField(default=list)  # List of option strings e.g. ["A", "B", "C", "D"]
    correct_answer = models.CharField(max_length=255)
    user_answer = models.CharField(max_length=255, blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)
    is_correct = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        return f"Q: {self.question_text[:50]}..."


class Flashcard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flashcards')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True, related_name='flashcards')
    source_note = models.ForeignKey(Note, on_delete=models.SET_NULL, null=True, blank=True, related_name='flashcards')
    front = models.TextField()
    back = models.TextField()
    known = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Flashcard'
        verbose_name_plural = 'Flashcards'
        ordering = ['known', '-created_at']

    def __str__(self):
        return f"Flashcard: {self.front[:30]}..."


class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='study_sessions')
    subject = models.CharField(max_length=150, blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=0)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Study Session'
        verbose_name_plural = 'Study Sessions'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['user', '-start_time']),
        ]

    def __str__(self):
        return f"Study Session ({self.subject or 'General'}) - {self.duration_minutes} mins"
