from django.urls import path
from .views import (
    ChoreCreateView,
    ChoreListView,
    ChoreDetailView,
    ChoreStatusUpdateView,
    ChoreDeleteView,
    ChildChoreListView,
    ChildChoreStatusUpdateView,
    ChoreStatusBreakdownView,
)

urlpatterns = [
    # Chore CRUD and parent status update
    path("chores/", ChoreListView.as_view(), name="chore-list"),
    path("chores/create/", ChoreCreateView.as_view(), name="chore-create"),
    path("chores/<uuid:pk>/", ChoreDetailView.as_view(), name="chore-detail"),
    path("chores/<uuid:pk>/delete/", ChoreDeleteView.as_view(), name="chore-delete"),
    path("chores/<uuid:pk>/status/", ChoreStatusUpdateView.as_view(), name="chore-status-update"),

    # Chore summary (used for pie chart)
    path("chores/summary/", ChoreStatusBreakdownView.as_view(), name="chore-summary"),

    # Child-specific chore actions
    path("children/chores/", ChildChoreListView.as_view(), name="child-chore-list"),
    path("children/chores/<uuid:pk>/status/", ChildChoreStatusUpdateView.as_view(), name="child-chore-status-update"),
]