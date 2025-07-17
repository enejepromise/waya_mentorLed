from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from children.authentication import ChildJWTAuthentication
from django.utils import timezone
from collections import defaultdict
from decimal import Decimal

from familywallet.models import ChildWallet, Transaction
from earningmeter.serializers import SummarySerializer  # or .serializers if needed

class EarningMeterView(APIView):
    """
    Child dashboard: Shows bar/pie charts + recent activities for the authenticated child.
    """
    authentication_classes = [ChildJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=SummarySerializer
    )
    def get(self, request):
        try:
            child = request.user
            try:
                wallet = child.wallet
            except ChildWallet.DoesNotExist:
                return Response({"error": "Child wallet not found."}, status=404)

            total_earned = wallet.total_earned
            total_saved = wallet.balance
            total_spent = wallet.total_spent

            # --- Bar chart earned/spent logic for last 7 days ---
            last_7_days = timezone.now() - timezone.timedelta(days=7)
            earned_qs = Transaction.objects.filter(
                child=child,
                type="chore_reward",
                status="paid",
                created_at__gte=last_7_days
            )
            spent_qs = Transaction.objects.filter(
                child=child,
                type="debit",
                status="paid",
                created_at__gte=last_7_days
            )

            earned_per_day = defaultdict(Decimal)
            spent_per_day = defaultdict(Decimal)
            for tx in earned_qs:
                date_str = tx.created_at.strftime("%b %d")
                earned_per_day[date_str] += tx.amount
            for tx in spent_qs:
                date_str = tx.created_at.strftime("%b %d")
                spent_per_day[date_str] += tx.amount

            bar_chart_days = sorted(set(list(earned_per_day.keys()) + list(spent_per_day.keys())))
            bar_chart_list = [
                {
                    "day": day,
                    "earned": earned_per_day.get(day, Decimal("0.00")),
                    "spent": spent_per_day.get(day, Decimal("0.00")),
                }
                for day in bar_chart_days
            ]

            pie_chart = {
                "reward_saved": total_saved,
                "reward_spent": total_spent
            }

            recent_activities = []
            tx_qs = Transaction.objects.filter(child=child).order_by('-created_at')[:5]
            for tx in tx_qs:
                if tx.status == "paid":
                    status_str = "saved" if tx.type in ("chore_reward", "credit") else "spent"
                elif tx.status == "pending":
                    status_str = "processing"
                elif tx.type == "debit":
                    status_str = "spent"
                else:
                    status_str = tx.status
                amount_fmt = f"NGN {tx.amount:.2f}"
                recent_activities.append({
                    "name": child.name,
                    "activity": tx.description,
                    "amount": amount_fmt,
                    "status": status_str,
                    "date": tx.created_at.strftime('%d-%B-%Y')
                })

            serializer = SummarySerializer({
                "bar_chart": bar_chart_list,
                "pie_chart": pie_chart,
                "recent_activities": recent_activities
            })
            return Response(serializer.data, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class SummaryView(APIView):
    """
    Weekly summary only: also shows earned/spent per day and pie chart for child in last 7d.
    """
    authentication_classes = [ChildJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=SummarySerializer
    )
    def get(self, request):
        try:
            child = request.user
            try:
                wallet = child.wallet
            except ChildWallet.DoesNotExist:
                return Response({"error": "Child wallet not found."}, status=404)

            now = timezone.now()
            seven_days_ago = now - timezone.timedelta(days=7)

            earned_qs = Transaction.objects.filter(
                child=child,
                type="chore_reward",
                status="paid",
                created_at__gte=seven_days_ago
            )
            spent_qs = Transaction.objects.filter(
                child=child,
                type="debit",
                status="paid",
                created_at__gte=seven_days_ago
            )

            daily_earned = defaultdict(Decimal)
            daily_spent = defaultdict(Decimal)
            for tx in earned_qs:
                day = tx.created_at.strftime("%b %d")
                daily_earned[day] += tx.amount
            for tx in spent_qs:
                day = tx.created_at.strftime("%b %d")
                daily_spent[day] += tx.amount

            chart_labels = sorted(set(daily_earned.keys()) | set(daily_spent.keys()))
            bar_chart_list = [
                {
                    "day": day,
                    "earned": daily_earned.get(day, Decimal("0.00")),
                    "spent": daily_spent.get(day, Decimal("0.00")),
                }
                for day in chart_labels
            ]

            pie_chart = {
                "reward_saved": wallet.balance,
                "reward_spent": wallet.total_spent
            }

            # Recent activities (same pattern)
            recent_activities = []
            tx_qs = Transaction.objects.filter(child=child).order_by('-created_at')[:5]
            for tx in tx_qs:
                if tx.status == "paid":
                    status_str = "saved" if tx.type in ("chore_reward", "credit") else "spent"
                elif tx.status == "pending":
                    status_str = "processing"
                elif tx.type == "debit":
                    status_str = "spent"
                else:
                    status_str = tx.status
                amount_fmt = f"NGN {tx.amount:.2f}"
                recent_activities.append({
                    "name": child.name,
                    "activity": tx.description,
                    "amount": amount_fmt,
                    "status": status_str,
                    "date": tx.created_at.strftime('%d-%B-%Y')
                })

            serializer = SummarySerializer({
                "bar_chart": bar_chart_list,
                "pie_chart": pie_chart,
                "recent_activities": recent_activities
            })
            return Response(serializer.data, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


from earningmeter.serializers import EarningTotalsSerializer
from drf_spectacular.utils import extend_schema

class EarningTotalsView(APIView):
    """
    Always returns the authenticated child's total earned, saved, and spent.
    """
    authentication_classes = [ChildJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=EarningTotalsSerializer)
    def get(self, request):
        child = request.user
        try:
            wallet = child.wallet
        except ChildWallet.DoesNotExist:
            return Response({"error": "Child wallet not found."}, status=404)

        data = {
            "total_earned": wallet.total_earned,
            "total_saved": wallet.balance,
            "total_spent": wallet.total_spent,
        }
        serializer = EarningTotalsSerializer(data)
        return Response(serializer.data, status=200)