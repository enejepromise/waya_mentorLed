from django.contrib import admin
from taskmaster.models import Chore
from children.models import Child


# @admin.register(Chore)
# class ChoreAdmin(admin.ModelAdmin):
#     list_display = ('title', 'name_child', 'full_name_parent', 'status', 'reward', 'due_date')
#     list_filter = ('status', 'due_date')
#     search_fields = ('title', 'assigned_to__name', 'parent__full_name')

#     def name_child(self, obj):
#         return obj.assigned_to.name
#     name_child.short_description = 'Name (Child)'

#     def full_name_parent(self, obj):
#         return obj.parent.full_name
#     full_name_parent.short_description = 'Full Name (Parent)'


#