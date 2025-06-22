from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import FamilyWallet, ChildWallet, Transaction


@admin.register(FamilyWallet)
class FamilyWalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent', 'balance', 'created_at')
    search_fields = ('parent__email', 'parent__username')
    list_filter = ('created_at',)
    ordering = ('-created_at',)


@admin.register(ChildWallet)
class ChildWalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'child', 'balance', 'total_earned', 'total_spent')
    search_fields = ('child__username', 'child__email')
    list_filter = ('created_at',)
    ordering = ('-created_at',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'family_wallet',
        'child',
        'amount',
        'transaction_type',
        'status',
        'created_by',
        'created_at',
    )
    search_fields = ('family_wallet__parent__email', 'child__username')
    list_filter = ('transaction_type', 'status', 'created_at')
    ordering = ('-created_at',)
