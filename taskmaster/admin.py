from django.contrib import admin
from .models import Chore

# @admin.register(Chore)
# class ChoreAdmin(admin.ModelAdmin):
#     list_display = ('title', 'parent_name', 'child_name', 'status', 'due_date', 'created_at')
#     list_filter = ('status', 'due_date', 'created_at', 'category')
#     search_fields = (
#         'title',
#         'description',
#         'assigned_to__name',
#         'parent__full_name',  
#     )
#     ordering = ('-created_at',)
#     readonly_fields = ('created_at', 'completed_at')

#     fieldsets = (
#         (None, {
#             'fields': ('title', 'description', 'category', 'reward')
#         }),
#         ('Assignment Info', {
#             'fields': ('parent', 'assigned_to', 'due_date')
#         }),
#         ('Status Info', {
#             'fields': ('status', 'created_at', 'completed_at')
#         }),
#     )

#     def parent_name(self, obj):
#         return obj.parent.full_name
#     parent_name.short_description = 'Parent'

#     def child_name(self, obj):
#         return obj.assigned_to.name
#     child_name.short_description = 'Child'
