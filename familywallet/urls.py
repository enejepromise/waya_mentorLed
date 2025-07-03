from django.urls import path
from .views import (
    FamilyWalletViewSet,
    ChildWalletViewSet,
    TransactionViewSet,
    AllowanceViewSet,
    WalletViewSet,
)

urlpatterns = [
    # FAMILY WALLET ENDPOINTS
    path('wallet/', FamilyWalletViewSet.as_view({'get': 'list'}), name='wallet-list'),
    path('wallet/add_funds/', FamilyWalletViewSet.as_view({'post': 'add_funds'}), name='wallet-add-funds'),
    path('wallet/dashboard_stats/', FamilyWalletViewSet.as_view({'get': 'dashboard_stats'}), name='wallet-dashboard-stats'),
    path('wallet/earnings_chart_data/', FamilyWalletViewSet.as_view({'get': 'earnings_chart_data'}), name='wallet-earnings-chart-data'),
    path('wallet/savings_breakdown/', FamilyWalletViewSet.as_view({'get': 'savings_breakdown'}), name='wallet-savings-breakdown'),
    path('wallet/transfer/', FamilyWalletViewSet.as_view({'post': 'transfer'}), name='wallet-transfer'),

    # WALLET PIN AND PAYMENT ENDPOINTS
    path('wallet/set_pin/', WalletViewSet.as_view({'post': 'set_pin'}), name='wallet-set-pin'),
    path('wallet/make_payment/', WalletViewSet.as_view({'post': 'make_payment'}), name='wallet-make-payment'),

    # CHILD WALLET ANALYSIS
    path('child-wallets/', ChildWalletViewSet.as_view({'get': 'list'}), name='child-wallets-list'),
    path('child-wallets/analysis/', ChildWalletViewSet.as_view({'get': 'analysis'}), name='child-wallets-analysis'),

    # TRANSACTION ENDPOINTS
    path('transactions/', TransactionViewSet.as_view({'get': 'list', 'post': 'create'}), name='transaction-list'),
    path('transactions/<uuid:pk>/', TransactionViewSet.as_view({'get': 'retrieve'}), name='transaction-detail'),
    path('transactions/<uuid:pk>/complete/', TransactionViewSet.as_view({'post': 'complete'}), name='transaction-complete'),
    path('transactions/<uuid:pk>/cancel/', TransactionViewSet.as_view({'post': 'cancel'}), name='transaction-cancel'),
    path('transactions/complete_multiple/', TransactionViewSet.as_view({'post': 'complete_multiple'}), name='transaction-complete-multiple'),
    path('transactions/recent_activities/', TransactionViewSet.as_view({'get': 'recent_activities'}), name='transaction-recent-activities'),

    # FAMILY ALLOWANCE ENDPOINTS
    path('allowances/', AllowanceViewSet.as_view({'get': 'list', 'post': 'create'}), name='allowance-list'),
    path('allowances/<uuid:pk>/', AllowanceViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='allowance-detail'),
]
