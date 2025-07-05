# chorequest/urls.py
from django.urls import path
from .views import (
    ChildChoreListView,
    ChildChoreStatusUpdateView,
    RedeemRewardView
)

urlpatterns = [
    path('chores/', ChildChoreListView.as_view(), name='child-chores'),
    path('chores/<uuid:pk>/status/', ChildChoreStatusUpdateView.as_view(), name='child-update-status'),
    path('chores/<uuid:chore_id>/redeem/', RedeemRewardView.as_view(), name='redeem-reward'),
]
