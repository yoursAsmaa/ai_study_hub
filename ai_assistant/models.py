from django.db import models
from django.contrib.auth.models import User


class ChatMessage(models.Model):
    """
    Stores a single AI chat exchange (one user question + one AI answer).
    History is per-user; users never see another user's messages.
    """
    ROLE_USER = 'user'
    ROLE_AI   = 'ai'

    ROLE_CHOICES = [
        (ROLE_USER, 'User'),
        (ROLE_AI,   'AI'),
    ]

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    role       = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        ordering            = ['created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"[{self.get_role_display()}] {self.user.username}: {self.content[:60]}"
