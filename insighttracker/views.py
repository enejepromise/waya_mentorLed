from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from children.models import Child
from taskmaster.models import Chore
from .serializers import InsightChoreSerializer


class InsightChoreView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InsightChoreSerializer  # <-- This is required

    def get(self, request):
        parent = request.user

        total_chores = Chore.objects.filter(parent=parent).count()
        total_completed = Chore.objects.filter(parent=parent, status=Chore.STATUS_COMPLETED).count()
        total_pending = Chore.objects.filter(parent=parent, status=Chore.STATUS_PENDING).count()

        children = Child.objects.filter(parent=parent)
        child_activities = []

        for child in children:
            child_chores = Chore.objects.filter(parent=parent, assigned_to=child)
            activities = []

            total_earned = 0
            for chore in child_chores:
                status = chore.status
                amount = float(chore.reward)

                if status == Chore.STATUS_COMPLETED:
                    total_earned += amount

                activities.append({
                    "chore_title": chore.title,
                    "reward": amount,
                    "status": status
                })

            child_activities.append({
                "child_name": child.username,
                "activities": activities,
                "total_earned": total_earned
            })

        data = {
            "total_chores_assigned": total_chores,
            "total_completed_chores": total_completed,
            "total_pending_chores": total_pending,
            "child_activities": child_activities
        }

        serializer = self.get_serializer(data)
        return Response(serializer.data)
