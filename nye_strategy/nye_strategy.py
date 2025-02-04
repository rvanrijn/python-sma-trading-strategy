from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class NYEStrategy(Strategy):
    # Parameters
    volume_threshold = 0.7  # Volume threshold compared to 20-day average
    rsi_period = 14
    rsi_oversold = 30
    rsi_overbought = 70
    stop_loss_atr = 2.0
    
    def init(self):
        # Calculate volume MA
        self.volume_ma = self.I(pd.Series.rolling, self.data.Volume, 20).mean()
        
        # Calculate RSI
        close = pd.Series(self.data.Close)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        self.rsi = 100 - (100 / (1 + rs))
        
        # Calculate ATR for stop loss
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        tr = pd.DataFrame()
        tr['h-l'] = high - low
        tr['h-pc'] = abs(high - close.shift(1))
        tr['l-pc'] = abs(low - close.shift(1))
        tr['tr'] = tr.max(axis=1)
        self.atr = tr['tr'].rolling(14).mean()
    
    def next(self):
        # Check if it's near NYE (December 26-31)
        current_date = pd.to_datetime(self.data.index[self.index])
        is_nye_period = current_date.month == 12 and current_date.day >= 26
        
        # Entry conditions
        low_volume = self.data.Volume[-1] < self.volume_ma[-1] * self.volume_threshold
        oversold = self.rsi[-1] < self.rsi_oversold
        overbought = self.rsi[-1] > self.rsi_overbought
        
        if not self.position and is_nye_period:
            if low_volume and oversold:
                # Enter long with stop loss
                stop_price = self.data.Close[-1] - self.atr[-1] * self.stop_loss_atr
                self.buy(sl=stop_price)
        
        elif self.position and (overbought or not is_nye_period):
            self.position.close()

def backtest_nye_strategy():
    # Get historical data for last 5 years
    symbol = 'SPY'  # S&P 500 ETF
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365)
    
    data = yf.download(symbol, start=start_date, end=end_date)
    
    # Run backtest
    bt = Backtest(data, NYEStrategy, cash=10000, commission=.002)
    stats = bt.run()
    
    print(f"\nNYE Strategy Backtest Results for {symbol}")
    print(f"Total Return: {stats['Return [%]']:.2f}%")
    print(f"Sharpe Ratio: {stats['Sharpe Ratio']:.2f}")
    print(f"Max Drawdown: {stats['Max. Drawdown [%]']:.2f}%")
    
    bt.plot()

if __name__ == '__main__':
    backtest_nye_strategy()