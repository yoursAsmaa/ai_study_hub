from django.contrib import admin
from .models import Activity

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'description', 'created_at')
    search_fields = ('user__username', 'action_type', 'description')
    list_filter = ('action_type', 'created_at')
