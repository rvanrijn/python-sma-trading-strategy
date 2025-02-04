from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import yfinance as yf
import pandas as pd

class SMACrossover(Strategy):
    n1 = 20  # Fast SMA
    n2 = 50  # Slow SMA
    
    def init(self):
        self.sma1 = self.I(pd.Series.rolling, self.data.Close, self.n1).mean()
        self.sma2 = self.I(pd.Series.rolling, self.data.Close, self.n2).mean()
    
    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()

def main():
    # Download data
    data = yf.download('AAPL', '2020-01-01', '2024-12-31')
    
    # Initialize and run backtest
    bt = Backtest(data, SMACrossover, cash=7000, commission=.002)
    stats = bt.run()
    
    print(stats)
    bt.plot()

if __name__ == '__main__':
    main()