from django.contrib import admin
from .models import Trader, Trade, Follower, CopiedTrade


@admin.register(Trader)
class TraderAdmin(admin.ModelAdmin):
    list_display = ['user', 'experience_level', 'total_followers', 'win_rate', 'rating', 'is_verified']
    list_filter = ['experience_level', 'is_verified', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'total_followers', 'total_trades']


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ['currency_pair', 'trader', 'direction', 'status', 'entry_price', 'profit_loss', 'roi_percentage']
    list_filter = ['status', 'currency_pair', 'direction', 'opened_at']
    search_fields = ['trader__user__username', 'currency_pair']
    readonly_fields = ['opened_at', 'closed_at']


@admin.register(Follower)
class FollowerAdmin(admin.ModelAdmin):
    list_display = ['follower_user', 'trader', 'auto_copy_trades', 'total_profit', 'current_balance']
    list_filter = ['auto_copy_trades', 'followed_at']
    search_fields = ['follower_user__username', 'trader__user__username']
    readonly_fields = ['followed_at', 'updated_at']


@admin.register(CopiedTrade)
class CopiedTradeAdmin(admin.ModelAdmin):
    list_display = ['follower', 'original_trade', 'status', 'profit_loss', 'roi_percentage']
    list_filter = ['status', 'copied_at']
    search_fields = ['follower__follower_user__username']
    readonly_fields = ['copied_at']
