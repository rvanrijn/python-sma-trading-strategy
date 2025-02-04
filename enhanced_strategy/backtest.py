import yfinance as yf
from backtesting import Backtest
from sma_strategy import EnhancedSMACrossover

def run_backtest(symbol='AAPL', start='2020-01-01', end='2024-12-31', cash=7000):
    # Download data
    data = yf.download(symbol, start, end)
    
    # Run backtest
    bt = Backtest(data, EnhancedSMACrossover,
                  cash=cash,
                  commission=.002,
                  exclusive_orders=True)
    
    stats = bt.run()
    bt.plot(filename=f'enhanced_strategy_{symbol}_backtest.html', open_browser=False)
    
    # Return key metrics
    return {
        'Total Return %': stats['Return [%]'],
        'Sharpe Ratio': stats['Sharpe Ratio'],
        'Max Drawdown %': stats['Max. Drawdown [%]'],
        'Win Rate %': stats['Win Rate [%]'],
        'Number of Trades': stats['# Trades'],
        'Average Risk %': stats.get('Avg Risk %', 'N/A')
    }

def compare_strategies(symbols=['AAPL', 'MSFT', 'GOOGL']):
    from basic_strategy.backtest import run_backtest as basic_backtest
    
    results = {}
    for symbol in symbols:
        print(f'\nComparing strategies on {symbol}:')
        basic_results = basic_backtest(symbol)
        enhanced_results = run_backtest(symbol)
        
        print('\nBasic Strategy:')
        for key, value in basic_results.items():
            print(f'{key}: {value:.2f}')
            
        print('\nEnhanced Strategy:')
        for key, value in enhanced_results.items():
            if isinstance(value, (int, float)):
                print(f'{key}: {value:.2f}')
            else:
                print(f'{key}: {value}')

if __name__ == '__main__':
    compare_strategies()