from enhanced_strategy.backtest import compare_strategies

def main():
    # Define symbols to test
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
    
    # Run comparison
    compare_strategies(symbols)

if __name__ == '__main__':
    main()