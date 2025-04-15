from datetime import datetime, time
import pytz
import calendar

class MarketSchedule:
    def __init__(self):
        # Indian Standard Time timezone
        self.timezone = pytz.timezone('Asia/Kolkata')
        
        # Market hours (NSE): 9:15 AM to 3:30 PM, Monday to Friday
        self.market_open_time = time(9, 15, 0)
        self.market_close_time = time(15, 30, 0)
        
        # Trading days: Monday to Friday (0 is Monday, 6 is Sunday in calendar.weekday)
        self.trading_days = range(0, 5)  # Monday to Friday
    
    def is_market_open(self):
        """Check if the market is currently open"""
        # Get current time in IST
        now = datetime.now(self.timezone)
        current_time = now.time()
        
        # Check if today is a trading day
        current_weekday = calendar.weekday(now.year, now.month, now.day)
        is_trading_day = current_weekday in self.trading_days
        
        # Check if current time is within market hours
        is_market_hours = (self.market_open_time <= current_time <= self.market_close_time)
        
        return is_trading_day and is_market_hours

    def time_until_market_open(self):
        """Get time in seconds until market opens"""
        now = datetime.now(self.timezone)
        current_time = now.time()
        current_weekday = calendar.weekday(now.year, now.month, now.day)
        
        if current_weekday in self.trading_days:
            # Check if market is yet to open today
            if current_time < self.market_open_time:
                # Calculate seconds until market open today
                now_secs = current_time.hour * 3600 + current_time.minute * 60 + current_time.second
                open_secs = self.market_open_time.hour * 3600 + self.market_open_time.minute * 60
                return open_secs - now_secs
            
            # Market has already opened and closed for today
            if current_time > self.market_close_time:
                # Calculate seconds until next trading day
                days_until_next_trading = 1
                if current_weekday == 4:  # Friday
                    days_until_next_trading = 3  # Saturday, Sunday, Monday
                
                # Return seconds until next market open
                return days_until_next_trading * 86400 - (
                    (current_time.hour * 3600 + current_time.minute * 60 + current_time.second) - 
                    (self.market_open_time.hour * 3600 + self.market_open_time.minute * 60)
                )
        
        # Calculate days until next trading day
        days_until_next_trading = 1
        if current_weekday == 5:  # Saturday
            days_until_next_trading = 2  # Sunday, Monday
        if current_weekday == 6:  # Sunday
            days_until_next_trading = 1  # Monday
        
        # Return seconds until next market open
        return days_until_next_trading * 86400 - (
            (current_time.hour * 3600 + current_time.minute * 60 + current_time.second) - 
            (self.market_open_time.hour * 3600 + self.market_open_time.minute * 60)
        )

    def time_until_market_close(self):
        """Get time in seconds until market closes if market is open, otherwise returns None"""
        if not self.is_market_open():
            return None
            
        now = datetime.now(self.timezone)
        current_time = now.time()
        
        # Calculate seconds until market close
        now_secs = current_time.hour * 3600 + current_time.minute * 60 + current_time.second
        close_secs = self.market_close_time.hour * 3600 + self.market_close_time.minute * 60
        
        return close_secs - now_secs