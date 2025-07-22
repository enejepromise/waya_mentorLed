from django.urls import path
from .views import ChoreQuestViewSet

# Define the base viewset views for list/retrieve and the custom actions
chorequest_list = ChoreQuestViewSet.as_view({
    'get': 'list',
})

chorequest_detail = ChoreQuestViewSet.as_view({
    'get': 'retrieve',
})

chorequest_complete = ChoreQuestViewSet.as_view({
    'post': 'mark_complete',
})

chorequest_redeem = ChoreQuestViewSet.as_view({
    'post': 'redeem_reward',
})

urlpatterns = [
    path('chorequest/', chorequest_list, name='chorequest-list'),
    path('chorequest/<uuid:pk>/', chorequest_detail, name='chorequest-detail'),
    path('chorequest/complete/', chorequest_complete, name='chorequest-complete'),
    path('chorequest/redeem/', chorequest_redeem, name='chorequest-redeem'),
]
