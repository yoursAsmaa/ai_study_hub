from django.db import models
from django.contrib.auth.models import User
from notes.models import Category

class Resource(models.Model):
    TYPE_ARTICLE = 'ARTICLE'
    TYPE_VIDEO = 'VIDEO'
    TYPE_COURSE = 'COURSE'
    TYPE_DOCS = 'DOCS'
    TYPE_WEBSITE = 'WEBSITE'
    TYPE_BOOK = 'BOOK'
    TYPE_OTHER = 'OTHER'

    RESOURCE_TYPE_CHOICES = [
        (TYPE_ARTICLE, 'Article'),
        (TYPE_VIDEO, 'Video'),
        (TYPE_COURSE, 'Course'),
        (TYPE_DOCS, 'Documentation'),
        (TYPE_WEBSITE, 'Website'),
        (TYPE_BOOK, 'Book'),
        (TYPE_OTHER, 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resources')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='resources')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    link = models.URLField(max_length=500)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES, default=TYPE_ARTICLE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Resource'
        verbose_name_plural = 'Resources'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'resource_type']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"
