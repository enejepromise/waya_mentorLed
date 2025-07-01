from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Child

# @admin.register(Child)
# class ChildAdmin(admin.ModelAdmin):
#     list_display = ('username', 'name', 'parent', 'created_at')
#     list_filter = ('parent', 'created_at')
#     search_fields = ('username', 'name', 'parent__username', 'parent__email')
#     readonly_fields = ('created_at',)
