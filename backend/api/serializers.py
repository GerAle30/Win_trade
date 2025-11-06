from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Trader, Trade, Follower, CopiedTrade


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class TraderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Trader
        fields = [
            'id', 'user', 'bio', 'experience_level', 'total_followers',
            'total_trades', 'win_rate', 'total_profit', 'avg_roi',
            'monthly_return', 'rating', 'profile_image', 'broker',
            'account_size', 'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TradeSerializer(serializers.ModelSerializer):
    trader_name = serializers.CharField(source='trader.user.get_full_name', read_only=True)
    
    class Meta:
        model = Trade
        fields = [
            'id', 'trader', 'trader_name', 'currency_pair', 'direction',
            'entry_price', 'exit_price', 'stop_loss', 'take_profit',
            'lot_size', 'profit_loss', 'roi_percentage', 'status',
            'opened_at', 'closed_at', 'description', 'risk_reward_ratio'
        ]
        read_only_fields = ['id', 'opened_at']


class FollowerSerializer(serializers.ModelSerializer):
    follower_name = serializers.CharField(source='follower_user.get_full_name', read_only=True)
    trader_name = serializers.CharField(source='trader.user.get_full_name', read_only=True)
    
    class Meta:
        model = Follower
        fields = [
            'id', 'trader', 'trader_name', 'follower_user', 'follower_name',
            'auto_copy_trades', 'copy_percentage', 'initial_investment',
            'current_balance', 'total_profit', 'commission_paid',
            'followed_at', 'updated_at'
        ]
        read_only_fields = ['id', 'followed_at', 'updated_at']


class CopiedTradeSerializer(serializers.ModelSerializer):
    original_trade_info = TradeSerializer(source='original_trade', read_only=True)
    
    class Meta:
        model = CopiedTrade
        fields = [
            'id', 'follower', 'original_trade', 'original_trade_info',
            'copied_at', 'entry_price', 'exit_price', 'lot_size',
            'profit_loss', 'roi_percentage', 'status', 'closed_at'
        ]
        read_only_fields = ['id', 'copied_at']
