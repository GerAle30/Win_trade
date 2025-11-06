from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Trader(models.Model):
    EXPERIENCE_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='trader_profile')
    bio = models.TextField(blank=True)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='beginner')
    total_followers = models.IntegerField(default=0)
    total_trades = models.IntegerField(default=0)
    win_rate = models.FloatField(default=0.0)
    total_profit = models.FloatField(default=0.0)
    avg_roi = models.FloatField(default=0.0)
    monthly_return = models.FloatField(default=0.0)
    rating = models.FloatField(default=0.0)
    profile_image = models.ImageField(upload_to='traders/', blank=True, null=True)
    broker = models.CharField(max_length=100, blank=True)
    account_size = models.FloatField(default=0.0)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.experience_level}"

    class Meta:
        ordering = ['-rating', '-total_followers']


class Trade(models.Model):
    CURRENCY_PAIRS = [
        ('EURUSD', 'EUR/USD'),
        ('GBPUSD', 'GBP/USD'),
        ('USDJPY', 'USD/JPY'),
        ('AUDUSD', 'AUD/USD'),
        ('NZDUSD', 'NZD/USD'),
        ('USDCAD', 'USD/CAD'),
        ('USDCHF', 'USD/CHF'),
        ('EURUSD', 'EUR/USD'),
    ]
    
    DIRECTION_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('pending', 'Pending'),
    ]

    trader = models.ForeignKey(Trader, on_delete=models.CASCADE, related_name='trades')
    currency_pair = models.CharField(max_length=10, choices=CURRENCY_PAIRS)
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    entry_price = models.FloatField()
    exit_price = models.FloatField(null=True, blank=True)
    stop_loss = models.FloatField()
    take_profit = models.FloatField()
    lot_size = models.FloatField()
    profit_loss = models.FloatField(default=0.0)
    roi_percentage = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    opened_at = models.DateTimeField(default=timezone.now)
    closed_at = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)
    risk_reward_ratio = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.currency_pair} - {self.direction} by {self.trader.user.get_full_name()}"

    class Meta:
        ordering = ['-opened_at']


class Follower(models.Model):
    trader = models.ForeignKey(Trader, on_delete=models.CASCADE, related_name='followers')
    follower_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    auto_copy_trades = models.BooleanField(default=True)
    copy_percentage = models.FloatField(default=100.0)
    initial_investment = models.FloatField(default=0.0)
    current_balance = models.FloatField(default=0.0)
    total_profit = models.FloatField(default=0.0)
    commission_paid = models.FloatField(default=0.0)
    followed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.follower_user.get_full_name()} following {self.trader.user.get_full_name()}"

    class Meta:
        unique_together = ('trader', 'follower_user')
        ordering = ['-followed_at']


class CopiedTrade(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]
    
    follower = models.ForeignKey(Follower, on_delete=models.CASCADE, related_name='copied_trades')
    original_trade = models.ForeignKey(Trade, on_delete=models.CASCADE, related_name='copies')
    copied_at = models.DateTimeField(auto_now_add=True)
    entry_price = models.FloatField()
    exit_price = models.FloatField(null=True, blank=True)
    lot_size = models.FloatField()
    profit_loss = models.FloatField(default=0.0)
    roi_percentage = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    closed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Copy of {self.original_trade} by {self.follower.follower_user.get_full_name()}"

    class Meta:
        ordering = ['-copied_at']
