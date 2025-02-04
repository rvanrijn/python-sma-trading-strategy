from backtesting import Backtest, Strategy
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, time
import pandas_market_calendars as mcal

class NYSEHoursStrategy(Strategy):
    """Trading strategy that only operates during NYSE market hours"""
    
    def __init__(self):
        super().__init__()
        # Initialize NYSE calendar
        self.nyse = mcal.get_calendar('NYSE')
    
    def is_market_open(self, timestamp):
        # Convert to EST (NYSE timezone)
        est_time = timestamp.tz_localize('UTC').tz_convert('America/New_York').time()
        
        # Regular trading hours: 9:30 AM - 4:00 PM EST
        market_open = time(9, 30)
        market_close = time(16, 0)
        
        # Check if it's within trading hours
        return market_open <= est_time <= market_close
    
    def is_trading_day(self, date):
        schedule = self.nyse.schedule(start_date=date, end_date=date)
        return not schedule.empty
    
    def init(self):
        # Price indicators
        self.sma50 = self.I(pd.Series.rolling, self.data.Close, 50).mean()
        self.sma20 = self.I(pd.Series.rolling, self.data.Close, 20).mean()
        
        # Volatility indicator
        self.atr = self.I(self.calc_atr, self.data.High, self.data.Low, self.data.Close)
    
    def calc_atr(self, high, low, close, period=14):
        tr = pd.DataFrame()
        tr['h-l'] = high - low
        tr['h-pc'] = abs(high - close.shift(1))
        tr['l-pc'] = abs(low - close.shift(1))
        tr['tr'] = tr.max(axis=1)
        return tr['tr'].rolling(period).mean()
    
    def next(self):
        # Get current timestamp
        current_time = pd.to_datetime(self.data.index[self.index])
        
        # Only trade if market is open
        if not (self.is_trading_day(current_time.date()) and 
                self.is_market_open(current_time)):
            return
        
        # Trading logic during market hours
        if not self.position:
            # Enter long if short-term MA crosses above long-term MA
            if self.sma20[-1] > self.sma50[-1] and self.sma20[-2] <= self.sma50[-2]:
                # Calculate position size based on ATR
                stop_distance = self.atr[-1] * 2
                size = self.equity * 0.02 / stop_distance  # Risk 2% per trade
                self.buy(size=size, sl=self.data.Close[-1] - stop_distance)
        
        else:
            # Exit if short-term MA crosses below long-term MA
            if self.sma20[-1] < self.sma50[-1] and self.sma20[-2] >= self.sma50[-2]:
                self.position.close()

def backtest_nyse_strategy(symbol='SPY', start='2020-01-01', end='2024-12-31'):
    data = yf.download(symbol, start=start, end=end, interval='1h')
    
    bt = Backtest(data, NYSEHoursStrategy,
                  cash=10000,
                  commission=.002,
                  exclusive_orders=True)
    
    stats = bt.run()
    print(f"\nBacktest Results for NYSE Hours Strategy ({symbol})")
    print(f"Total Return: {stats['Return [%]']:.2f}%")
    print(f"Sharpe Ratio: {stats['Sharpe Ratio']:.2f}")
    print(f"Max Drawdown: {stats['Max. Drawdown [%]']:.2f}%")
    print(f"Number of Trades: {stats['# Trades']}")
    
    bt.plot()

if __name__ == '__main__':
    backtest_nyse_strategy()