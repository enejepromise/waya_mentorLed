from django.contrib import admin
from .models import NotificationSettings, RewardSettings


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ('full_name_user', 'chore_completion', 'reward_redemption', 'chore_reminder', 'weekly_summary')
    search_fields = ('user__full_name', 'user__email')

    def full_name_user(self, obj):
        return obj.user.full_name
    full_name_user.short_description = 'Full Name (User)'


@admin.register(RewardSettings)
class RewardSettingsAdmin(admin.ModelAdmin):
    list_display = ('full_name_user', 'reward_approval_required', 'max_daily_reward', 'allow_savings')
    search_fields = ('user__full_name', 'user__email')

    def full_name_user(self, obj):
        return obj.user.full_name
    full_name_user.short_description = 'Full Name (User)'