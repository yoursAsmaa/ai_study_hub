from django.contrib import admin
from .models import Resource

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'resource_type', 'link', 'created_at')
    search_fields = ('title', 'description', 'link', 'user__username')
    list_filter = ('resource_type', 'category', 'created_at')
