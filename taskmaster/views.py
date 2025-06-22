from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Task
from .serializers import (
    TaskCreateUpdateSerializer,
    TaskReadSerializer,
    TaskStatusUpdateSerializer,
)
from .permissions import IsParentOfTask, IsChildAssignedToTask  # Custom permissions


class TaskCreateView(generics.CreateAPIView):
    serializer_class = TaskCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        """Pass the request to the serializer for validation."""
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def perform_create(self, serializer):
        """Attach the parent to the task after validation."""
        parent = self.request.user
        serializer.save(parent=parent)


class TaskListView(generics.ListAPIView):
    serializer_class = TaskReadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(parent=user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsParentOfTask]
    queryset = Task.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class TaskStatusUpdateView(generics.UpdateAPIView):
    serializer_class = TaskStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Task.objects.all()

    def get_object(self):
        return super().get_object()

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ChildChoreListView(generics.ListAPIView):
    serializer_class = TaskReadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        child_id = self.request.query_params.get('childId')
        user = self.request.user
        if not child_id:
            return Task.objects.none()
        return Task.objects.filter(parent=user, assigned_to__id=child_id)


class ChildChoreStatusUpdateView(generics.UpdateAPIView):
    serializer_class = TaskStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsChildAssignedToTask]
    queryset = Task.objects.all()

    def get_object(self):
        task = super().get_object()
        self.check_object_permissions(self.request, task)
        return task