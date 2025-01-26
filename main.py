import argparse
from data.data_fetcher import fetch_symbols_from_db, fetch_momentum_symbols_from_db, fetch_recent_trading_days_from_db
from strategies.momentum import filter_and_rank_stocks

# def get_us_stock_tickers():
#     """Returns a list of US stock tickers."""
#     return ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "AMD", "INTC"]



# Default parameters
# default_start_date = "2025-01-15"
# default_end_date = "2025-01-23"
result  = fetch_recent_trading_days_from_db()
# 첫 번째 날짜와 두 번째 날짜 추출
default_start_date = result[0][0].strftime('%Y-%m-%d')
default_end_date = result[0][1].strftime('%Y-%m-%d')

default_min_volume = 8000000
default_min_price = 100
default_max_price = 1000
default_min_sortino = 0.2
default_min_diff_ratio = 0.2
default_top_n = 20

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter and rank momentum stocks.")
    
    # Add arguments
    parser.add_argument("--start_date", type=str, default=default_start_date, help="Start date for analysis (YYYY-MM-DD).")
    parser.add_argument("--end_date", type=str, default=default_end_date, help="End date for analysis (YYYY-MM-DD).")
    parser.add_argument("--min_volume", type=int, default=default_min_volume, help="Minimum trading volume.")
    parser.add_argument("--min_price", type=float, default=default_min_price, help="Minimum stock price.")
    parser.add_argument("--max_price", type=float, default=default_max_price, help="Maximum stock price.")
    parser.add_argument("--min_sortino", type=float, default=default_min_sortino, help="Minimum Sortino ratio.")
    parser.add_argument("--min_diff_ratio", type=float, default=default_min_diff_ratio, help="Minimum difference ratio.")
    parser.add_argument("--top_n", type=int, default=default_top_n, help="Number of top stocks to select.")

    # Parse arguments
    args = parser.parse_args()

    # Fetch tickers based on momentum criteria
    tickers = fetch_momentum_symbols_from_db(
        args.start_date, args.end_date, args.min_volume, args.min_price, args.max_price
    )

    # Filter and rank stocks
    result = filter_and_rank_stocks(
        tickers,
        args.start_date,
        args.end_date,
        args.min_volume,
        args.min_price,
        args.max_price,
        args.min_sortino,
        args.min_diff_ratio,
        args.top_n
    )

    # Print result
    print(result)
