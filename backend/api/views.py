from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Sum
from django.utils import timezone

from .models import Trader, Trade, Follower, CopiedTrade
from .serializers import (
    TraderSerializer, TradeSerializer, FollowerSerializer, CopiedTradeSerializer
)


class TraderViewSet(viewsets.ModelViewSet):
    queryset = Trader.objects.all()
    serializer_class = TraderSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['experience_level', 'is_verified']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    ordering_fields = ['rating', 'total_followers', 'total_profit']
    ordering = ['-rating']

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        trader = self.get_object()
        stats = {
            'total_followers': trader.total_followers,
            'total_trades': trader.total_trades,
            'win_rate': trader.win_rate,
            'total_profit': trader.total_profit,
            'avg_roi': trader.avg_roi,
            'monthly_return': trader.monthly_return,
            'rating': trader.rating,
        }
        return Response(stats)

    @action(detail=True, methods=['get'])
    def trades(self, request, pk=None):
        trader = self.get_object()
        trades = trader.trades.all()
        serializer = TradeSerializer(trades, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def followers_list(self, request, pk=None):
        trader = self.get_object()
        followers = trader.followers.all()
        serializer = FollowerSerializer(followers, many=True)
        return Response(serializer.data)


class TradeViewSet(viewsets.ModelViewSet):
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['trader', 'currency_pair', 'direction', 'status']
    search_fields = ['currency_pair', 'description']
    ordering_fields = ['opened_at', 'profit_loss', 'roi_percentage']
    ordering = ['-opened_at']

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=['get'])
    def by_status(self, request):
        status_filter = request.query_params.get('status', 'open')
        trades = Trade.objects.filter(status=status_filter)
        serializer = self.get_serializer(trades, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def top_performers(self, request):
        limit = int(request.query_params.get('limit', 10))
        trades = Trade.objects.filter(status='closed').order_by('-roi_percentage')[:limit]
        serializer = self.get_serializer(trades, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def close_trade(self, request, pk=None):
        trade = self.get_object()
        exit_price = request.data.get('exit_price')
        
        if exit_price is None:
            return Response(
                {'error': 'exit_price is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trade.exit_price = exit_price
        trade.status = 'closed'
        trade.closed_at = timezone.now()
        
        # Calculate profit/loss
        if trade.direction == 'buy':
            trade.profit_loss = (exit_price - trade.entry_price) * trade.lot_size
        else:
            trade.profit_loss = (trade.entry_price - exit_price) * trade.lot_size
        
        trade.roi_percentage = (trade.profit_loss / (trade.entry_price * trade.lot_size)) * 100
        trade.save()
        
        serializer = self.get_serializer(trade)
        return Response(serializer.data)


class FollowerViewSet(viewsets.ModelViewSet):
    queryset = Follower.objects.all()
    serializer_class = FollowerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['trader', 'follower_user', 'auto_copy_trades']
    ordering_fields = ['followed_at', 'total_profit']
    ordering = ['-followed_at']

    @action(detail=False, methods=['post'])
    def follow_trader(self, request):
        trader_id = request.data.get('trader_id')
        auto_copy = request.data.get('auto_copy_trades', True)
        copy_percentage = request.data.get('copy_percentage', 100.0)
        initial_investment = request.data.get('initial_investment', 0.0)
        
        if not trader_id:
            return Response(
                {'error': 'trader_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trader = get_object_or_404(Trader, id=trader_id)
        
        follower, created = Follower.objects.get_or_create(
            trader=trader,
            follower_user=request.user,
            defaults={
                'auto_copy_trades': auto_copy,
                'copy_percentage': copy_percentage,
                'initial_investment': initial_investment,
                'current_balance': initial_investment,
            }
        )
        
        if not created:
            return Response(
                {'error': 'You are already following this trader'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(follower)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def unfollow_trader(self, request):
        trader_id = request.data.get('trader_id')
        
        if not trader_id:
            return Response(
                {'error': 'trader_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        follower = get_object_or_404(
            Follower,
            trader_id=trader_id,
            follower_user=request.user
        )
        follower.delete()
        
        return Response({'status': 'unfollowed'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        follower = self.get_object()
        copied_trades = follower.copied_trades.all()
        
        total_trades = copied_trades.count()
        closed_trades = copied_trades.filter(status='closed')
        winning_trades = closed_trades.filter(profit_loss__gt=0).count()
        
        performance = {
            'total_copied_trades': total_trades,
            'closed_trades': closed_trades.count(),
            'winning_trades': winning_trades,
            'total_profit': follower.total_profit,
            'commission_paid': follower.commission_paid,
            'current_balance': follower.current_balance,
        }
        
        if closed_trades.count() > 0:
            performance['win_rate'] = (winning_trades / closed_trades.count()) * 100
        
        return Response(performance)
