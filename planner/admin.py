from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'priority', 'status', 'due_date', 'is_completed')
    search_fields = ('title', 'description', 'user__username')
    list_filter = ('priority', 'status', 'is_completed', 'category', 'due_date')
