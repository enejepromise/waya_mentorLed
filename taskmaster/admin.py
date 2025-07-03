from django.contrib import admin
from .models import Chore

@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'assigned_to', 'parent', 'status', 'due_date', 'reward', 'category', 'created_at', 'completed_at'
    )
    list_filter = ('status', 'category', 'due_date')
    search_fields = ('title', 'description', 'assigned_to__username', 'parent__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'completed_at')
