from django.urls import path
from familywallet import views

urlpatterns = [
    path('api/parents/wallet/', views.FamilyWalletViewSet.as_view({'get': 'retrieve'}), name='family-wallet'),
    path('api/parents/wallet/dashboard-stats/', views.FamilyWalletViewSet.as_view({'get': 'dashboard_stats'}), name='wallet-dashboard-stats'),
    path('api/parents/wallet/add-funds/', views.FamilyWalletViewSet.as_view({'post': 'add_funds'}), name='wallet-add-funds'),
    path('api/parents/wallet/earnings-chart/', views.FamilyWalletViewSet.as_view({'get': 'earnings_chart_data'}), name='wallet-earnings-chart'),
    path('api/parents/wallet/savings-breakdown/', views.FamilyWalletViewSet.as_view({'get': 'savings_breakdown'}), name='wallet-savings-breakdown'),

    # Transactions
    path('api/parents/wallet/transactions/', views.TransactionViewSet.as_view({'get': 'list'}), name='wallet-transactions'),
    path('api/parents/wallet/transactions/<uuid:pk>/complete/', views.TransactionViewSet.as_view({'post': 'complete'}), name='transaction-complete'),
    path('api/parents/wallet/transactions/<uuid:pk>/cancel/', views.TransactionViewSet.as_view({'post': 'cancel'}), name='transaction-cancel'),
    path('api/parents/wallet/transactions/complete-multiple/', views.TransactionViewSet.as_view({'post': 'complete_multiple'}), name='transactions-complete-multiple'),
    path('api/parents/wallet/transactions/recent/', views.TransactionViewSet.as_view({'get': 'recent_activities'}), name='transactions-recent'),

    # Children Wallets
    path('api/parents/wallet/children-wallets/', views.ChildWalletViewSet.as_view({'get': 'list'}), name='children-wallets'),
    path('api/parents/wallet/children-wallets/analysis/', views.ChildWalletViewSet.as_view({'get': 'analysis'}), name='children-wallets-analysis'),

    path('api/allowances/', views.FamilyAllowanceViewSet.as_view({'get': 'list', 'post': 'create'}), name='allowances'),
]
