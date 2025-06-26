from django.urls import path
from .views import (
    TaskCreateView,
    TaskListView,
    TaskDetailView,
    TaskStatusUpdateView,
    ChildChoreListView,
    ChildChoreStatusUpdateView,
    LegacyActivityListView,
    LegacyChoreListView,

)

urlpatterns = [
    # Parent Task Endpoints
    path('tasks/create/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/', TaskListView.as_view(), name='task-list'),
    path('tasks/<uuid:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<uuid:pk>/update/', TaskDetailView.as_view(), name='task-update'),
    path('tasks/<uuid:pk>/delete/', TaskDetailView.as_view(), name='task-delete'),
    path('tasks/<uuid:pk>/status/', TaskStatusUpdateView.as_view(), name='task-status-update'),
    path('activities/', LegacyActivityListView.as_view(), name='legacy-activities'),
    path('chores/', LegacyChoreListView.as_view(), name='legacy-chores'),

    # Child Chore Endpoints
    path('child-chores/', ChildChoreListView.as_view(), name='child-chore-list'),
    path('child-chores/<uuid:pk>/status/', ChildChoreStatusUpdateView.as_view(), name='child-chore-status-update'),
]
