from django.urls import path
from familywallet import views

urlpatterns = [
    # 1. Parent Wallet Overview
    path('api/parents/wallet/', views.FamilyWalletViewSet.as_view({'get': 'retrieve'}), name='family-wallet'),

    # 2. Dashboard Stats
    path('api/parents/wallet/dashboard-stats/', views.FamilyWalletViewSet.as_view({'get': 'dashboard_stats'}), name='wallet-dashboard-stats'),

    # 3. Add Funds to Wallet
    path('api/parents/wallet/add-funds/', views.FamilyWalletViewSet.as_view({'post': 'add_funds'}), name='wallet-add-funds'),

    # 4. Earnings Chart Data
    path('api/parents/wallet/earnings-chart/', views.FamilyWalletViewSet.as_view({'get': 'earnings_chart_data'}), name='wallet-earnings-chart'),

    # 5. Savings Breakdown
    path('api/parents/wallet/savings-breakdown/', views.FamilyWalletViewSet.as_view({'get': 'savings_breakdown'}), name='wallet-savings-breakdown'),

    # 6. List All Transactions
    path('api/parents/wallet/transactions/', views.TransactionViewSet.as_view({'get': 'list'}), name='wallet-transactions'),

    # 7. Complete Transaction
    path('api/parents/wallet/transactions/<uuid:pk>/complete/', views.TransactionViewSet.as_view({'post': 'complete'}), name='transaction-complete'),

    # 8. Cancel Transaction
    path('api/parents/wallet/transactions/<uuid:pk>/cancel/', views.TransactionViewSet.as_view({'post': 'cancel'}), name='transaction-cancel'),

    # 9. Complete Multiple Transactions
    path('api/parents/wallet/transactions/complete-multiple/', views.TransactionViewSet.as_view({'post': 'complete_multiple'}), name='transactions-complete-multiple'),

    # 10. Recent Transactions
    path('api/parents/wallet/transactions/recent/', views.TransactionViewSet.as_view({'get': 'recent_activities'}), name='transactions-recent'),

    # 11. Get Child Wallets
    path('api/parents/wallet/children-wallets/', views.ChildWalletViewSet.as_view({'get': 'list'}), name='children-wallets'),

    # 12. Create Allowance
    path('api/allowances/', views.CreateFamilyAllowanceView.as_view(), name='create-allowance'),

    # 13. List Allowances
    path('api/allowances/list/', views.ListFamilyAllowancesView.as_view(), name='list-allowances'),
]
