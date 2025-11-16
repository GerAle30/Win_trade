"""
Trade copying and execution services for Win Trade platform
"""
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from .models import Trade, Follower, CopiedTrade


class TradeCopyingService:
    """Service for handling trade copying logic"""
    
    @staticmethod
    def calculate_copy_lot_size(original_lot_size, copy_percentage, follower_investment, original_entry_price):
        """
        Calculate the lot size for copied trade based on follower's investment
        
        Args:
            original_lot_size: Original trade lot size
            copy_percentage: Percentage of follower's investment to copy (0-100)
            follower_investment: Follower's initial investment
            original_entry_price: Original trade entry price
        
        Returns:
            Calculated lot size for the copy trade
        """
        if original_lot_size == 0 or original_entry_price == 0:
            return 0
        
        # Calculate proportional investment
        proportional_investment = (follower_investment * Decimal(copy_percentage)) / Decimal(100)
        
        # Calculate lot size: investment / entry_price
        copy_lot_size = proportional_investment / Decimal(original_entry_price)
        
        return float(copy_lot_size)
    
    @staticmethod
    def calculate_profit_loss(entry_price, exit_price, lot_size, direction):
        """
        Calculate profit/loss for a trade
        
        Args:
            entry_price: Trade entry price
            exit_price: Trade exit price
            lot_size: Trade lot size
            direction: Trade direction ('buy' or 'sell')
        
        Returns:
            Tuple of (profit_loss, roi_percentage)
        """
        if direction == 'buy':
            profit_loss = (Decimal(exit_price) - Decimal(entry_price)) * Decimal(lot_size)
        else:  # sell
            profit_loss = (Decimal(entry_price) - Decimal(exit_price)) * Decimal(lot_size)
        
        # Calculate ROI percentage
        initial_investment = Decimal(entry_price) * Decimal(lot_size)
        if initial_investment == 0:
            roi_percentage = 0
        else:
            roi_percentage = (profit_loss / initial_investment) * Decimal(100)
        
        return float(profit_loss), float(roi_percentage)
    
    @staticmethod
    @transaction.atomic
    def copy_trade(original_trade, follower):
        """
        Create a copy of a trade for a follower
        
        Args:
            original_trade: Trade instance to copy
            follower: Follower instance
        
        Returns:
            Created CopiedTrade instance or None if error
        """
        try:
            # Calculate copy lot size
            copy_lot_size = TradeCopyingService.calculate_copy_lot_size(
                original_lot_size=original_trade.lot_size,
                copy_percentage=follower.copy_percentage,
                follower_investment=follower.initial_investment,
                original_entry_price=original_trade.entry_price
            )
            
            # Create copied trade
            copied_trade = CopiedTrade.objects.create(
                follower=follower,
                original_trade=original_trade,
                entry_price=original_trade.entry_price,
                lot_size=copy_lot_size,
                status='open'
            )
            
            return copied_trade
        
        except Exception as e:
            print(f"Error copying trade: {str(e)}")
            return None
    
    @staticmethod
    @transaction.atomic
    def close_copied_trade(copied_trade, exit_price):
        """
        Close a copied trade and calculate profit/loss
        
        Args:
            copied_trade: CopiedTrade instance to close
            exit_price: Exit price for the trade
        
        Returns:
            Updated CopiedTrade instance
        """
        try:
            original_trade = copied_trade.original_trade
            
            # Calculate profit/loss
            profit_loss, roi_percentage = TradeCopyingService.calculate_profit_loss(
                entry_price=copied_trade.entry_price,
                exit_price=exit_price,
                lot_size=copied_trade.lot_size,
                direction=original_trade.direction
            )
            
            # Update copied trade
            copied_trade.exit_price = exit_price
            copied_trade.profit_loss = profit_loss
            copied_trade.roi_percentage = roi_percentage
            copied_trade.status = 'closed'
            copied_trade.closed_at = timezone.now()
            copied_trade.save()
            
            # Update follower's balance and stats
            follower = copied_trade.follower
            follower.current_balance += Decimal(profit_loss)
            follower.total_profit += Decimal(profit_loss)
            
            # Calculate and update commission (e.g., 10% of profit if profitable)
            if profit_loss > 0:
                commission = Decimal(profit_loss) * Decimal(0.1)
                follower.commission_paid += commission
            
            follower.save()
            
            return copied_trade
        
        except Exception as e:
            print(f"Error closing copied trade: {str(e)}")
            return None
    
    @staticmethod
    def auto_copy_trade_for_followers(original_trade):
        """
        Automatically copy a trade to all followers with auto_copy enabled
        
        Args:
            original_trade: Trade instance that was created
        
        Returns:
            List of created CopiedTrade instances
        """
        copied_trades = []
        
        try:
            # Get all followers of the trader with auto_copy enabled
            followers = Follower.objects.filter(
                trader=original_trade.trader,
                auto_copy_trades=True
            )
            
            # Copy trade for each follower
            for follower in followers:
                copied_trade = TradeCopyingService.copy_trade(original_trade, follower)
                if copied_trade:
                    copied_trades.append(copied_trade)
            
            return copied_trades
        
        except Exception as e:
            print(f"Error auto-copying trade: {str(e)}")
            return []
    
    @staticmethod
    def get_follower_performance(follower):
        """
        Calculate performance metrics for a follower
        
        Args:
            follower: Follower instance
        
        Returns:
            Dictionary with performance metrics
        """
        copied_trades = follower.copied_trades.all()
        closed_trades = copied_trades.filter(status='closed')
        winning_trades = closed_trades.filter(profit_loss__gt=0)
        losing_trades = closed_trades.filter(profit_loss__lt=0)
        
        total_trades = copied_trades.count()
        total_closed = closed_trades.count()
        total_profit = sum(t.profit_loss for t in closed_trades)
        total_loss = sum(abs(t.profit_loss) for t in losing_trades)
        
        performance = {
            'total_copied_trades': total_trades,
            'open_trades': copied_trades.filter(status='open').count(),
            'closed_trades': total_closed,
            'winning_trades': winning_trades.count(),
            'losing_trades': losing_trades.count(),
            'win_rate': (winning_trades.count() / total_closed * 100) if total_closed > 0 else 0,
            'total_profit': follower.total_profit,
            'total_loss': float(total_loss),
            'avg_profit_per_trade': float(total_profit / total_closed) if total_closed > 0 else 0,
            'current_balance': float(follower.current_balance),
            'commission_paid': float(follower.commission_paid),
            'initial_investment': float(follower.initial_investment),
            'roi_percentage': (float(follower.total_profit) / float(follower.initial_investment) * 100) 
                             if float(follower.initial_investment) > 0 else 0,
        }
        
        return performance
    
    @staticmethod
    def update_trader_stats(trader):
        """
        Update trader statistics based on their trades
        
        Args:
            trader: Trader instance
        """
        trades = trader.trades.all()
        closed_trades = trades.filter(status='closed')
        winning_trades = closed_trades.filter(profit_loss__gt=0)
        
        total_trades = trades.count()
        total_profit = sum(t.profit_loss for t in closed_trades)
        
        # Update trader stats
        trader.total_trades = total_trades
        trader.total_profit = float(total_profit)
        
        if total_trades > 0:
            trader.win_rate = (winning_trades.count() / closed_trades.count() * 100) if closed_trades.count() > 0 else 0
        
        # Calculate average ROI
        if closed_trades.count() > 0:
            total_roi = sum(t.roi_percentage for t in closed_trades)
            trader.avg_roi = float(total_roi / closed_trades.count())
        
        # Update rating (based on win rate and ROI)
        trader.rating = (trader.win_rate * 0.4 + trader.avg_roi * 0.6) / 100
        
        # Update monthly return (you can enhance this with date filtering)
        trader.monthly_return = float(total_profit)
        
        trader.save()
