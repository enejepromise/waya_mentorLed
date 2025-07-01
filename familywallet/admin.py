from django.contrib import admin
from .models import FamilyWallet, ChildWallet, Transaction, Allowance


@admin.register(FamilyWallet)
class FamilyWalletAdmin(admin.ModelAdmin):
    list_display = ('full_name_parent', 'balance', 'pin_set', 'created_at', 'updated_at')
    search_fields = ('parent__full_name', 'parent__email')
    readonly_fields = ['created_at', 'updated_at']

    def full_name_parent(self, obj):
        return obj.parent.full_name
    full_name_parent.short_description = 'Full Name (Parent)'

    def pin_set(self, obj):
        return bool(obj.pin)
    pin_set.boolean = True
    pin_set.short_description = 'PIN Set'


@admin.register(ChildWallet)
class ChildWalletAdmin(admin.ModelAdmin):
    list_display = ('name_child', 'full_name_parent', 'balance', 'total_earned', 'total_spent', 'savings_rate')
    search_fields = ('child__name', 'child__parent__full_name', 'child__parent__email')
    readonly_fields = ['created_at', 'updated_at']

    def name_child(self, obj):
        return obj.child.name
    name_child.short_description = 'Name (Child)'

    def full_name_parent(self, obj):
        return obj.child.parent.full_name
    full_name_parent.short_description = 'Full Name (Parent)'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name_child', 'amount', 'type', 'status', 'created_at'
    )
    search_fields = ('child__name', 'created_by__full_name', 'description')
    list_filter = ('type', 'status', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ['created_at']

    def name_child(self, obj):
        return obj.child.name if obj.child else 'N/A'
    name_child.short_description = 'Name (Child)'


@admin.register(Allowance)
class AllowanceAdmin(admin.ModelAdmin):
    list_display = ('full_name_parent', 'name_child', 'amount', 'status', 'created_at')
    search_fields = ('parent__full_name', 'child__name')
    list_filter = ('status', 'created_at')
    readonly_fields = ['created_at']

    def name_child(self, obj):
        return obj.child.name
    name_child.short_description = 'Name (Child)'

    def full_name_parent(self, obj):
        return obj.parent.full_name
    full_name_parent.short_description = 'Full Name (Parent)'
