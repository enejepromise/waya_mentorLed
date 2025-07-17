from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from collections import defaultdict
from decimal import Decimal

from familywallet.models import ChildWallet, Transaction
from familywallet.serializers import EarningMeterSerializer  
from children.models import Child


class EarningMeterView(APIView):
    # Removed all permissions so this view is open to anyone
    permission_classes = []  

    @extend_schema(
        responses=EarningMeterSerializer  
    )
    def get(self, request):
        try:
            # You need a way to identify the child since request.user is not guaranteed now.
            # For example, get child ID from query params: /api/earning-meter/?child_id=abc123
            child_id = request.query_params.get('child_id')

            if not child_id:
                return Response({"error": "child_id is required as a query parameter."}, status=400)

            try:
                child = Child.objects.get(id=child_id)
            except Child.DoesNotExist:
                return Response({"error": "Child not found."}, status=404)

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
class SummaryView(APIView):
    permission_classes = []

    @extend_schema(
        description="Weekly summary for barchart and pie chart (reward earned/spent/saved)",
        responses=dict  # You can later plug in a serializer if needed
    )
    def get(self, request):
        child_id = request.query_params.get("child_id")

        if not child_id:
            return Response({"error": "child_id is required"}, status=400)

        try:
            child = Child.objects.get(id=child_id)
        except Child.DoesNotExist:
            return Response({"error": "Child not found"}, status=404)

        try:
            now = timezone.now()
            seven_days_ago = now - timezone.timedelta(days=7)

            # Bar chart: reward earned per day
            earned_transactions = Transaction.objects.filter(
                child=child,
                type="chore_reward",
                status="paid",
                created_at__gte=seven_days_ago
            )

            spent_transactions = Transaction.objects.filter(
                child=child,
                type="debit",  # assuming "debit" is the spent transaction type
                status="paid",
                created_at__gte=seven_days_ago
            )

            daily_earned = defaultdict(Decimal)
            daily_spent = defaultdict(Decimal)

            for tx in earned_transactions:
                date = tx.created_at.strftime("%b %d")  # e.g., "Apr 20"
                daily_earned[date] += tx.amount

            for tx in spent_transactions:
                date = tx.created_at.strftime("%b %d")
                daily_spent[date] += tx.amount

            # Prepare bar chart data
            chart_labels = list({*daily_earned.keys(), *daily_spent.keys()})
            chart_labels.sort()  # optional, to sort by day name

            bar_chart_data = {
                "labels": chart_labels,
                "earned": [float(daily_earned.get(day, 0)) for day in chart_labels],
                "spent": [float(daily_spent.get(day, 0)) for day in chart_labels]
            }

            # Pie chart: total reward saved vs spent
            wallet = child.wallet
            total_saved = wallet.balance
            total_spent = wallet.total_spent

            pie_chart_data = {
                "reward_saved": float(total_saved),
                "reward_spent": float(total_spent)
            }

            return Response({
                "bar_chart": bar_chart_data,
                "pie_chart": pie_chart_data
            }, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
