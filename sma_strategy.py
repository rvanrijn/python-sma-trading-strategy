from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import yfinance as yf
import pandas as pd
import numpy as np

class EnhancedSMACrossover(Strategy):
    n1 = 20  # Fast SMA
    n2 = 50  # Slow SMA
    risk_pct = 0.02  # Risk per trade (2%)
    atr_periods = 14  # ATR period
    
    def init(self):
        self.sma1 = self.I(pd.Series.rolling, self.data.Close, self.n1).mean()
        self.sma2 = self.I(pd.Series.rolling, self.data.Close, self.n2).mean()
        
        # Calculate ATR for position sizing
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        close = pd.Series(self.data.Close)
        
        tr = pd.DataFrame()
        tr['h-l'] = high - low
        tr['h-pc'] = abs(high - close.shift(1))
        tr['l-pc'] = abs(low - close.shift(1))
        tr['tr'] = tr.max(axis=1)
        self.atr = tr['tr'].rolling(self.atr_periods).mean()
    
    def next(self):
        if not self.position:
            if crossover(self.sma1, self.sma2):
                # Calculate position size based on risk
                risk_amount = self.equity * self.risk_pct
                stop_distance = self.atr[-1] * 2
                size = risk_amount / stop_distance
                
                self.buy(size=size, sl=self.data.Close[-1] - stop_distance)
        
        elif crossover(self.sma2, self.sma1):
            self.position.close()

def main():
    # Download data
    data = yf.download('AAPL', '2020-01-01', '2024-12-31')
    
    # Initialize and run backtest
    bt = Backtest(data, EnhancedSMACrossover, cash=7000, commission=.002,
                  exclusive_orders=True)
    stats = bt.run()
    
    print("\nBacktest Results:")
    print(f"Total Return: {stats['Return [%]']:.2f}%")
    print(f"Sharpe Ratio: {stats['Sharpe Ratio']:.2f}")
    print(f"Max Drawdown: {stats['Max. Drawdown [%]']:.2f}%")
    print(f"Win Rate: {stats['Win Rate [%]']:.2f}%")
    
    bt.plot()

if __name__ == '__main__':
    main()