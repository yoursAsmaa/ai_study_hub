from django.contrib import admin
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display  = ('user', 'role', 'short_content', 'created_at')
    list_filter   = ('role', 'created_at')
    search_fields = ('user__username', 'content')
    readonly_fields = ('user', 'role', 'content', 'created_at')
    ordering      = ('-created_at',)

    def short_content(self, obj):
        return obj.content[:80] + ('…' if len(obj.content) > 80 else '')
    short_content.short_description = 'Content'

    def has_add_permission(self, request):
        # Chat history is created by the app only, not by admins
        return False
