"""
Serializers for trade copying and execution
"""
from rest_framework import serializers
from .models import Trade, CopiedTrade, Follower
from .services import TradeCopyingService


class TradeExecutionSerializer(serializers.ModelSerializer):
    """Serializer for executing trades"""
    trader_name = serializers.CharField(source='trader.user.get_full_name', read_only=True)
    
    class Meta:
        model = Trade
        fields = [
            'id', 'trader', 'trader_name', 'currency_pair', 'direction',
            'entry_price', 'exit_price', 'stop_loss', 'take_profit',
            'lot_size', 'profit_loss', 'roi_percentage', 'status',
            'opened_at', 'closed_at', 'description', 'risk_reward_ratio'
        ]
        read_only_fields = ['id', 'opened_at', 'profit_loss', 'roi_percentage']


class CloseTradeCopySerializer(serializers.Serializer):
    """Serializer for closing a copied trade"""
    exit_price = serializers.FloatField(min_value=0)
    
    def validate_exit_price(self, value):
        """Validate exit price"""
        if value <= 0:
            raise serializers.ValidationError("Exit price must be greater than 0")
        return value


class CopiedTradeExecutionSerializer(serializers.ModelSerializer):
    """Serializer for executing copied trades"""
    original_trade_currency_pair = serializers.CharField(
        source='original_trade.currency_pair', read_only=True
    )
    original_trade_direction = serializers.CharField(
        source='original_trade.direction', read_only=True
    )
    follower_name = serializers.CharField(
        source='follower.follower_user.get_full_name', read_only=True
    )
    
    class Meta:
        model = CopiedTrade
        fields = [
            'id', 'follower', 'follower_name', 'original_trade',
            'original_trade_currency_pair', 'original_trade_direction',
            'copied_at', 'entry_price', 'exit_price', 'lot_size',
            'profit_loss', 'roi_percentage', 'status', 'closed_at'
        ]
        read_only_fields = ['id', 'copied_at', 'profit_loss', 'roi_percentage']


class FollowerPerformanceSerializer(serializers.Serializer):
    """Serializer for follower performance metrics"""
    follower_id = serializers.IntegerField()
    follower_name = serializers.CharField()
    total_copied_trades = serializers.IntegerField()
    open_trades = serializers.IntegerField()
    closed_trades = serializers.IntegerField()
    winning_trades = serializers.IntegerField()
    losing_trades = serializers.IntegerField()
    win_rate = serializers.FloatField()
    total_profit = serializers.FloatField()
    total_loss = serializers.FloatField()
    avg_profit_per_trade = serializers.FloatField()
    current_balance = serializers.FloatField()
    commission_paid = serializers.FloatField()
    initial_investment = serializers.FloatField()
    roi_percentage = serializers.FloatField()


class TraderStatsSerializer(serializers.Serializer):
    """Serializer for trader statistics"""
    trader_id = serializers.IntegerField()
    trader_name = serializers.CharField()
    total_trades = serializers.IntegerField()
    total_profit = serializers.FloatField()
    win_rate = serializers.FloatField()
    avg_roi = serializers.FloatField()
    rating = serializers.FloatField()
    monthly_return = serializers.FloatField()
    total_followers = serializers.IntegerField()


class AutoCopyTradeSerializer(serializers.Serializer):
    """Serializer for auto-copying trades to followers"""
    copied_trades_count = serializers.IntegerField()
    message = serializers.CharField()
    details = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )


class CopyTradeManuallySerializer(serializers.Serializer):
    """Serializer for manually copying a trade to specific follower"""
    follower_id = serializers.IntegerField()
    
    def validate_follower_id(self, value):
        """Validate that follower exists"""
        try:
            Follower.objects.get(id=value)
        except Follower.DoesNotExist:
            raise serializers.ValidationError("Follower not found")
        return value


class CloseCopiedTradeSerializer(serializers.Serializer):
    """Serializer for closing a copied trade"""
    exit_price = serializers.FloatField(min_value=0)
    
    def validate_exit_price(self, value):
        """Validate exit price"""
        if value <= 0:
            raise serializers.ValidationError("Exit price must be greater than 0")
        return value


class UpdateCopyPercentageSerializer(serializers.Serializer):
    """Serializer for updating copy percentage"""
    copy_percentage = serializers.FloatField(min_value=0, max_value=100)
    
    def validate_copy_percentage(self, value):
        """Validate copy percentage"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Copy percentage must be between 0 and 100")
        return value


class CreateTradeSerializer(serializers.ModelSerializer):
    """Serializer for creating new trades"""
    auto_copy = serializers.BooleanField(write_only=True, required=False, default=True)
    
    class Meta:
        model = Trade
        fields = [
            'currency_pair', 'direction', 'entry_price', 'exit_price',
            'stop_loss', 'take_profit', 'lot_size', 'description',
            'risk_reward_ratio', 'auto_copy'
        ]
    
    def create(self, validated_data):
        """Create trade and auto-copy if enabled"""
        auto_copy = validated_data.pop('auto_copy', True)
        
        # Create the trade
        trade = Trade.objects.create(**validated_data)
        
        # Auto-copy to followers if enabled
        if auto_copy:
            TradeCopyingService.auto_copy_trade_for_followers(trade)
        
        return trade
