from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Chore
from notifications.models import Notification
from .serializers import (
    ChoreCreateUpdateSerializer,
    ChoreReadSerializer,
    ChoreStatusUpdateSerializer,
)
from .permissions import IsParentOfChore, IsChildAssignedToChore
from .models import notify_parent_realtime


class ChoreCreateView(generics.CreateAPIView):
    """
    POST /api/chores/ - Create a new chore
    """
    serializer_class = ChoreCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        return {"request": self.request}

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        if serializer.is_valid():
            chore = serializer.save(parent=request.user)
            return Response(ChoreReadSerializer(chore).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChoreListView(generics.ListAPIView):
    """
    GET /api/chores/ - List chores (filterable by status, assignedTo, category)
    """
    serializer_class = ChoreReadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Chore.objects.filter(parent=user)

        status_param = self.request.query_params.get("status")
        child_id = self.request.query_params.get("assignedTo")
        category = self.request.query_params.get("category")

        if status_param:
            queryset = queryset.filter(status=status_param)
        if child_id:
            queryset = queryset.filter(assigned_to__id=child_id)

        return queryset

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {"detail": f"Server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChoreDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/chores/{choreId}/ — Chore detail  
    PUT /api/chores/{choreId}/update/ — Update chore  
    DELETE /api/chores/{choreId}/delete/ — Delete chore
    """
    queryset = Chore.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsParentOfChore]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ChoreReadSerializer
        return ChoreCreateUpdateSerializer


class ChoreStatusUpdateView(generics.UpdateAPIView):
    """
    PATCH /api/chores/{id}/status/ - Update chore status (parent only)
    """
    serializer_class = ChoreStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsParentOfChore]
    queryset = Chore.objects.all()

    def patch(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            previous_status = instance.status
            response = super().patch(request, *args, **kwargs)

            if instance.status == Chore.STATUS_COMPLETED and previous_status != Chore.STATUS_COMPLETED:
                Notification.objects.create(
                    parent=instance.parent,
                    type="chore_completed",
                    title="Chore Completed",
                    message=f"{instance.assigned_to.username} completed '{instance.title}'",
                    related_id=instance.id
                )
                notify_parent_realtime(
                    instance.parent,
                    f"{instance.assigned_to.username} completed '{instance.title}'",
                    instance.id
                )

            return response
        except Chore.DoesNotExist:
            return Response({"detail": "Chore not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"Server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChildChoreListView(generics.ListAPIView):
    """
    GET /api/children/chores/?childId=<uuid>
    Returns chore list for a specific child (used in child dashboard)
    """
    serializer_class = ChoreReadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        child_id = self.request.query_params.get("childId")
        user = self.request.user
        if not child_id:
            return Chore.objects.none()
        return Chore.objects.filter(parent=user, assigned_to__id=child_id)


class ChildChoreStatusUpdateView(generics.UpdateAPIView):
    """
    PATCH — Child updates their own chore status
    """
    serializer_class = ChoreStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsChildAssignedToChore]
    queryset = Chore.objects.all()

    def get_object(self):
        chore = super().get_object()
        self.check_object_permissions(self.request, chore)
        return chore

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        previous_status = instance.status
        response = super().patch(request, *args, **kwargs)

        if instance.status == Chore.STATUS_COMPLETED and previous_status != Chore.STATUS_COMPLETED:
            Notification.objects.create(
                parent=instance.parent,
                type="chore_completed",
                title="Chore Completed",
                message=f"{instance.assigned_to.username} completed '{instance.title}'",
                related_id=instance.id
            )
            notify_parent_realtime(
                instance.parent,
                f"{instance.assigned_to.username} completed '{instance.title}'",
                instance.id
            )

        return response


class ChoreDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/chores/{id}/ - Delete a chore
    """
    queryset = Chore.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsParentOfChore]

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Chore.DoesNotExist:
            return Response({"detail": "Chore not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"Server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChoreStatusBreakdownView(APIView):
    """
    GET /api/chores/summary/ - Returns count of completed, pending, missed, and total chores
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        chores = Chore.objects.filter(parent=user)

        summary = {
            'pending': chores.filter(status=Chore.STATUS_PENDING).count(),
            'completed': chores.filter(status=Chore.STATUS_COMPLETED).count(),
            'missed': chores.filter(status=Chore.STATUS_MISSED).count(),
            'total': chores.count()
        }
        return Response(summary, status=status.HTTP_200_OK)
