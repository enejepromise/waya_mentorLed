from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Task
from .serializers import (
    TaskCreateUpdateSerializer,
    TaskReadSerializer,
    TaskStatusUpdateSerializer,
)
from .permissions import IsParentOfTask, IsChildAssignedToTask


class TaskCreateView(generics.CreateAPIView):
    """POST /api/taskmaster/tasks/create/ — Create new task"""
    serializer_class = TaskCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def perform_create(self, serializer):
        parent = self.request.user
        serializer.save(parent=parent)


class TaskListView(generics.ListAPIView):
    """GET /api/taskmaster/tasks/ — List tasks with filters"""
    serializer_class = TaskReadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.filter(parent=user)

        # Filtering
        status_param = self.request.query_params.get("status")
        child_id = self.request.query_params.get("assignedTo")
        category = self.request.query_params.get("category")  # If you add category later

        if status_param:
            queryset = queryset.filter(status=status_param)
        if child_id:
            queryset = queryset.filter(assigned_to__id=child_id)

        return queryset


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/taskmaster/tasks/{taskId}/ — Task detail  
    PUT /api/taskmaster/tasks/{taskId}/update/ — Update task  
    DELETE /api/taskmaster/tasks/{taskId}/delete/ — Delete task
    """
    queryset = Task.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsParentOfTask]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TaskReadSerializer
        return TaskCreateUpdateSerializer


class TaskStatusUpdateView(generics.UpdateAPIView):
    """PATCH /api/taskmaster/tasks/{taskId}/status/ — Update task status"""
    serializer_class = TaskStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsParentOfTask]
    queryset = Task.objects.all()

    def get_object(self):
        task = super().get_object()
        self.check_object_permissions(self.request, task)
        return task

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ChildChoreListView(generics.ListAPIView):
    """GET chore list for specific child (e.g., used in child dashboard)"""
    serializer_class = TaskReadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        child_id = self.request.query_params.get("childId")
        user = self.request.user
        if not child_id:
            return Task.objects.none()
        return Task.objects.filter(parent=user, assigned_to__id=child_id)


class ChildChoreStatusUpdateView(generics.UpdateAPIView):
    """PATCH — Child updates their own task status (e.g., mark as completed)"""
    serializer_class = TaskStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsChildAssignedToTask]
    queryset = Task.objects.all()

    def get_object(self):
        task = super().get_object()
        self.check_object_permissions(self.request, task)
        return task
