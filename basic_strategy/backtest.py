import yfinance as yf
from backtesting import Backtest
from sma_strategy import SMACrossover

def run_backtest(symbol='AAPL', start='2020-01-01', end='2024-12-31', cash=7000):
    # Download data
    data = yf.download(symbol, start, end)
    
    # Run backtest
    bt = Backtest(data, SMACrossover,
                  cash=cash,
                  commission=.002)
    
    stats = bt.run()
    bt.plot(filename=f'basic_strategy_{symbol}_backtest.html', open_browser=False)
    
    # Return key metrics
    return {
        'Total Return %': stats['Return [%]'],
        'Sharpe Ratio': stats['Sharpe Ratio'],
        'Max Drawdown %': stats['Max. Drawdown [%]'],
        'Win Rate %': stats['Win Rate [%]'],
        'Number of Trades': stats['# Trades']
    }

if __name__ == '__main__':
    # Test on multiple symbols
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    
    for symbol in symbols:
        print(f'\nBacktesting {symbol}:')
        metrics = run_backtest(symbol)
        for key, value in metrics.items():
            print(f'{key}: {value:.2f}')