from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from collections import defaultdict
from decimal import Decimal

from familywallet.models import ChildWallet, Transaction
from familywallet.serializers import EarningMeterSerializer  # ✅ import
from children.models import Child


class EarningMeterView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses=EarningMeterSerializer  # ✅ tells drf-spectacular what to expect
    )
    def get(self, request):
        try:
            if not hasattr(request.user, "child"):
                return Response({"error": "Only child users can access this endpoint."}, status=403)

            child = request.user.child
            wallet = child.wallet

            total_earned = wallet.total_earned
            total_saved = wallet.balance
            total_spent = wallet.total_spent

            savings_breakdown = {
                "reward_saved": str(total_saved),
                "reward_spent": str(total_spent)
            }

            last_7_days = timezone.now() - timezone.timedelta(days=7)
            transactions = Transaction.objects.filter(
                child=child,
                type="chore_reward",
                status="paid",
                created_at__gte=last_7_days
            ).order_by('-created_at')

            earnings_over_time = defaultdict(Decimal)
            recent_activities = []

            for tx in transactions:
                date_str = tx.created_at.strftime("%Y-%m-%d")
                earnings_over_time[date_str] += tx.amount
                recent_activities.append({
                    "activity": tx.description,
                    "amount": str(tx.amount),
                    "status": tx.status,
                    "date": tx.created_at.strftime("%d-%B-%Y")
                })

            data = {
                "total_earned": str(total_earned),
                "total_saved": str(total_saved),
                "total_spent": str(total_spent),
                "savings_breakdown": savings_breakdown,
                "earnings_over_time": {k: str(v) for k, v in earnings_over_time.items()},
                "recent_activities": recent_activities[:5]
            }

            return Response(data, status=200)

        except ChildWallet.DoesNotExist:
            return Response({"error": "Child wallet not found."}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
