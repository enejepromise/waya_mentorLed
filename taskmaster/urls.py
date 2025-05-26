from django.urls import path
from .views import (
    TaskCreateView,
    TaskListView,
    TaskDetailView,
    TaskStatusUpdateView,
    ChildChoreListView,
    ChildChoreStatusUpdateView,
)

urlpatterns = [
    path('tasks/create/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/', TaskListView.as_view(), name='task-list'),
    path('tasks/<uuid:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<uuid:pk>/status/', TaskStatusUpdateView.as_view(), name='task-status-update'),

    path('child-chores/', ChildChoreListView.as_view(), name='child-chore-list'),
    path('child-chores/<uuid:pk>/status/', ChildChoreStatusUpdateView.as_view(), name='child-chore-status-update'),
]
