from django.contrib import admin
from .models import  Reward
from users.models import User
from children.models import Child

# Register models from settings_waya
@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('user', 'reward_approval_required', 'max_daily_reward', 'allow_savings')

