from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'university', 'major', 'phone', 'is_email_verified', 'created_at')
    search_fields = ('user__username', 'user__email', 'university', 'major')
    list_filter = ('is_email_verified', 'created_at')
