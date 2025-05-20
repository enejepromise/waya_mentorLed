from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from allauth.socialaccount.models import SocialApp

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'fullname', 'is_active', 'is_staff')
    search_fields = ('email', 'fullname')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'fullname', 'password', 'avatar', 'terms_accepted')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('created_at',)}),  # <-- Note the trailing comma
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'fullname', 'password1', 'password2', 'terms_accepted', 'avatar')}
        ),
    )

# Optional: register SocialApp so you can add Google config from admin
# admin.site.register(SocialApp)
