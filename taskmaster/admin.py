from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'assigned_to',
        'parent',
        'status',
        'reward',
        'due_date',
        'created_at',
        'completed_at',
    )
    list_filter = ('status', 'due_date', 'parent')
    search_fields = ('title', 'assigned_to__username', 'parent__username')
    readonly_fields = ('created_at', 'completed_at')

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'reward', 'due_date')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'parent')
        }),
        ('Status', {
            'fields': ('status', 'created_at', 'completed_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        # Optional: if you want to set parent automatically for new tasks created by admin user
        # Uncomment if needed
        # if not change and not obj.parent:
        #     obj.parent = request.user
        super().save_model(request, obj, form, change)
